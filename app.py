from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import json
from datetime import datetime, date, timedelta

from dotenv import load_dotenv

from flask_mail import Mail
from utils.mailer import send_email

from models import db, User, Appointment
from bot_logic import medbot_reply

# -----------------------------------------
# APP CONFIG
# -----------------------------------------
app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file

app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-dev-key")


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clinic.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# -----------------------------------------
# FLOWISE CONFIG
# -----------------------------------------
FLOWISE_URL = "YOUR_FLOWISE_API_URL"
FLOWISE_TIMEOUT = 12
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY")
DEBUG_FLOWISE = True

# -----------------------------------------
# FLASK-MAIL CONFIG
# -----------------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'clinic_mail id' 
app.config['MAIL_PASSWORD'] = 'APP_PASSWORD'         
app.config['MAIL_DEFAULT_SENDER'] = ('MedBot Dental Clinic', 'sender_mailid')

mail = Mail(app)

# -----------------------------------------
# DB INIT + DEFAULT DOCTOR
# -----------------------------------------
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="doctor").first():
        doctor = User(
            name="Dr. MedBot",
            dob="1980-01-01",
            place="Clinic",
            username="doctor",
            email="doctor@medbotclinic.com",  
            password=generate_password_hash("doctor123"),
            secret_key=None,
            role="doctor"
        )
        db.session.add(doctor)
        db.session.commit()

# -----------------------------------------
# HOME (REAL PAGE)
# -----------------------------------------
@app.route("/")
def home():
    user = User.query.get(session["user_id"]) if "user_id" in session else None
    return render_template("home.html", user=user)

# -----------------------------------------
# DASHBOARD ROUTER
# -----------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "doctor":
        return redirect(url_for("doctor_dashboard"))

    return redirect(url_for("patient_dashboard"))

# -----------------------------------------
# SIGNUP
# -----------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Check username
        if User.query.filter_by(username=request.form["username"]).first():
            return render_template("signup.html", error="Username already exists!")
        
        # 🆕 Check email
        if User.query.filter_by(email=request.form["email"]).first():
            return render_template("signup.html", error="Email already registered!")

        user = User(
            name=request.form["name"],
            dob=request.form["dob"],
            place=request.form["place"],
            username=request.form["username"],
            email=request.form["email"],  # 🆕 ADD THIS LINE
            password=generate_password_hash(request.form["password"]),
            secret_key=request.form["secret_key"],
            role="patient"
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("signup.html")

# -----------------------------------------
# LOGIN
# -----------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    user = User.query.filter_by(username=request.form["username"]).first()

    if user and check_password_hash(user.password, request.form["password"]):
        session.clear()
        session["user_id"] = user.id
        session["role"] = user.role
        session["username"] = user.username

        if user.role == "doctor":
            session["doctor_id"] = user.id

        return redirect(url_for("dashboard"))

    return render_template("login.html", error="Invalid credentials")

# -----------------------------------------
# LOGOUT
# -----------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------------------
# PATIENT DASHBOARD
# -----------------------------------------
@app.route("/patient/dashboard")
def patient_dashboard():
    if "user_id" not in session or session.get("role") != "patient":
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    appointments = Appointment.query.filter_by(
        patient_id=user.id
    ).order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()

    return render_template(
        "patient_dashboard.html",
        user=user,
        appointments=appointments
    )

# -----------------------------------------
# DOCTOR DASHBOARD
# -----------------------------------------
@app.route("/doctor_dashboard")
def doctor_dashboard():
    if "doctor_id" not in session:
        return redirect(url_for("login"))

    today = date.today()
    
    # Today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.appointment_date == today
    ).order_by(Appointment.appointment_time).all()
    
    # Upcoming appointments (after today)
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date > today
    ).order_by(
        Appointment.appointment_date,
        Appointment.appointment_time
    ).limit(5).all()
    
    # Emergency cases (appointments with status "Emergency")
    emergencies = Appointment.query.filter_by(
        status="Emergency"
    ).order_by(Appointment.id.desc()).all()
    
    # Format emergencies to match template expectations
    # If your Appointment model doesn't have patient_name and created_at fields,
    # we'll create them on the fly
    for e in emergencies:
        if not hasattr(e, 'patient_name'):
            e.patient_name = e.patient.name if e.patient else "Unknown"
        if not hasattr(e, 'created_at'):
            e.created_at = datetime.now()

    return render_template(
        "doctor_dashboard.html",
        today=today.strftime('%Y-%m-%d'),
        appointments=today_appointments,
        upcoming_appointments=upcoming_appointments,
        emergencies=emergencies
    )

# -----------------------------------------
# DOCTOR APPOINTMENTS (Full List with Filter)
# -----------------------------------------
@app.route("/doctor/appointments")
def doctor_appointments():
    if "doctor_id" not in session:
        return redirect(url_for("login"))

    filter_type = request.args.get('filter', 'all')
    today = date.today()
    
    query = Appointment.query
    
    # Apply filters
    if filter_type == 'today':
        query = query.filter(Appointment.appointment_date == today)
    elif filter_type == 'upcoming':
        query = query.filter(Appointment.appointment_date > today)
    elif filter_type == 'completed':
        query = query.filter(Appointment.status == 'completed')
    elif filter_type == 'cancelled':
        query = query.filter(
            (Appointment.status == 'cancelled') | 
            (Appointment.status == 'rejected')
        )
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()

    return render_template(
        "doctor_appointments.html",
        appointments=appointments,
        filter=filter_type
    )

# -----------------------------------------
# ADD EMERGENCY CASE
# -----------------------------------------
@app.route("/doctor/add_emergency", methods=["GET", "POST"])
def add_emergency():
    if "doctor_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        # Create emergency appointment
        emergency_appointment = Appointment(
            patient_id=None,  # Emergency cases might not have patient_id initially
            appointment_date=request.form.get("date"),
            appointment_time=request.form.get("time"),
            reason=request.form.get("reason", "Emergency"),
            status="Emergency",
            source="Emergency"
        )
        db.session.add(emergency_appointment)
        db.session.commit()
        
        return redirect(url_for("doctor_dashboard"))
    
    return render_template("add_emergency.html")

# -----------------------------------------
# CHATBOT (HYBRID MODE)
# -----------------------------------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type something 🙂"})

    if "user_id" not in session:
        return jsonify({"reply": "Please log in to continue 😊"})

    # ------------------------------------------------
    # BACKEND MODE (booking already in progress)
    # ------------------------------------------------
    if session.get("booking_state"):
        return jsonify(
            medbot_reply(
                {"intent": None, "message": user_message},
                session
            )
        )

    # ------------------------------------------------
    # AI MODE (Flowise – free conversation)
    # ------------------------------------------------
    try:
        headers = {}
        if FLOWISE_API_KEY:
            headers["Authorization"] = f"Bearer {FLOWISE_API_KEY}"

        res = requests.post(
            FLOWISE_URL,
            headers=headers,
            json={"question": user_message},
            timeout=FLOWISE_TIMEOUT
        )
        res.raise_for_status()
        flowise_data = res.json()

    except Exception as e:
        if DEBUG_FLOWISE:
            print("❌ Flowise error:", e)
        return jsonify({"reply": "⚠️ I'm having trouble right now."})

    # ------------------------------------------------
    # Parse Flowise output
    # Expected:
    # {
    #   reply: "...",
    #   handoff: "none | booking | availability | status"
    # }
    # ------------------------------------------------
    try:
        payload = (
            flowise_data.get("json")
            or json.loads(flowise_data.get("text", "{}"))
        )
    except Exception:
        payload = {}

    reply = payload.get("reply", "🤔 I'm not sure about that.")
    handoff = payload.get("handoff", "none")

    # ------------------------------------------------
    # HARD SAFETY NET (AI may miss intent)
    # ------------------------------------------------
    if handoff == "none":
        lowered = user_message.lower()
        if any(k in lowered for k in [
            "book", "appointment", "schedule", "visit dentist",
            "checkup", "cleaning", "tooth pain"
        ]):
            handoff = "booking"

    # ------------------------------------------------
    # NORMAL CHAT
    # ------------------------------------------------
    if handoff == "none":
        return jsonify({"reply": reply})

    # ------------------------------------------------
    # HANDOFF → BACKEND AUTHORITY
    # ------------------------------------------------
    handoff_map = {
        "booking": "book",
        "availability": "availability",
        "status": "status"
    }

    intent = handoff_map.get(handoff, handoff)

    return jsonify(
        medbot_reply(
            {"intent": intent, "message": user_message},
            session
        )
    )

@app.route("/chatbot/greet", methods=["POST"])
def chatbot_greet():
    if "user_id" not in session:
        return jsonify({"reply": None})

    if session.get("chatbot_greeted"):
        return jsonify({"reply": None})

    session["chatbot_greeted"] = True

    return jsonify({
        "reply": "Heyy! 👋 I'm MedBot 😊\nHow can I help you today?"
    })

# -----------------------------------------
# APPROVE APPOINTMENT (Updated)
# -----------------------------------------
@app.route("/doctor/appointment/<int:appointment_id>/approve", methods=["POST"])
def approve_appointment(appointment_id):
    if "doctor_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.status != "pending":
        return jsonify({
            "success": False,
            "message": f"Appointment is already {appointment.status}"
        })
    
    appointment.status = "approved"
    db.session.commit()
    
    patient = User.query.get(appointment.patient_id)
    
    if not patient:
        return jsonify({"success": False, "message": "Patient not found"})
    
    formatted_date = appointment.appointment_date.strftime('%B %d, %Y')
    formatted_time = appointment.appointment_time.strftime('%I:%M %p')
    
    try:
        send_email(
            to_email=patient.email,  # 🆕 Use email field
            subject="✅ Appointment Approved - MedBot Clinic",
            template_name="appointment_approved.html",
            name=patient.name,
            date=formatted_date,
            time_slot=formatted_time
        )
        
        return jsonify({
            "success": True, 
            "message": f"Appointment approved! Email sent to {patient.name}"
        })
    except Exception as e:
        print(f"❌ Email error: {e}")
        return jsonify({
            "success": True, 
            "message": f"Appointment approved but email failed: {str(e)}"
        })

# -----------------------------------------
# REJECT APPOINTMENT (Updated)
# -----------------------------------------
@app.route("/doctor/appointment/<int:appointment_id>/reject", methods=["POST"])
def reject_appointment(appointment_id):
    if "doctor_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    rejection_reason = data.get("reason", "Slot unavailable")
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.status != "pending":
        return jsonify({
            "success": False,
            "message": f"Appointment is already {appointment.status}"
        })
    
    appt_time_display = appointment.appointment_time.strftime('%I:%M %p')
    
    appointment.status = "rejected"
    db.session.commit()
    
    patient = User.query.get(appointment.patient_id)
    
    if not patient:
        return jsonify({"success": False, "message": "Patient not found"})
    
    try:
        send_email(
            to_email=patient.email,  # 🆕 Use email field
            subject="Appointment Update - MedBot Clinic",
            template_name="appointment_rejected.html",
            name=patient.name,
            reason=rejection_reason
        )
        
        message = f"Appointment rejected and email sent to {patient.name}. "
        message += f"✅ Time slot {appt_time_display} is now available for other patients."
        
        return jsonify({"success": True, "message": message})
    except Exception as e:
        print(f"❌ Email error: {e}")
        return jsonify({
            "success": True, 
            "message": f"Appointment rejected but email failed: {str(e)}"
        })

# -----------------------------------------
# MANUAL BOOKING (Updated to use email field)
# -----------------------------------------
@app.route("/book-appointment", methods=["GET", "POST"])
def manual_booking():
    if "user_id" not in session or session.get("role") != "patient":
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    
    if request.method == "GET":
        min_date = date.today().strftime('%Y-%m-%d')
        return render_template("manual_booking.html", user=user, min_date=min_date)
    
    # POST - Process booking
    try:
        secret_key = request.form.get("secret_key")
        
        if secret_key != user.secret_key:
            return render_template(
                "manual_booking.html",
                user=user,
                min_date=date.today().strftime('%Y-%m-%d'),
                error="Invalid secret key. Please try again."
            )
        
        appointment_date = datetime.strptime(request.form.get("appointment_date"), "%Y-%m-%d").date()
        appointment_time = datetime.strptime(request.form.get("appointment_time"), "%H:%M").time()
        
        if appointment_date < date.today():
            return render_template(
                "manual_booking.html",
                user=user,
                min_date=date.today().strftime('%Y-%m-%d'),
                error="Cannot book appointments in the past."
            )
        
        from utils.validators import validate_appointment_conflict
        ok, conflict_msg = validate_appointment_conflict(user.id, 1, appointment_date, appointment_time)
        
        if not ok:
            return render_template(
                "manual_booking.html",
                user=user,
                min_date=date.today().strftime('%Y-%m-%d'),
                error=conflict_msg or "This time slot is no longer available."
            )
        
        procedure = request.form.get("procedure")
        duration = int(request.form.get("duration_minutes", 30))
        
        new_appointment = Appointment(
            patient_id=user.id,
            doctor_id=1,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            duration_minutes=duration,
            reason=request.form.get("reason"),
            procedure=procedure,
            status="pending",
            source="manual"
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        # Send email using the new email field
        try:
            send_email(
                to_email=user.email,  # 🆕 Use email field instead of username
                subject="Appointment Request Received - MedBot Clinic",
                template_name="appointment_requested.html",
                name=user.name,
                date=appointment_date.strftime('%B %d, %Y'),
                time_slot=appointment_time.strftime('%I:%M %p'),
                procedure=procedure
            )
        except Exception as e:
            print(f"📧 Email notification failed: {e}")
        
        return render_template(
            "manual_booking.html",
            user=user,
            min_date=date.today().strftime('%Y-%m-%d'),
            success=f"✅ Appointment booked successfully! Your appointment is on {appointment_date.strftime('%B %d, %Y')} at {appointment_time.strftime('%I:%M %p')}. Please wait for doctor's approval."
        )
        
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return render_template(
            "manual_booking.html",
            user=user,
            min_date=date.today().strftime('%Y-%m-%d'),
            error=f"An error occurred: {str(e)}"
        )
# -----------------------------------------
# API: AVAILABLE SLOTS
# -----------------------------------------
@app.route("/api/available-slots", methods=["GET"])
def get_available_slots():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    date_str = request.args.get("date")
    duration = request.args.get("duration", type=int)
    
    if not date_str or not duration:
        return jsonify({"success": False, "message": "Date and duration are required"}), 400
    
    try:
        from utils.slot_manager import SlotManager
        slot_manager = SlotManager()
        available_slots = slot_manager.get_available_start_times(date_str, duration)
        
        return jsonify({
            "success": True,
            "slots": available_slots,
            "date": date_str,
            "duration": duration
        })
    except Exception as e:
        print(f"❌ Error fetching slots: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# -----------------------------------------
# RUN
# -----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)