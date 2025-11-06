#!/usr/bin/env python3
"""
Database Initialization Script
Run this script to initialize the database and seed it with default data
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db, seed_default_data

def main():
    print("Initializing database...")
    init_db()
    print("Database tables created successfully!")

    print("\nSeeding default data...")
    seed_default_data()
    print("Default data seeded successfully!")

    print("\n✅ Database initialization complete!")
    print("\nDefault data includes:")
    print("  - 4 DID Methods (web, key, peer, sov)")
    print("  - 3 Assurance Levels (LOA1, LOA2, LOA3)")
    print("  - 4 Authorizations (issue, verify, revoke, register)")
    print("  - 1 Trust Registry Configuration")
    print("\nYou can now:")
    print("  1. Start the server: python -m app.main")
    print("  2. Access the Admin UI: http://localhost:8000/admin-ui")
    print("  3. View API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
