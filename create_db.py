#!/usr/bin/env python3

from app import app, db

def create_database():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables with new schema
        db.create_all()

        print("Database recreated successfully with new schema!")
        print("Available tables:", [table.name for table in db.metadata.tables.values()])

if __name__ == "__main__":
    create_database()
