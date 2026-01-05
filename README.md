# 🏥 MedBot - Smart Dental Clinic Management System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A modern, AI-powered clinic management system designed for dental clinics. Features include intelligent appointment booking via chatbot, manual booking forms, doctor approval workflow, automated email notifications, and real-time slot management.

## ✨ Features

### 👥 For Patients
- 🤖 **AI Chatbot Booking** - Natural language appointment scheduling
- 📋 **Manual Booking Form** - Quick visual appointment booking
- 📧 **Email Notifications** - Automated confirmations and updates
- 🔐 **Secure Authentication** - Secret key verification for bookings
- 📱 **Responsive Design** - Works seamlessly on mobile and desktop
- 📊 **Dashboard** - View appointment history and status

### 👨‍⚕️ For Doctors
- ✅ **Approval Workflow** - Accept or reject appointments with one click
- 📅 **Smart Dashboard** - Today's, upcoming, and emergency appointments
- 📧 **Automated Emails** - Notifications sent to patients automatically
- 🔄 **Slot Management** - Rejected slots automatically become available
- 📊 **Appointment Filtering** - Filter by date, status, or type
- 🚨 **Emergency Cases** - Dedicated section for urgent appointments

### 🛠️ Technical Features
- 🤖 **Flowise AI Integration** - Hybrid chatbot with intent detection
- ⚡ **Real-time Slot Availability** - Dynamic scheduling algorithm
- 🔒 **Security** - Password hashing, secret key verification
- 📱 **Modern UI** - Gradient designs, smooth animations
- 🎨 **Dark Mode** - Optional dark theme for chatbot
- 📧 **Professional Emails** - HTML email templates

---

## 🖼️ Screenshots

![Chatbot]
<p align="center">
  <img src="output screenshots/2.png" width="600">
</p>
![Booking Form]
<p align="center">
  <img src="output screenshots/3.png" width="600">
</p>
![Doctor Dashboard]
<p align="center">
  <img src="output screenshots/4.png" width="600">
</p>
---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Gmail account (for email notifications)
- Flowise instance (optional, for AI chatbot)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/nerd5238/medbot-clinic-management.git
cd medbot-clinic-management
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
# See Configuration section below
```

5. **Run the application**
```bash
python app.py
```

6. **Open browser**
```
http://localhost:5000
```

---

## ⚙️ Configuration

### 1. Gmail API Setup (Required for Email Notifications)

#### **Step 1: Enable 2-Step Verification**
1. Go to https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification**
3. Follow steps to enable

#### **Step 2: Generate App Password**
1. Go to **Security** → **App passwords**
2. Select **Mail** and **Other (Custom name)**
3. Enter "MedBot Clinic"
4. Click **Generate**
5. Copy the 16-character password

#### **Step 3: Update .env file**
```env
MAIL_USERNAME=your-clinic-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Paste the 16-char password
```

⚠️ **Important**: Use the App Password, NOT your regular Gmail password!

---

### 2. Flowise AI Setup (Optional - for AI Chatbot)

Flowise provides the AI-powered conversational interface for the chatbot.

#### **Option A: Use Existing Flowise Instance**

If you already have Flowise running:

1. Create a new chatflow in Flowise
2. Configure intent detection with these intents:
   - `booking` - Appointment booking requests
   - `status` - Check appointment status
   - `clinic_info` - Clinic information queries
   - `greeting` - Greetings
   - `help` - Help requests
3. Get your chatflow prediction URL
4. Update `.env`:

```env
FLOWISE_URL=http://localhost:3000/api/v1/prediction/YOUR-FLOW-ID
FLOWISE_API_KEY=your-api-key  # Optional, if you set one
```

#### **Option B: Install Flowise Locally**

1. **Install Node.js** (16.x or higher)
   - Download from: https://nodejs.org/

2. **Install Flowise**
```bash
npm install -g flowise
```

3. **Start Flowise**
```bash
npx flowise start
```

4. **Access Flowise**
   - Open: http://localhost:3000
   - Create account
   - Build chatflow with intent detection

5. **Configure Chatflow**
   - Add Language Model (OpenAI, Claude, etc.)
   - Add Intent Classifier
   - Configure intents: `booking`, `status`, `clinic_info`, `greeting`, `help`
   - Set response to return JSON: `{reply: "...", handoff: "none|booking|status|clinic_info"}`
   
## 🤖 AI Chatbot Architecture (Flowise)

<p align="center">
  <img src="output screenshots/6.png" width="800" alt="Flowise Chatflow Architecture">
</p>

**Flow Description:**
- JSON File node provides structured clinic responses
- Prompt Template defines assistant behavior and constraints
- HuggingFace Chat Model handles natural language understanding
- LLM Chain orchestrates response generation and intent handling
- Backend logic validates and executes all database operations

<p align="center">
  <em>Intent-based chatbot architecture built using Flowise (Agentic AI)</em>
</p>


6. **Get API Details**
   - Click **API** button on chatflow
   - Copy Prediction URL
   - Add to `.env` file

#### **Option C: Run Without Flowise**

The system can work without Flowise (chatbot will use basic pattern matching):

```env
# Leave these commented out or empty
# FLOWISE_URL=
# FLOWISE_API_KEY=
```

The chatbot will still work using the `bot_logic.py` fallback.

---

### 3. Database Setup

The application uses SQLite by default (no setup needed).

**First Run:**
```bash
python app.py
```

This will:
- Create `instance/clinic.db`
- Create all tables
- Add default doctor account:
  - Username: `doctor`
  - Password: `doctor123`
  - Email: `doctor@medbotclinic.com`

**Change Default Doctor Password:**
```python
# In app.py, find doctor creation section and update:
password=generate_password_hash("your-secure-password")
```

---

### 4. Environment Variables

Complete `.env` file template:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key-here-change-this

# Gmail Configuration (Required for emails)
MAIL_USERNAME=your-clinic-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx

# Flowise Configuration (Optional - for AI chatbot)
FLOWISE_URL=http://localhost:3000/api/v1/prediction/your-flow-id
FLOWISE_API_KEY=your-flowise-api-key

# Database (Optional - defaults to SQLite)
DATABASE_URI=sqlite:///clinic.db

# Debug Mode (Set to False in production)
DEBUG=True
```

---

## 📖 Usage Guide

### For Patients

#### **Method 1: Chatbot Booking**
1. Login or create account
2. Click chatbot icon (💬) in bottom-right
3. Type: "I want to book an appointment"
4. Follow the conversation:
   - Describe reason (e.g., "tooth pain", "cleaning")
   - Choose date
   - Select time slot
   - Enter secret key
5. Receive confirmation email
6. Wait for doctor approval

#### **Method 2: Manual Booking**
1. Login to patient account
2. Click **"📅 Book Appointment"** in navigation
3. Fill the form:
   - Select reason from dropdown
   - Pick date (date picker)
   - Choose available time slot
   - Enter secret key
4. Submit → Confirmation email sent
5. Wait for doctor approval

### For Doctors

1. Login with doctor credentials:
   - Username: `doctor`
   - Password: `doctor123` (change this!)

2. **Dashboard shows:**
   - Today's appointments
   - Upcoming appointments pending approval
   - Emergency cases

3. **To approve:**
   - Click **✓ Accept** button
   - Patient receives approval email
   - Slot remains blocked

4. **To reject:**
   - Click **✗ Reject** button
   - Select rejection reason
   - Confirm
   - Patient receives rejection email
   - Slot becomes available for others

---

## 🏗️ Project Structure

```
medbot-clinic-management/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── bot_logic.py               # Chatbot conversation logic
├── clinic_responses.json      # Bot response templates
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
│
├── instance/
│   └── clinic.db             # SQLite database (auto-generated)
│
├── static/
│   ├── css/
│   │   ├── style.css         # Main stylesheet
│   │   └── chatbot.css       # Chatbot-specific styles
│   ├── js/
│   │   ├── chatbot.js        # Chatbot functionality
│   │   └── ui.js             # UI interactions
│   ├── img/
│   │   ├── logo.png          # Clinic logo
│   │   └── doctor.png        # Doctor image
│   └── sounds/
│       ├── send.mp3          # Message send sound
│       └── receive.wav       # Message receive sound
│
├── templates/
│   ├── base.html             # Base template
│   ├── home.html             # Landing page
│   ├── login.html            # Login page
│   ├── signup.html           # Signup page
│   ├── patient_dashboard.html    # Patient dashboard
│   ├── doctor_dashboard.html     # Doctor dashboard
│   ├── doctor_appointments.html  # All appointments view
│   ├── manual_booking.html       # Manual booking form
│   ├── add_emergency.html        # Emergency case form
│   ├── chatbot_window.html       # Chatbot widget
│   └── email_templates/
│       ├── appointment_requested.html  # Request confirmation
│       ├── appointment_approved.html   # Approval email
│       └── appointment_rejected.html   # Rejection email
│
└── utils/
    ├── mailer.py             # Email sending utility
    ├── slot_manager.py       # Appointment slot logic
    └── validators.py         # Input validation functions
```

---

## 🔧 Customization

### Change Clinic Information

Edit `bot_logic.py`:
```python
CLINIC_INFO = {
    "name": "Your Clinic Name",
    "services": [
        "Your services here",
    ],
    "timings": "Your working hours",
    "doctor": "Dr. Your Name"
}
```

### Modify Working Hours

Edit `utils/slot_manager.py`:
```python
SlotManager(
    start_time="09:00",      # Clinic opens
    lunch_start="13:00",     # Lunch starts
    lunch_end="14:00",       # Lunch ends
    end_time="18:00",        # Clinic closes
    step_minutes=15          # Slot intervals
)
```

### Add New Procedures

Edit `bot_logic.py` TREATMENTS:
```python
TREATMENTS = [
    (["keywords"], "Procedure Name", duration_minutes),
    # Example:
    (["whitening", "white teeth"], "Teeth Whitening", 45),
]
```

### Customize Email Templates

Edit files in `templates/email_templates/`:
- Change colors, fonts, layout
- Add clinic logo
- Modify text content

---

## 🐛 Troubleshooting

### Issue: Emails Not Sending

**Symptoms:** Appointments work but no emails received

**Solutions:**
1. Check Gmail App Password is correct (16 characters)
2. Verify 2-Step Verification is enabled
3. Check `.env` has correct `MAIL_USERNAME` and `MAIL_PASSWORD`
4. Look for errors in terminal
5. Test with this command:
```python
from app import app, mail
from flask_mail import Message

with app.app_context():
    msg = Message("Test", recipients=["test@example.com"])
    msg.body = "Test email"
    mail.send(msg)
```

### Issue: Chatbot Not Responding

**Symptoms:** Chatbot shows but doesn't reply

**Solutions:**
1. Check Flowise is running (if using)
2. Verify `FLOWISE_URL` is correct
3. Check terminal for error messages
4. Test Flowise API directly in browser
5. Try without Flowise (comment out FLOWISE_URL)

### Issue: Slots Not Showing

**Symptoms:** No time slots appear when booking

**Solutions:**
1. Check date is not in the past
2. Verify all slots aren't already booked
3. Check `slot_manager.py` working hours
4. Look for errors in browser console (F12)
5. Test API: `/api/available-slots?date=2026-01-10&duration=30`

### Issue: Database Errors

**Symptoms:** Error about missing columns

**Solutions:**
1. Delete `instance/clinic.db`
2. Restart Flask: `python app.py`
3. Database will be recreated
4. Create new test accounts

### Issue: Port Already in Use

**Symptoms:** Error: "Address already in use"

**Solutions:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

---

## 🚀 Deployment

### Deploy to Heroku

1. **Install Heroku CLI**
   - Download from: https://devcenter.heroku.com/articles/heroku-cli

2. **Create Heroku App**
```bash
heroku login
heroku create your-clinic-name
```

3. **Add Buildpack**
```bash
heroku buildpacks:set heroku/python
```

4. **Set Environment Variables**
```bash
heroku config:set FLASK_SECRET_KEY=your-secret
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password
heroku config:set FLOWISE_URL=your-flowise-url
```

5. **Deploy**
```bash
git push heroku main
```

6. **Open App**
```bash
heroku open
```

### Deploy to Railway

1. Go to https://railway.app
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Connect your repository
4. Add environment variables in Railway dashboard
5. Deploy automatically

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add comments for complex logic
- Test before submitting PR
- Update documentation if needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: Nerd 5238 (https://github.com/your-username)
- Email: sriragav235@gmail.com
- LinkedIn: Shri Ragavendra K (https://www.linkedin.com/in/shri-ragavendra-k/))

---

## 🙏 Acknowledgments

- **Flask** - Web framework
- **Flowise** - AI chatbot platform
- **SQLAlchemy** - Database ORM
- **Flask-Mail** - Email integration
- **Tailwind CSS** - UI styling inspiration

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [GitHub Issues](https://github.com/your-username/medbot-clinic-management/issues)
3. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] SMS notifications via Twilio
- [ ] Patient medical records
- [ ] Prescription management
- [ ] Payment integration
- [ ] Multi-doctor support

### Version 1.2 (Future)
- [ ] Video consultation
- [ ] Appointment reminders
- [ ] Patient feedback system
- [ ] Analytics dashboard
- [ ] Multi-language support

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/medbot-clinic-management&type=Date)](https://star-history.com/#your-username/medbot-clinic-management&Date)

---

<div align="center">

---

## ☕ Support

If this project helped you or saved you time, you can support my work here:

<a href="https://www.buymeacoffee.com/nerd5238" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
       alt="Buy Me A Coffee"
       height="45">
</a>

**Made with ❤️ for healthcare professionals**

[Report Bug](https://github.com/your-username/medbot-clinic-management/issues) · [Request Feature](https://github.com/your-username/medbot-clinic-management/issues) · [Documentation](https://github.com/your-username/medbot-clinic-management/wiki)

</div> 
