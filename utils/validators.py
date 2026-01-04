# utils/validators.py

import re

# -------------------------------
# Validate Secret Key (4 digits)
# -------------------------------

def validate_secret_key(key: str) -> bool:
    """
    Secret Key must be exactly 4 digits.
    Used to confirm appointments in chatbot.
    """
    return bool(re.fullmatch(r"\d{4}", key))


# -------------------------------
# Validate Password
# -------------------------------

def validate_password(password: str) -> bool:
    """
    Password rules:
      - minimum 6 characters
      - must contain at least 1 letter and 1 number
    """
    if len(password) < 6:
        return False

    has_letter = re.search(r"[A-Za-z]", password)
    has_number = re.search(r"\d", password)

    return bool(has_letter and has_number)


# -------------------------------
# Validate Username
# -------------------------------

def validate_username(username: str) -> bool:
    """
    Username rules:
      - only letters, numbers, underscores
      - 3 to 20 characters
    """
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", username))


# -------------------------------
# Validate Name
# -------------------------------

def validate_name(name: str) -> bool:
    """
    Name rules:
      - alphabets and spaces only
      - at least 2 characters
    """
    return bool(re.fullmatch(r"[A-Za-z ]{2,50}", name))


# -------------------------------
# Validate Date (YYYY-MM-DD)
# -------------------------------

def validate_date(date_str: str) -> bool:
    """
    Simple YYYY-MM-DD validation.
    (Flask will use it for signup DOB and appointment date)
    """
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str))

# ----------------------------------------------------
# Validate if slot exists & is available
# ----------------------------------------------------
from models import Slot, Appointment

def validate_slot(doctor_id, appt_date, appt_time):
    """
    Checks:
    - Does the slot exist?
    - Is it available?
    """
    slot = Slot.query.filter_by(date=appt_date, slot_time=appt_time).first()

    if not slot:
        return False, "Selected slot does not exist."

    if not slot.is_available:
        return False, "That slot is already taken."

    return True, "Slot available."


# ----------------------------------------------------
# Validate appointment conflicts (doctor + patient)
# ----------------------------------------------------
def validate_appointment_conflict(patient_id, doctor_id, appt_date, appt_time):
    """
    Prevent:
    - patient double booking
    - doctor double booking
    """

    # Patient conflict
    patient_conflict = Appointment.query.filter_by(
        patient_id=patient_id,
        appointment_date=appt_date,
        appointment_time=appt_time
    ).first()

    if patient_conflict:
        return False, "You already have an appointment at this time."

    # Doctor conflict
    doctor_conflict = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appt_date,
        appointment_time=appt_time
    ).first()

    if doctor_conflict:
        return False, "Doctor already has an appointment in this slot."

    return True, "No conflicts."
