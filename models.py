from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()


# -----------------------------------------
# USER MODEL (Doctor + Patient)
# -----------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20))
    place = db.Column(db.String(100))

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # 🆕 NEW FIELD
    password = db.Column(db.String(200), nullable=False)  # hashed
    secret_key = db.Column(db.String(10), nullable=True)  # only for patients

    role = db.Column(db.String(20), nullable=False)   # "doctor" or "patient"

    # Relationships (explicit)
    patient_appointments = db.relationship(
        'Appointment',
        foreign_keys='Appointment.patient_id',
        backref='patient',
        lazy=True
    )

    doctor_appointments = db.relationship(
        'Appointment',
        foreign_keys='Appointment.doctor_id',
        backref='doctor',
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# -----------------------------------------
# APPOINTMENT MODEL
# -----------------------------------------
class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)

    # NEW FIELDS: reason / procedure / estimated time
    reason = db.Column(db.String(255))          # what patient said
    procedure = db.Column(db.String(100))       # interpreted procedure
    estimated_minutes = db.Column(db.Integer)   # copy of duration for clarity

    status = db.Column(db.String(20), default='pending')
    source = db.Column(db.String(20), default='chatbot')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment {self.id}>"


# -----------------------------------------
# EMERGENCY BOOKING MODEL
# -----------------------------------------
class Emergency(db.Model):
    __tablename__ = 'emergency_cases'

    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)

    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default='active')

    def __repr__(self):
        return f"<Emergency {self.id}>"


# -----------------------------------------
# SLOT MODEL (still there for API endpoints)
# -----------------------------------------
class Slot(db.Model):
    __tablename__ = 'slots'

    id = db.Column(db.Integer, primary_key=True)

    slot_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<Slot {self.slot_time} - {self.date}>"