#!/usr/bin/env python3
"""
Load seed data into the Ayra TRQP database.

This script will:
1. Optionally drop all existing tables
2. Recreate the schema
3. Load seed data from a selected SQL file

Usage:
    python load_seed_data.py
    python load_seed_data.py --preset cts-sandbox --yes
    python load_seed_data.py --seed-file seed_data_cts_sandbox.sql --yes

Options:
    --keep-existing    Don't drop existing data, only add new data
    --seed-file        Path to a SQL seed file
    --preset           Named seed preset (default, cts-sandbox)
    --yes              Skip the destructive confirmation prompt
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import Base, SessionLocal, engine


PRESET_FILES = {
    "default": project_root / "seed_data.sql",
    "cts-sandbox": project_root / "seed_data_cts_sandbox.sql",
}


def drop_all_tables():
    """Drop all tables in the database."""
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")


def create_all_tables():
    """Create all tables from the schema."""
    print("Creating tables from schema...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def resolve_seed_file(seed_file: str | None, preset: str) -> Path:
    """Resolve the requested seed file path."""
    if seed_file:
        path = Path(seed_file)
        if not path.is_absolute():
            path = project_root / path
        return path

    return PRESET_FILES[preset]


def load_seed_data(seed_file: Path) -> bool:
    """Load seed data from a SQL file."""
    print(f"Loading seed data from {seed_file.name}...")

    db_url = str(engine.url)
    if "sqlite" not in db_url:
        print("✗ This script currently only supports SQLite databases")
        return False

    db_path = db_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if not seed_file.exists():
        print(f"✗ Seed data file not found: {seed_file}")
        conn.close()
        return False

    with open(seed_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    try:
        cursor.executescript(sql_content)
    except sqlite3.Error as e:
        print(f"✗ Error executing seed SQL: {e}")
        conn.rollback()
        conn.close()
        return False

    conn.commit()
    conn.close()
    print("✓ Seed data loaded successfully")
    return True


def verify_data() -> bool:
    """Verify that data was loaded correctly."""
    print("\nVerifying data...")

    db = SessionLocal()
    try:
        from app.database import AssuranceLevel, Authorization, Entity, Recognition, DIDMethod

        db.expire_all()

        entity_count = db.query(Entity).count()
        auth_count = db.query(Authorization).count()
        recog_count = db.query(Recognition).count()
        did_method_count = db.query(DIDMethod).count()
        assurance_count = db.query(AssuranceLevel).count()

        print(f"  Entities: {entity_count}")
        print(f"  Authorizations: {auth_count}")
        print(f"  Recognitions: {recog_count}")
        print(f"  DID Methods: {did_method_count}")
        print(f"  Assurance Levels: {assurance_count}")

        if entity_count > 0 and auth_count > 0:
            print("✓ Data verified successfully")

            print("\nEntity Hierarchy:")
            ecosystems = db.query(Entity).filter(Entity.authority_id == None).all()
            for eco in ecosystems:
                print(f"  📦 {eco.name} ({eco.entity_type})")
                children = db.query(Entity).filter(Entity.authority_id == eco.entity_did).all()
                for child in children:
                    print(f"     └─ {child.name} ({child.entity_type})")

            return True

        print("✗ Data verification failed - no data found")
        return False
    finally:
        db.close()


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Seed the Ayra TRQP database")
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Don't drop existing data, only add new records",
    )
    parser.add_argument(
        "--seed-file",
        help="Path to a SQL seed file (relative to repo root or absolute path)",
    )
    parser.add_argument(
        "--preset",
        default="default",
        choices=sorted(PRESET_FILES),
        help="Named seed preset to load when --seed-file is not provided",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the destructive confirmation prompt",
    )
    return parser.parse_args()


def main():
    """Main execution."""
    args = parse_args()
    keep_existing = args.keep_existing
    seed_file = resolve_seed_file(args.seed_file, args.preset)

    print("=" * 60)
    print("Ayra TRQP Database Seed Data Loader")
    print("=" * 60)
    print()
    print(f"Seed source: {seed_file}")
    print()

    if not keep_existing:
        if not args.yes:
            response = input("This will DELETE all existing data. Continue? (yes/no): ")
            if response.lower() != "yes":
                print("Aborted.")
                return

        drop_all_tables()
        create_all_tables()
    else:
        print("Keeping existing data, will only add new records...")

    if load_seed_data(seed_file):
        if verify_data():
            print("\n" + "=" * 60)
            print("✓ Database seeded successfully!")
            print("=" * 60)
            print("\nYou can now start the server with: python3 main.py")
            print("Or visit the admin UI at: http://localhost:8000/admin/ui")
        else:
            print("\n✗ Data verification failed")
            sys.exit(1)
    else:
        print("\n✗ Failed to load seed data")
        sys.exit(1)


if __name__ == "__main__":
    main()
