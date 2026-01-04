from flask_mail import Message
from flask import render_template

def send_email(to_email, subject, template_name, **kwargs):
    """
    Sends an email using the given template inside templates/email_templates/
    Example usage:
        send_email(user.email, "Appointment Approved", "appointment_approved.html",
                   name=user.name, date=..., time_slot=...)
    """
    try:
        # Import mail only when function is called (lazy import)
        from app import mail
        
        msg = Message(
            subject=subject,
            sender=("MedBot Dental Clinic", "yourclinicmail@gmail.com"),
            recipients=[to_email]
        )
        # Render HTML template with required variables
        msg.html = render_template(f"email_templates/{template_name}", **kwargs)
        mail.send(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")