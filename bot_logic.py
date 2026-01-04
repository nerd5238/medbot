from datetime import datetime
import json
import random

from utils.slot_manager import SlotManager
from utils.validators import (
    validate_secret_key,
    validate_date,
    validate_appointment_conflict
)
from utils.mailer import send_email
from models import db, Appointment, User

slot_manager = SlotManager()

# -------------------------------
# Load JSON responses
# -------------------------------
with open("clinic_responses.json", "r", encoding="utf-8") as f:
    RESP = json.load(f)

# -------------------------------
# Clinic Info (SAFE BACKEND DATA)
# -------------------------------
CLINIC_INFO = {
    "name": "MedBot Dental Clinic",
    "services": [
        "General checkups",
        "Dental cleaning & scaling",
        "Fillings",
        "Extractions",
        "Root canal treatment",
        "Minor dental procedures"
    ],
    "timings": "Monday to Saturday, 9:00 AM – 7:00 PM",
    "doctor": "Dr. MedBot (Dental Surgeon)"
}

# -------------------------------
# Treatment Mapping
# -------------------------------
TREATMENTS = [
    (["checkup", "consult", "tooth pain", "toothache", "sensitivity"], "General Checkup", 15),
    (["cleaning", "scaling", "polish"], "Cleaning / Scaling", 30),
    (["filling", "cavity"], "Filling", 30),
    (["extraction", "remove tooth"], "Extraction", 45),
    (["root canal", "rct"], "Root Canal Treatment", 60),
    (["emergency", "bleeding", "swelling"], "Emergency Visit", 30)
]

# -------------------------------
# Helpers
# -------------------------------
def map_reason_to_procedure(text):
    text = text.lower()
    for keys, proc, mins in TREATMENTS:
        if any(k in text for k in keys):
            return proc, mins
    return None, None


def normalize_time(text):
    for fmt in ("%H:%M", "%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(text.upper(), fmt).strftime("%H:%M")
        except:
            continue
    return None


def pick(key, **kwargs):
    msg = random.choice(RESP.get(key, RESP["fallback"]))
    for k, v in kwargs.items():
        msg = msg.replace(f"{{{{{k}}}}}", str(v))
    return msg


def clear_booking(session):
    for k in [
        "booking_state",
        "procedure",
        "duration_minutes",
        "appointment_date",
        "appointment_time",
        "secret_attempts"
    ]:
        session.pop(k, None)


# -------------------------------
# MAIN BOT LOGIC
# -------------------------------
def medbot_reply(intent_payload, session):
    intent = intent_payload.get("intent") or "general"
    message = intent_payload.get("message", "").strip()
    msg = message.lower()

    if "user_id" not in session:
        return {"reply": pick("login_required")}

    user = User.query.get(session["user_id"])
    state = session.get("booking_state")

    # ---------------- Greeting ----------------
    if intent == "greeting":
        return {"reply": pick("greeting", name=user.name)}

    # ---------------- Help ----------------
    if intent == "help":
        return {"reply": pick("help")}

    # ---------------- General / Casual ----------------
    if intent == "general" and not state:
        return {"reply": pick("general")}

    # ---------------- Clinic Info ----------------
    if intent == "clinic_info":
        services = "\n".join(f"• {s}" for s in CLINIC_INFO["services"])
        return {
            "reply": pick(
                "clinic_info",
                services=services,
                timings=CLINIC_INFO["timings"],
                doctor=CLINIC_INFO["doctor"]
            )
        }

    # ---------------- Appointment Status ----------------
    if intent == "status":
        appt = Appointment.query.filter_by(patient_id=user.id).order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).first()

        if not appt:
            return {"reply": pick("status_none")}

        return {
            "reply": pick(
                "status_found",
                date=appt.appointment_date,
                time=appt.appointment_time,
                procedure=appt.procedure,
                status=appt.status.capitalize()
            )
        }

    # ---------------- Start Booking ----------------
    if intent == "book" and not state:
        session["booking_state"] = "await_reason"
        return {"reply": pick("ask_reason")}

    # ---------------- Booking Flow ----------------
    if state == "await_reason":
        proc, mins = map_reason_to_procedure(message)
        if not proc:
            return {"reply": pick("invalid_reason")}

        session.update({
            "procedure": proc,
            "duration_minutes": mins,
            "booking_state": "await_date"
        })
        return {"reply": pick("ask_date")}

    if state == "await_date":
        if not validate_date(msg):
            return {"reply": pick("invalid_date")}

        slots = slot_manager.get_available_start_times(
            msg, session["duration_minutes"]
        )

        if not slots:
            clear_booking(session)
            return {"reply": pick("no_slots")}

        session["appointment_date"] = msg
        session["booking_state"] = "await_time"
        return {
            "reply": pick("ask_time", slots="\n".join(f"• {s}" for s in slots))
        }

    if state == "await_time":
        time_24 = normalize_time(msg)
        if not time_24:
            return {"reply": pick("invalid_time")}

        session["appointment_time"] = time_24
        session["booking_state"] = "await_secret"
        session["secret_attempts"] = 0
        return {"reply": pick("ask_secret")}

    if state == "await_secret":
        session["secret_attempts"] += 1

        if session["secret_attempts"] > 3:
            clear_booking(session)
            return {"reply": pick("too_many_attempts")}

        if not validate_secret_key(msg) or msg != user.secret_key:
            return {"reply": pick("wrong_secret")}

        date_obj = datetime.strptime(session["appointment_date"], "%Y-%m-%d").date()
        time_obj = datetime.strptime(session["appointment_time"], "%H:%M").time()

        ok, _ = validate_appointment_conflict(
            user.id, 1, date_obj, time_obj
        )

        if not ok:
            return {"reply": pick("slot_conflict")}

        procedure = session["procedure"]

        # CREATE APPOINTMENT
        db.session.add(Appointment(
            patient_id=user.id,
            doctor_id=1,
            appointment_date=date_obj,
            appointment_time=time_obj,
            procedure=procedure,
            duration_minutes=session["duration_minutes"],
            status="pending",
            source="chatbot"
        ))
        db.session.commit()

        # SEND CONFIRMATION EMAIL
        try:
            formatted_date = date_obj.strftime('%B %d, %Y')
            formatted_time = time_obj.strftime('%I:%M %p')
            
            send_email(
                to_email=user.email,
                subject="📅 Appointment Request Received - MedBot Clinic",
                template_name="appointment_requested.html",
                name=user.name,
                date=formatted_date,
                time_slot=formatted_time
            )
            print(f"✅ Confirmation email sent to {user.email}")
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")

        reply = pick(
            "booking_success",
            date=date_obj,
            time=time_obj,
            procedure=procedure
        )

        clear_booking(session)
        return {"reply": reply}

    # ---------------- Fallback ----------------
    return {"reply": pick("fallback")}