"""
Database migration script to add email column to users table
Run this BEFORE starting the app with updated models.py

Usage: python migrate_add_email.py
"""

import sqlite3
import os

def migrate_database():
    # Path to your database
    db_path = os.path.join('instance', 'clinic.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        # Connect to SQLite database directly
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if email column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'email' in columns:
            print("✅ Email column already exists!")
            conn.close()
            return
        
        print("🔄 Adding email column to users table...")
        
        # Add email column
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(120)")
        conn.commit()
        print("✅ Email column added!")
        
        # Migrate existing data: copy username to email
        print("🔄 Migrating existing data (username → email)...")
        cursor.execute("UPDATE users SET email = username WHERE email IS NULL")
        conn.commit()
        print("✅ Data migrated!")
        
        # Display current users
        print("\n" + "="*70)
        print("📋 CURRENT USERS IN DATABASE:")
        print("="*70)
        cursor.execute("SELECT id, name, username, email, role FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_id, name, username, email, role = user
            print(f"ID: {user_id} | Name: {name} | Username: {username} | Email: {email} | Role: {role}")
        
        print("\n" + "="*70)
        print("⚠️  IMPORTANT NEXT STEPS:")
        print("="*70)
        print("1. Update existing users' emails if they are not actual email addresses")
        print("2. You can update emails using the update_emails.py script")
        print("3. For the doctor account, update email to a valid address")
        print("\nExample SQL to update:")
        print("   UPDATE users SET email = 'patient@example.com' WHERE id = 2;")
        print("   UPDATE users SET email = 'doctor@medbotclinic.com' WHERE role = 'doctor';")
        print("="*70 + "\n")
        
        conn.close()
        
        print("✅ Migration completed successfully!")
        print("🚀 You can now start your Flask app with the updated models.py")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATABASE MIGRATION: Adding Email Column")
    print("="*70 + "\n")
    migrate_database()