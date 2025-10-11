#!/usr/bin/env python3

import os
import sys
from app import app, db, Project, BlogPost, ContactMessage, NewsletterSubscriber

def create_database():
    with app.app_context():
        # Safety check for production
        if os.environ.get('FLASK_ENV') == 'production':
            confirm = input("WARNING: You are about to reset the production database. Type 'YES' to continue: ")
            if confirm != 'YES':
                print("Database reset cancelled.")
                return

        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        # Only add sample data in development
        if os.environ.get('FLASK_ENV') != 'production':
            print("Adding sample data...")
            # Add your sample data population here
            # Example:
            # sample_project = Project(title="Sample Project", ...)
            # db.session.add(sample_project)
            db.session.commit()
        
        print("\nDatabase initialized successfully!")
        print("Available tables:", [table.name for table in db.metadata.tables.values()])

if __name__ == "__main__":
    # Set environment variables if not set
    if not os.environ.get('FLASK_APP'):
        os.environ['FLASK_APP'] = 'app.py'
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    print(f"Initializing database in {os.environ['FLASK_ENV']} environment...")
    create_database()