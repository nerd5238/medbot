"""
Script to update user emails after migration
Run this AFTER migrate_add_email.py and AFTER updating models.py

Usage: python update_emails.py
"""

from app import app, db
from models import User

def update_emails():
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            
            print("\n" + "="*70)
            print("📋 CURRENT USERS:")
            print("="*70)
            
            for user in users:
                print(f"{user.id}. {user.name} ({user.role}) - Email: {user.email}")
            
            print("\n" + "="*70)
            print("🔄 UPDATING EMAILS...")
            print("="*70 + "\n")
            
            # Update doctor email
            doctor = User.query.filter_by(role='doctor').first()
            if doctor:
                old_email = doctor.email
                doctor.email = 'doctor@medbotclinic.com'
                print(f"✅ Doctor: {old_email} → {doctor.email}")
            
            # You can add more updates here for specific users
            # Example:
            # patient = User.query.get(2)
            # if patient:
            #     patient.email = 'patient@example.com'
            #     print(f"✅ Patient {patient.name}: updated to {patient.email}")
            
            db.session.commit()
            
            print("\n" + "="*70)
            print("✅ EMAILS UPDATED SUCCESSFULLY!")
            print("="*70 + "\n")
            
            # Show updated users
            users = User.query.all()
            print("📋 UPDATED USERS:")
            print("="*70)
            for user in users:
                print(f"{user.id}. {user.name} ({user.role}) - Email: {user.email}")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("UPDATE USER EMAILS")
    print("="*70)
    update_emails()