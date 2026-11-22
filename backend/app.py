from functools import wraps
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify, send_file
from flask_caching import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    create_access_token,
    JWTManager,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY") or secrets.token_hex(32)
jwt = JWTManager(app)

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = os.environ.get("REDIS_HOST", "localhost")
app.config["CACHE_REDIS_PORT"] = int(os.environ.get("REDIS_PORT", 6379))
app.config["CACHE_REDIS_DB"] = 0
app.config["CACHE_DEFAULT_TIMEOUT"] = 60
cache = Cache(app)





class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Active")

    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    assigned_treks = db.relationship("Trek", back_populates="staff")
    staff_profile = db.relationship("StaffProfile", back_populates="user", uselist=False)
    user_profile = db.relationship("UserProfile", back_populates="user", uselist=False)


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    duration = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    slots = db.Column(db.Integer, default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="Active")
    stage = db.Column(db.String(50), default="Upcoming")

    bookings = db.relationship("Booking", back_populates="trek", cascade="all, delete-orphan")
    change_requests = db.relationship("TrekChangeRequest", back_populates="trek", cascade="all, delete-orphan")
    staff = db.relationship("User", back_populates="assigned_treks")


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked")
    payment_status = db.Column(db.String(20), default="Not Required")
    reminder_sent = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")


class TrekChangeRequest(db.Model):
    __tablename__ = "trek_change_requests"

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    field = db.Column(db.String(30), nullable=False)
    old_value = db.Column(db.String(100))
    new_value = db.Column(db.String(100))
    request_status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trek = db.relationship("Trek", back_populates="change_requests")
    staff = db.relationship("User")


class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    contact_number = db.Column(db.String(15))
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    medical_certification = db.Column(db.String(100))
    experience = db.Column(db.String(200))

    user = db.relationship("User", back_populates="staff_profile", uselist=False)


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    contact_number = db.Column(db.String(15))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    medical_conditions = db.Column(db.String(200))
    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_number = db.Column(db.String(20))

    user = db.relationship("User", back_populates="user_profile", uselist=False)


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in allowed_roles:
                return jsonify({"info": "You are not authorized to perform this action"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def current_user_id():
    return int(get_jwt_identity())

def require_active_account():
    user = User.query.get(current_user_id())
    if not user or user.status != "Active":
        return jsonify({"info": "Your account is not active. Contact admin."}), 403
    return None

def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError("Dates must be in YYYY-MM-DD format")

DIFFICULTIES = ("Easy", "Moderate", "Difficult")
TREK_STATUSES = ("Active", "Closed")
TREK_STAGES = ("Upcoming", "Started", "Ongoing", "Completed")
ACCOUNT_STATUSES = ("Active", "Blacklisted", "Inactive")

def today():
    return datetime.now().date()

def has_scheduling_conflict(staff_id, start_date, end_date, exclude_trek_id=None):
    query = Trek.query.filter(
        Trek.staff_id == staff_id,
        Trek.start_date <= end_date,
        Trek.end_date >= start_date
    )
    if exclude_trek_id is not None:
        query = query.filter(Trek.id != exclude_trek_id)
    return query.first() is not None


CACHED_LISTING_KEYS = [
    "cache_trek_all",
    "cache_staff_all",
    "cache_user_all",
    "cache_booking_all",
    "cache_stats",
]

def invalidate_listing_caches():
    for key in CACHED_LISTING_KEYS:
        cache.delete(key)


def add_change_request(trek_id, staff_id, field, old_value, new_value):
    change_request = TrekChangeRequest(
        trek_id=trek_id,
        staff_id=staff_id,
        field=field,
        old_value=None if old_value is None else str(old_value),
        new_value=None if new_value is None else str(new_value),
        request_status="Pending"
    )
    db.session.add(change_request)
    db.session.commit()
    return change_request

def find_change_request(request_id):
    return TrekChangeRequest.query.get(request_id)

def apply_trek_change(change_request):
    trek = change_request.trek
    if not trek:
        return

    field = change_request.field
    new_value = change_request.new_value

    if field == "status":
        if new_value == "Active" and trek.stage != "Upcoming":
            return
        trek.status = new_value

    elif field == "slots":
        trek.slots = int(new_value)

    elif field == "difficulty":
        trek.difficulty = new_value

    elif field == "stage":
        trek.stage = new_value
        if new_value != "Upcoming":
            trek.status = "Closed"
        if new_value == "Completed":
            for booking in trek.bookings:
                if booking.status == "Booked":
                    booking.status = "Completed"





@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"info": "Username, email, and password are all required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"info": "Email already exists!"}), 400

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = User(username=username, email=email, password=hashed_password, role="user")
    db.session.add(new_user)
    db.session.commit()
    invalidate_listing_caches()

    return jsonify({"info": "User registration successful!"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"info": "Invalid credentials!"}), 401

    if user.status != "Active":
        return jsonify({"info": "Your account is not active. Contact admin."}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    return jsonify({
        "info": "Login successful!",
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }
    }), 200





@app.route("/trek/all", methods=["GET"])
@cache.cached(timeout=60, key_prefix="cache_trek_all")
def all_treks():

    treks = Trek.query.all()
    if treks:
        return jsonify({"treks": [{
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "duration": trek.duration,
            "difficulty": trek.difficulty,
            "slots": trek.slots,
            "staff_id": trek.staff_id,                                    
            "staff_name": trek.staff.username if trek.staff else None,
            "start_date": trek.start_date.isoformat() if trek.start_date else None,
            "end_date": trek.end_date.isoformat() if trek.end_date else None,
            "status": trek.status,
            "stage": trek.stage
        } for trek in treks]}), 200
    else:
        return jsonify({"info": "No treks found"}), 404


@app.route("/trek/add", methods=["POST"])
@role_required("admin")
def add_trek():
    data = request.get_json() or {}

    name = data.get("name")
    location = data.get("location")
    difficulty = data.get("difficulty")
    slots = data.get("slots")
    start_date_raw = data.get("start_date")
    end_date_raw = data.get("end_date")

    if not name or not location:
        return jsonify({"info": "Name and location are required"}), 400

    if not difficulty:
        return jsonify({"info": "Difficulty is required"}), 400

    if difficulty not in DIFFICULTIES:
        return jsonify({"info": "Invalid difficulty"}), 400

    if slots is None:
        return jsonify({"info": "Slots are required"}), 400

    if not isinstance(slots, int) or slots < 1:
        return jsonify({"info": "Trek must have at least 1 slot"}), 400

    if not start_date_raw or not end_date_raw:
        return jsonify({"info": "Start date and end date are required"}), 400

    try:
        start_date = parse_date(start_date_raw)
        end_date = parse_date(end_date_raw)
    except ValueError as e:
        return jsonify({"info": str(e)}), 400

    if start_date <= today():
        return jsonify({"info": "Start date must be after today"}), 400

    if end_date < start_date:
        return jsonify({"info": "End date cannot be before start date"}), 400

    staff = User.query.filter_by(id=data.get("staff_id"), role="staff", status="Active").first()
    if not staff:
        return jsonify({"info": "Staff not found"}), 404

    existing_trek = Trek.query.filter_by(name=name, location=location, start_date=start_date).first()
    if existing_trek:
        return jsonify({"info": "This trek already exists"}), 400

    if has_scheduling_conflict(staff.id, start_date, end_date):
        return jsonify({"info": "Staff member already has a trek during this date range"}), 400

    new_trek = Trek(
        name=name,
        location=location,
        duration=data.get("duration"),
        difficulty=difficulty,
        slots=slots,
        start_date=start_date,
        end_date=end_date,
        staff_id=staff.id,
        status="Active",
        stage="Upcoming"
    )
    db.session.add(new_trek)
    db.session.commit()
    invalidate_listing_caches()

    return jsonify({"info": "Trek added successfully"}), 201


@app.route("/trek/<int:trek_id>/update", methods=["POST"])
@role_required("admin")
def update_trek(trek_id):
    data = request.get_json() or {}

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"info": "Trek not found"}), 404

    if "difficulty" in data and not data.get("difficulty"):
        return jsonify({"info": "Difficulty is required"}), 400

    if data.get("difficulty") is not None and data["difficulty"] not in DIFFICULTIES:
        return jsonify({"info": "Invalid difficulty"}), 400

    new_slots = trek.slots
    if data.get("slots") is not None:
        new_slots = data["slots"]
        if not isinstance(new_slots, int) or new_slots < 1:
            return jsonify({"info": "Trek must have at least 1 slot"}), 400

    new_start = trek.start_date
    new_end = trek.end_date
    try:
        if data.get("start_date") is not None:
            new_start = parse_date(data["start_date"])
        if data.get("end_date") is not None:
            new_end = parse_date(data["end_date"])
    except ValueError as e:
        return jsonify({"info": str(e)}), 400

    if new_start != trek.start_date and new_start and new_start <= today():
        return jsonify({"info": "Start date must be after today"}), 400

    if new_start and new_end and new_end < new_start:
        return jsonify({"info": "End date cannot be before start date"}), 400

    if trek.staff_id and new_start and new_end and (new_start != trek.start_date or new_end != trek.end_date):
        if has_scheduling_conflict(trek.staff_id, new_start, new_end, exclude_trek_id=trek.id):
            return jsonify({"info": "Staff member already has a trek during this date range"}), 400

    if data.get("name") is not None:
        trek.name = data["name"]
    if data.get("location") is not None:
        trek.location = data["location"]
    if data.get("duration") is not None:
        trek.duration = data["duration"]
    if data.get("difficulty") is not None:
        trek.difficulty = data["difficulty"]
    trek.slots = new_slots
    trek.start_date = new_start
    trek.end_date = new_end

    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"info": "Trek updated successfully"}), 200


@app.route("/trek/<int:trek_id>/assign_staff", methods=["POST"])
@role_required("admin")
def assign_staff(trek_id):
    data = request.get_json() or {}

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"assign_info": "Trek not found"}), 404

    staff = User.query.filter_by(id=data.get("staff_id"), role="staff", status="Active").first()
    if not staff:
        return jsonify({"assign_info": "Staff not found"}), 404

    if trek.start_date and trek.end_date and has_scheduling_conflict(staff.id, trek.start_date, trek.end_date, exclude_trek_id=trek.id):
        return jsonify({"assign_info": "Staff member already has a trek during this date range"}), 400

    trek.staff_id = staff.id
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"assign_info": "Staff assigned successfully"}), 200


@app.route("/trek/<int:trek_id>", methods=["DELETE"])
@role_required("admin")
def delete_trek(trek_id):
    
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"delete_info": "Trek not found"}), 404

    db.session.delete(trek)
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"delete_info": "Trek deleted successfully"}), 200


@app.route("/trek/<int:trek_id>/slots", methods=["POST"])
@role_required("admin", "staff")
def update_trek_slots(trek_id):
    inactive = require_active_account()
    if inactive:
        return inactive

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"slots_info": "Trek not found"}), 404

    if trek.staff_id != current_user_id() and get_jwt().get("role") != "admin":
        return jsonify({"slots_info": "Not authorized for this trek"}), 403

    data = request.get_json() or {}
    new_slots = data.get("slots")
    if new_slots is None:
        return jsonify({"slots_info": "Missing 'slots' field"}), 400

    if not isinstance(new_slots, int) or new_slots < 1:
        return jsonify({"slots_info": "Trek must have at least 1 slot"}), 400

    if get_jwt().get("role") == "staff":
        add_change_request(trek.id, current_user_id(), "slots", str(trek.slots), str(new_slots))
        return jsonify({"slots_info": "Slots change submitted for admin approval"})

    trek.slots = new_slots
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"slots_info": "Slots updated successfully"})


@app.route("/trek/<int:trek_id>/status", methods=["POST"])
@role_required("admin", "staff")
def update_trek_status(trek_id):
    inactive = require_active_account()
    if inactive:
        return inactive

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"status_info": "Trek not found"}), 404

    if trek.staff_id != current_user_id() and get_jwt().get("role") != "admin":
        return jsonify({"status_info": "Not authorized for this trek"}), 403

    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"status_info": "Missing 'status' field"}), 400

    if new_status not in TREK_STATUSES:
        return jsonify({"status_info": "Invalid status"}), 400

    if new_status == "Active" and trek.stage != "Upcoming":
        return jsonify({"status_info": "Trek cannot be reopened once it is Ongoing or Completed"}), 400

    if get_jwt().get("role") == "staff":
        add_change_request(trek.id, current_user_id(), "status", trek.status, new_status)
        return jsonify({"status_info": "Status change submitted for admin approval"})

    trek.status = new_status
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"status_info": "Trek status updated successfully"})


@app.route("/trek/<int:trek_id>/stage", methods=["POST"])
@role_required("admin", "staff")
def update_trek_stage(trek_id):
    inactive = require_active_account()
    if inactive:
        return inactive

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"stage_info": "Trek not found"}), 404

    if trek.staff_id != current_user_id() and get_jwt().get("role") != "admin":
        return jsonify({"stage_info": "Not authorized for this trek"}), 403

    data = request.get_json() or {}
    new_stage = data.get("stage")
    if not new_stage:
        return jsonify({"stage_info": "Missing 'stage' field"}), 400

    if new_stage not in TREK_STAGES:
        return jsonify({"stage_info": "Invalid stage"}), 400

    if get_jwt().get("role") == "staff":
        add_change_request(trek.id, current_user_id(), "stage", trek.stage, new_stage)
        return jsonify({"stage_info": "Stage change submitted for admin approval"})

    trek.stage = new_stage

    if new_stage != "Upcoming":
        trek.status = "Closed"

    if new_stage == "Completed":
        for booking in trek.bookings:
            if booking.status == "Booked":
                booking.status = "Completed"

    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"stage_info": "Trek stage updated successfully"})


@app.route("/trek/<int:trek_id>/difficulty", methods=["POST"])
@role_required("admin", "staff")
def update_trek_difficulty(trek_id):
    inactive = require_active_account()
    if inactive:
        return inactive

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"difficulty_info": "Trek not found"}), 404

    if trek.staff_id != current_user_id() and get_jwt().get("role") != "admin":
        return jsonify({"difficulty_info": "Not authorized for this trek"}), 403

    data = request.get_json() or {}
    new_difficulty = data.get("difficulty")
    if not new_difficulty:
        return jsonify({"difficulty_info": "Missing 'difficulty' field"}), 400

    if new_difficulty not in DIFFICULTIES:
        return jsonify({"difficulty_info": "Invalid difficulty"}), 400

    if get_jwt().get("role") == "staff":
        add_change_request(trek.id, current_user_id(), "difficulty", trek.difficulty, new_difficulty)
        return jsonify({"difficulty_info": "Difficulty change submitted for admin approval"})

    trek.difficulty = new_difficulty
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"difficulty_info": "Trek difficulty updated successfully"})


@app.route("/trek/change_requests", methods=["GET"])
@role_required("admin")
def list_trek_change_requests():

    pending = TrekChangeRequest.query.filter_by(request_status="Pending").order_by(TrekChangeRequest.id).all()
    result = [{
        "id": r.id,
        "trek_id": r.trek_id,
        "trek_name": r.trek.name if r.trek else None,
        "staff_id": r.staff_id,
        "staff_name": r.staff.username if r.staff else None,
        "field": r.field,
        "old_value": r.old_value,
        "new_value": r.new_value,
        "created_at": r.created_at.isoformat()
    } for r in pending]

    return jsonify({"requests": result}), 200


@app.route("/trek/change_requests/<int:request_id>/approve", methods=["POST"])
@role_required("admin")
def approve_trek_change_request(request_id):

    change_request = find_change_request(request_id)
    if not change_request:
        return jsonify({"info": "Request not found"}), 404

    if change_request.request_status != "Pending":
        return jsonify({"info": "This request has already been reviewed"}), 400

    apply_trek_change(change_request)
    change_request.request_status = "Approved"
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"info": "Change approved and applied"}), 200


@app.route("/trek/change_requests/<int:request_id>/reject", methods=["POST"])
@role_required("admin")
def reject_trek_change_request(request_id):

    change_request = find_change_request(request_id)
    if not change_request:
        return jsonify({"info": "Request not found"}), 404

    if change_request.request_status != "Pending":
        return jsonify({"info": "This request has already been reviewed"}), 400

    change_request.request_status = "Rejected"
    db.session.commit()
    return jsonify({"info": "Change rejected"}), 200


@app.route("/trek/<int:trek_id>/book", methods=["POST"])
@role_required("user")
def book_trek(trek_id):
    user_id = current_user_id()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"booking_info": "User not found"}), 404

    if user.status != "Active":
        return jsonify({"booking_info": "Your account is not active. Contact admin."}), 403

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"booking_info": "Trek not found"}), 404

    if trek.status != "Active" or trek.stage != "Upcoming":
        return jsonify({"booking_info": "Trek is not open for booking"}), 400

    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status="Booked").first()
    if existing:
        return jsonify({"booking_info": "You have already booked this trek"}), 400

    claimed = Trek.query.filter(Trek.id == trek_id, Trek.slots > 0).update(
        {Trek.slots: Trek.slots - 1}, synchronize_session=False
    )
    if not claimed:
        db.session.rollback()
        return jsonify({"booking_info": "No slots available"}), 400

    db.session.add(Booking(user_id=user_id, trek_id=trek_id))
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"booking_info": "Trek booked successfully"}), 201


@app.route("/trek/<int:trek_id>/bookings", methods=["GET"])
@role_required("staff", "admin")
def trek_bookings(trek_id):

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"booking_info": "Trek not found"}), 404

    if trek.staff_id != current_user_id() and get_jwt().get("role") != "admin":
        return jsonify({"booking_info": "Not authorized for this trek"}), 403

    return jsonify({
        "trek_name": trek.name,
        "bookings": [{
            "booking_id": booking.id,
            "user_id": booking.user.id,
            "username": booking.user.username,
            "email": booking.user.email,
            "booking_date": booking.booking_date.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p"),
            "status": booking.status,
            "payment_status": booking.payment_status
        } for booking in trek.bookings if booking.status == "Booked"]
    })





@app.route("/booking/all", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60, key_prefix="cache_booking_all")
def all_bookings():

    bookings = Booking.query.all()

    return jsonify({"all_bookings": [{
        "id": booking.id,
        "username": booking.user.username,
        "email": booking.user.email,
        "trek_name": booking.trek.name,
        "booking_date": booking.booking_date.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p"),
        "trek_status": booking.trek.status,
        "trek_stage": booking.trek.stage,
        "trek_start_date": booking.trek.start_date.isoformat() if booking.trek.start_date else None,
        "trek_end_date": booking.trek.end_date.isoformat() if booking.trek.end_date else None,
        "booking_status": booking.status,
        "payment_status": booking.payment_status
    } for booking in bookings]})


@app.route("/booking/<int:booking_id>/cancel", methods=["POST"])
@role_required("user")
def cancel_booking(booking_id):
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"booking_info": "Booking not found"}), 404

    if booking.user_id != current_user_id():
        return jsonify({"booking_info": "Not authorized to cancel this booking"}), 403

    if booking.status != "Booked":
        return jsonify({"booking_info": "This booking can no longer be cancelled"}), 400

    booking.trek.slots += 1
    booking.status = "Cancelled"
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"booking_info": "Booking cancelled successfully"}), 200


@app.route("/booking/<int:booking_id>/remove", methods=["POST"])
@role_required("staff", "admin")
def remove_booking(booking_id):
    inactive = require_active_account()
    if inactive:
        return inactive

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"booking_info": "Booking not found"}), 404

    if booking.trek.staff_id != current_user_id() and get_jwt().get("role") != "admin":
        return jsonify({"booking_info": "Not authorized for this trek"}), 403

    if booking.status != "Booked":
        return jsonify({"booking_info": "This booking has already been removed"}), 400

    booking.trek.slots += 1
    booking.status = "Cancelled"
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"booking_info": "Participant removed successfully"})





@app.route("/staff/add", methods=["POST"])
@role_required("admin")
def add_staff():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"info": "Username, email, and password are all required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"info": "Email already exists"}), 400

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    new_staff = User(username=username, email=email, password=hashed_password, role="staff")
    db.session.add(new_staff)
    db.session.commit()
    invalidate_listing_caches()

    return jsonify({"info": "Staff added successfully"}), 201


@app.route("/staff/all", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60, key_prefix="cache_staff_all")
def all_staff():

    staff = User.query.filter_by(role="staff").all()

    if staff:
        return jsonify({"staff": [{
            "id": s.id, "username": s.username, "email": s.email, "status": s.status
        } for s in staff]}), 200
    else:
        return jsonify({"info": "No staff found"}), 404


@app.route("/staff/<int:staff_id>/status", methods=["POST"])
@role_required("admin")
def update_staff_status(staff_id):

    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"status_info": "Staff not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"status_info": "Missing 'status' field"}), 400

    if new_status not in ACCOUNT_STATUSES:
        return jsonify({"status_info": "Invalid status"}), 400

    staff.status = new_status
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"status_info": "Status updated successfully"}), 200


@app.route("/staff/profile", methods=["POST"])
@role_required("staff")
def save_staff_profile():
    data = request.get_json()
    staff_id = current_user_id()

    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"info": "Staff not found"}), 404

    if staff.staff_profile:
        profile = staff.staff_profile
    else:
        profile = StaffProfile(user_id=staff_id)
        db.session.add(profile)

    profile.contact_number = data.get("contact_number")
    profile.gender = data.get("gender")
    profile.address = data.get("address")
    profile.medical_certification = data.get("medical_certification")
    profile.experience = data.get("experience")

    db.session.commit()
    return jsonify({"info": "Profile saved successfully"}), 200


@app.route("/staff/<int:staff_id>/profile", methods=["GET"])
@role_required("staff")
def get_staff_profile(staff_id):
    if staff_id != current_user_id():
        return jsonify({"info": "Not authorized"}), 403

    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"info": "Staff not found"}), 404

    if not staff.staff_profile:
        return jsonify({"profile": None}), 200

    profile = staff.staff_profile
    return jsonify({"profile": {
        "contact_number": profile.contact_number,
        "gender": profile.gender,
        "address": profile.address,
        "medical_certification": profile.medical_certification,
        "experience": profile.experience
    }}), 200


@app.route("/staff/<int:staff_id>/treks", methods=["GET"])
@role_required("staff")
def staff_treks(staff_id):
    if staff_id != current_user_id():
        return jsonify({"info": "Not authorized"}), 403

    treks = Trek.query.filter_by(staff_id=staff_id).all()

    return jsonify({"treks": [{
        "id": trek.id,
        "name": trek.name,
        "location": trek.location,
        "slots": trek.slots,
        "duration": trek.duration,
        "difficulty": trek.difficulty,
        "status": trek.status,
        "stage": trek.stage,
        "trekkers_count": len(trek.bookings)
    } for trek in treks]}), 200






@app.route("/user/all", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60, key_prefix="cache_user_all")
def all_users():

    users = User.query.filter_by(role="user").all()
    if users:
        return jsonify({"users": [{
            "id": u.id, "username": u.username, "email": u.email, "status": u.status
        } for u in users]}), 200
    else:
        return jsonify({"info": "No users found"}), 404


@app.route("/user/<int:user_id>/status", methods=["POST"])
@role_required("admin")
def update_user_status(user_id):

    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        return jsonify({"status_info": "User not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"status_info": "Missing 'status' field"}), 400

    if new_status not in ACCOUNT_STATUSES:
        return jsonify({"status_info": "Invalid status"}), 400

    user.status = new_status
    db.session.commit()
    invalidate_listing_caches()
    return jsonify({"status_info": "Status updated successfully"}), 200


@app.route("/user/profile", methods=["POST"])
@role_required("user")
def save_user_profile():
    data = request.get_json()

    user_id = current_user_id()

    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        return jsonify({"info": "User not found"}), 404

    if user.user_profile:
        profile = user.user_profile
    else:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    profile.contact_number = data.get("contact_number")
    profile.age = data.get("age")
    profile.gender = data.get("gender")
    profile.address = data.get("address")
    profile.medical_conditions = data.get("medical_conditions")
    profile.emergency_contact_name = data.get("emergency_contact_name")
    profile.emergency_contact_number = data.get("emergency_contact_number")

    db.session.commit()
    return jsonify({"info": "Profile saved successfully"}), 200


@app.route("/user/<int:user_id>/profile", methods=["GET"])
@role_required("user")
def get_user_profile(user_id):
    if user_id != current_user_id():
        return jsonify({"info": "Not authorized"}), 403

    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        return jsonify({"info": "User not found"}), 404

    if not user.user_profile:
        return jsonify({"profile": None}), 200

    profile = user.user_profile
    return jsonify({"profile": {
        "contact_number": profile.contact_number,
        "age": profile.age,
        "gender": profile.gender,
        "address": profile.address,
        "medical_conditions": profile.medical_conditions,
        "emergency_contact_name": profile.emergency_contact_name,
        "emergency_contact_number": profile.emergency_contact_number
    }}), 200


@app.route("/user/<int:user_id>/bookings", methods=["GET"])
@role_required("user")
def user_bookings(user_id):
    if user_id != current_user_id():
        return jsonify({"info": "Not authorized"}), 403

    bookings = Booking.query.filter_by(user_id=user_id).all()

    return jsonify({"bookings": [{
        "booking_id": b.id,
        "trek_id": b.trek_id,
        "trek_name": b.trek.name,
        "booking_date": b.booking_date.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p"),
        "status": b.status,
        "payment_status": b.payment_status
    } for b in bookings]}), 200





@app.route("/stats", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60, key_prefix="cache_stats")
def stats():
    return jsonify({"stats": {
        "total_users": User.query.filter_by(role="user").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_treks": Trek.query.count(),
        "total_bookings": Booking.query.count(),
        "active_treks": Trek.query.filter_by(status="Active").count(),
        "closed_treks": Trek.query.filter_by(status="Closed").count(),
        "completed_treks": Trek.query.filter_by(stage="Completed").count()
    }})





@app.route("/admin/reminders/run", methods=["POST"])
@role_required("admin")
def run_reminders_now():
    from tasks import send_trek_reminders
    send_trek_reminders.delay()
    return jsonify({"info": "Reminder job queued"}), 202


@app.route("/admin/reports/generate", methods=["POST"])
@role_required("admin")
def run_report_now():
    from tasks import generate_monthly_report
    generate_monthly_report.delay()
    return jsonify({"info": "Report job queued"}), 202


@app.route("/admin/reports", methods=["GET"])
@role_required("admin")
def list_reports():

    if not os.path.isdir("reports"):
        return jsonify({"reports": []}), 200

    files = sorted(os.listdir("reports"), reverse=True)
    return jsonify({"reports": files}), 200


@app.route("/admin/reports/<path:filename>", methods=["GET"])
@role_required("admin")
def view_report(filename):
    safe_name = os.path.basename(filename)
    filepath = os.path.join("reports", safe_name)

    if not os.path.isfile(filepath):
        return jsonify({"info": "Report not found"}), 404

    return send_file(filepath)


@app.route("/booking/export", methods=["POST"])
@role_required("user")
def start_export():
    from tasks import export_bookings_csv
    task = export_bookings_csv.delay(current_user_id())
    return jsonify({"task_id": task.id}), 202


@app.route("/booking/export/<task_id>/status", methods=["GET"])
@role_required("user")
def export_status(task_id):
    from tasks import export_bookings_csv
    result = export_bookings_csv.AsyncResult(task_id)
    return jsonify({"state": result.state, "ready": result.ready()}), 200


@app.route("/booking/export/<task_id>/download", methods=["GET"])
@role_required("user")
def download_export(task_id):
    from tasks import export_bookings_csv
    result = export_bookings_csv.AsyncResult(task_id)

    if not result.ready():
        return jsonify({"info": "Export not ready yet"}), 400
    if result.failed():
        return jsonify({"info": "Export failed"}), 500

    filename = result.result

    expected_prefix = f"exports/bookings_user{current_user_id()}_"
    if not filename.startswith(expected_prefix):
        return jsonify({"info": "Not authorized for this export"}), 403

    return send_file(filename, as_attachment=True)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        admin_exists = User.query.filter_by(role="admin").first()
        if not admin_exists:
            admin_email = os.environ.get("ADMIN_EMAIL", "admin@gmail.com")
            admin_password = os.environ.get("ADMIN_PASSWORD")
            if not admin_password:
                admin_password = secrets.token_urlsafe(12)
                print(f"Generated admin password for {admin_email}: {admin_password}")
            admin = User(
                username="admin",
                email=admin_email,
                password=generate_password_hash(admin_password, method="pbkdf2:sha256"),
                role="admin",
                status="Active"
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")