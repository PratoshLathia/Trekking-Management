from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    verified = db.Column(db.Boolean, default=False)

    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan')

    assigned_treks = db.relationship('Trek', back_populates='coordinator')


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100))
    difficulty = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    slots = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Open")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    bookings = db.relationship('Booking', back_populates='trek', cascade='all, delete-orphan')
    
    coordinator = db.relationship('User', back_populates='assigned_treks')


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked")

    user = db.relationship('User', back_populates='bookings')

    trek = db.relationship('Trek', back_populates='bookings')
    




if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        admin_exist = User.query.filter_by(role='admin').first()
        if not admin_exist:
            admin = User(username="admin", email="admin@gmail.com", password="admin", role="admin", verified=True)
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)