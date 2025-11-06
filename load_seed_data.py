#!/usr/bin/env python3
"""
Load seed data into the Ayra TRQP database.

This script will:
1. Drop all existing tables
2. Recreate the schema
3. Load sample data from seed_data.sql

Usage:
    python load_seed_data.py [--keep-existing]

Options:
    --keep-existing    Don't drop existing data, only add new data
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import Base, engine, SessionLocal
import sqlite3


def drop_all_tables():
    """Drop all tables in the database"""
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")


def create_all_tables():
    """Create all tables from the schema"""
    print("Creating tables from schema...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def load_seed_data():
    """Load seed data from SQL file"""
    print("Loading seed data...")

    # Get database URL from engine
    db_url = str(engine.url)

    if "sqlite" in db_url:
        # Extract database file path
        db_path = db_url.replace("sqlite:///", "")

        # Connect to SQLite and execute seed data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Read and execute SQL file
        seed_file = project_root / "seed_data.sql"
        if not seed_file.exists():
            print(f"✗ Seed data file not found: {seed_file}")
            return False

        with open(seed_file, 'r') as f:
            sql_content = f.read()

            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

            success_count = 0
            error_count = 0
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                        success_count += 1
                    except sqlite3.Error as e:
                        error_count += 1
                        print(f"  ⚠️  Error: {e}")
                        print(f"  Statement: {statement[:150]}...")

            if error_count > 0:
                print(f"⚠️  {error_count} statements failed, {success_count} succeeded")

        conn.commit()
        conn.close()
        print("✓ Seed data loaded successfully")
        return True
    else:
        print("✗ This script currently only supports SQLite databases")
        return False


def verify_data():
    """Verify that data was loaded correctly"""
    print("\nVerifying data...")

    # Use a new session to ensure we see committed data
    db = SessionLocal()

    try:
        from app.database import Entity, Authorization, DIDMethod, AssuranceLevel

        # Force refresh by expiring all objects
        db.expire_all()

        entity_count = db.query(Entity).count()
        auth_count = db.query(Authorization).count()
        did_method_count = db.query(DIDMethod).count()
        assurance_count = db.query(AssuranceLevel).count()

        print(f"  Entities: {entity_count}")
        print(f"  Authorizations: {auth_count}")
        print(f"  DID Methods: {did_method_count}")
        print(f"  Assurance Levels: {assurance_count}")

        if entity_count > 0 and auth_count > 0:
            print("✓ Data verified successfully")

            # Show entity hierarchy
            print("\nEntity Hierarchy:")
            ecosystems = db.query(Entity).filter(Entity.authority_id == None).all()
            for eco in ecosystems:
                print(f"  📦 {eco.name} ({eco.entity_type})")
                children = db.query(Entity).filter(Entity.authority_id == eco.entity_did).all()
                for child in children:
                    print(f"     └─ {child.name} ({child.entity_type})")

            return True
        else:
            print("✗ Data verification failed - no data found")
            return False

    finally:
        db.close()


def main():
    """Main execution"""
    keep_existing = "--keep-existing" in sys.argv

    print("=" * 60)
    print("Ayra TRQP Database Seed Data Loader")
    print("=" * 60)
    print()

    if not keep_existing:
        response = input("This will DELETE all existing data. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

        drop_all_tables()
        create_all_tables()
    else:
        print("Keeping existing data, will only add new records...")

    if load_seed_data():
        if verify_data():
            print("\n" + "=" * 60)
            print("✓ Database seeded successfully!")
            print("=" * 60)
            print("\nYou can now start the server with: python -m app.main")
            print("Or visit the admin UI at: http://localhost:8000/admin-ui")
        else:
            print("\n✗ Data verification failed")
            sys.exit(1)
    else:
        print("\n✗ Failed to load seed data")
        sys.exit(1)


if __name__ == "__main__":
    main()
