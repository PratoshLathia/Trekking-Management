import csv
import io
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from celery import Celery
from celery.schedules import crontab
from flask_mail import Mail, Message
from sqlalchemy import func

from app import app, db, Trek, Booking


celery_app = Celery(
    "trekking_tasks",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
)

celery_app.conf.beat_schedule = {
    "send-daily-trek-reminders": {
        "task": "tasks.send_trek_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "generate-monthly-report": {
        "task": "tasks.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),
    },
}
celery_app.conf.timezone = "Asia/Kolkata"
celery_app.conf.enable_utc = True

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER") or os.environ.get("MAIL_USERNAME")

mail = Mail(app)


def now_ist():
    return datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Kolkata"))

def to_ist(naive_utc_dt):
    if naive_utc_dt is None:
        return None
    return naive_utc_dt.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p")

def send_email(to, subject, body=None, html=None):
    msg = Message(subject=subject, recipients=[to], body=body, html=html)
    mail.send(msg)





@celery_app.task
def send_trek_reminders():
    with app.app_context():
        today = now_ist().date()
        reminder_window = today + timedelta(days=3)

        upcoming_treks = Trek.query.filter(
            Trek.start_date.isnot(None),
            Trek.start_date >= today,
            Trek.start_date <= reminder_window,
        ).all()

        reminders_sent = 0
        for trek in upcoming_treks:
            for booking in trek.bookings:
                if booking.status == "Booked" and not booking.reminder_sent:
                    send_email(
                        to=booking.user.email,
                        subject=f"Reminder: {trek.name} starts soon!",
                        body=(
                            f"Hi {booking.user.username},\n\n"
                            f"This is a reminder that your trek \"{trek.name}\" in "
                            f"{trek.location} starts on {trek.start_date}.\n\n"
                            f"See you on the trail!\nTrekMate"
                        ),
                    )
                    booking.reminder_sent = True
                    reminders_sent += 1

        db.session.commit()
        print(f"[reminders] sent {reminders_sent} reminder(s)")
        return reminders_sent


@celery_app.task
def generate_monthly_report():
    with app.app_context():
        from app import User

        today = now_ist().date()
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        first_of_last_month = last_month_end.replace(day=1)
        month_label = first_of_last_month.strftime("%B %Y")

        conducted = Trek.query.filter(
            Trek.stage == "Completed",
            Trek.end_date >= first_of_last_month,
            Trek.end_date <= last_month_end,
        ).all()

        participants = (
            Booking.query
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(
                Booking.status.in_(["Completed", "Booked"]),
                Trek.stage == "Completed",
                Trek.end_date >= first_of_last_month,
                Trek.end_date <= last_month_end,
            )
            .count()
        )

        popular = (
            db.session.query(
                Trek.name,
                func.count(Booking.id).label("count"),
            )
            .join(Booking, Booking.trek_id == Trek.id)
            .filter(
                Trek.stage == "Completed",
                Trek.end_date >= first_of_last_month,
                Trek.end_date <= last_month_end,
                Booking.status.in_(["Completed", "Booked"]),
            )
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
            .all()
        )

        if popular:
            popular_html = "".join(
                f"<li>{name} — {count} participant(s)</li>"
                for name, count in popular
            )
        else:
            popular_html = "<li>No treks completed last month</li>"

        conducted_names = ", ".join(t.name for t in conducted) if conducted else "None"

        html_body = f"""
        <h2>Monthly Trekking Activity Report — {month_label}</h2>
        <p>Summary for <strong>{month_label}</strong>:</p>
        <ul>
            <li><strong>Treks conducted:</strong> {len(conducted)}</li>
            <li><strong>Total participants:</strong> {participants}</li>
            <li><strong>Treks:</strong> {conducted_names}</li>
        </ul>
        <h3>Popular treks</h3>
        <ul>{popular_html}</ul>
        <p>— Trekking Admin System</p>
        """

        report_html = f"""<!DOCTYPE html>
<html>
<head><title>Trekking Activity Report - {month_label}</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
{html_body}
</body>
</html>"""
        os.makedirs("reports", exist_ok=True)
        report_filename = f"reports/report_{first_of_last_month.strftime('%Y_%m')}.html"
        with open(report_filename, "w") as f:
            f.write(report_html)

        admins = User.query.filter_by(role="admin").all()
        if not admins:
            print(f"[report] saved {report_filename}, but no admin users found to email")
            return f"Saved {report_filename}, no admin users found"

        sent = 0
        for admin in admins:
            send_email(
                to=admin.email,
                subject=f"Monthly Trekking Report — {month_label}",
                html=html_body,
            )
            sent += 1

        print(f"[report] saved {report_filename} and emailed {sent} admin(s) for {month_label}")
        return f"Saved {report_filename}, emailed {sent} admin(s) for {month_label}"


@celery_app.task
def export_bookings_csv(user_id):
    with app.app_context():
        bookings = (
            Booking.query
            .filter_by(user_id=user_id)
            .order_by(Booking.booking_date.desc())
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Booking ID", "Trek Name", "Location", "Difficulty", "Duration",
            "Booked At", "Booking Status", "Trek Booking Status", "Trek State",
            "Coordinator",
        ])
        for b in bookings:
            t = b.trek
            writer.writerow([
                b.id,
                t.name,
                t.location,
                t.difficulty,
                t.duration,
                to_ist(b.booking_date),
                b.status,
                t.status,
                t.stage,
                t.staff.username,
            ])

        os.makedirs("exports", exist_ok=True)
        timestamp = now_ist().strftime("%Y%m%d%H%M%S")
        filename = f"exports/bookings_user{user_id}_{timestamp}.csv"
        with open(filename, "w", newline="") as f:
            f.write(output.getvalue())

        print(f"[export] generated {filename} for user {user_id}")
        return filename