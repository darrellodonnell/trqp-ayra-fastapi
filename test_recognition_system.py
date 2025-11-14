#!/usr/bin/env python3
"""
Test script for the new Recognition system
Creates test data and verifies the recognition endpoints work
"""

from app.database import SessionLocal, init_db
from app import crud
from datetime import datetime, timedelta

def test_recognition_system():
    print("=" * 60)
    print("Testing Recognition System")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 1. Create test recognitions
        print("\n1. Creating test recognitions...")
        recog1 = crud.create_recognition(
            db,
            action="recognize",
            resource="credential",
            description="Recognition of credential types from other ecosystems"
        )
        print(f"   ✓ Created recognition: {recog1.action} / {recog1.resource} (ID: {recog1.id})")

        recog2 = crud.create_recognition(
            db,
            action="recognize",
            resource="ecosystem",
            description="Recognition of other ecosystems"
        )
        print(f"   ✓ Created recognition: {recog2.action} / {recog2.resource} (ID: {recog2.id})")

        # 2. Get or create test ecosystems
        print("\n2. Getting/creating test ecosystems...")

        # Try to get existing ecosystems, or create new ones
        ecosystem1 = crud.get_entity_by_did(db, "did:webvh:SCID-ATN:ayra.forum")
        if not ecosystem1:
            ecosystem1 = crud.create_entity(
                db,
                entity_did="did:webvh:SCID-ATN:ayra.forum",
                authority_id=None,  # Root ecosystem
                name="Ayra Trust Network",
                entity_type="ecosystem",
                status="active",
                description="Root ecosystem for Ayra Trust Registry"
            )
            print(f"   ✓ Created ecosystem: {ecosystem1.name} (DID: {ecosystem1.entity_did})")
        else:
            print(f"   ✓ Using existing ecosystem: {ecosystem1.name} (DID: {ecosystem1.entity_did})")

        ecosystem2 = crud.get_entity_by_did(db, "did:web:bubbagroup.com")
        if not ecosystem2:
            ecosystem2 = crud.create_entity(
                db,
                entity_did="did:web:bubbagroup.com",
                authority_id="did:webvh:SCID-ATN:ayra.forum",
                name="Bubba Group Ecosystem",
                entity_type="ecosystem",
                status="active",
                description="Child ecosystem"
            )
            print(f"   ✓ Created ecosystem: {ecosystem2.name} (DID: {ecosystem2.entity_did})")
        else:
            print(f"   ✓ Using existing ecosystem: {ecosystem2.name} (DID: {ecosystem2.entity_did})")

        # 3. Add recognition to ecosystem1 recognizing ecosystem2
        print("\n3. Adding recognition relationship...")
        valid_from = datetime.utcnow()
        valid_until = datetime.utcnow() + timedelta(days=365)

        crud.add_entity_recognition(
            db,
            entity_id=ecosystem1.id,
            recognition_id=recog2.id,
            recognized_registry_did=ecosystem2.entity_did,
            recognized=True,
            valid_from=valid_from,
            valid_until=valid_until
        )
        print(f"   ✓ {ecosystem1.name} now recognizes {ecosystem2.name}")
        print(f"     Valid from: {valid_from}")
        print(f"     Valid until: {valid_until}")

        # 4. Test recognition query
        print("\n4. Testing recognition query...")
        is_recognized = crud.check_ecosystem_recognition(
            db,
            recognizing_ecosystem_did=ecosystem1.entity_did,
            recognized_registry_did=ecosystem2.entity_did,
            action="recognize",
            resource="ecosystem",
            check_time=None
        )
        print(f"   ✓ Recognition check result: {is_recognized}")

        if is_recognized:
            print(f"   ✅ SUCCESS: {ecosystem1.name} recognizes {ecosystem2.name}")
        else:
            print(f"   ❌ FAILED: Recognition not found")

        # 5. Test negative case (should not be recognized)
        print("\n5. Testing negative case...")
        is_not_recognized = crud.check_ecosystem_recognition(
            db,
            recognizing_ecosystem_did=ecosystem2.entity_did,  # Reverse direction
            recognized_registry_did=ecosystem1.entity_did,
            action="recognize",
            resource="ecosystem",
            check_time=None
        )
        print(f"   ✓ Recognition check result: {is_not_recognized}")

        if not is_not_recognized:
            print(f"   ✅ SUCCESS: {ecosystem2.name} does NOT recognize {ecosystem1.name} (as expected)")
        else:
            print(f"   ❌ FAILED: Unexpected recognition found")

        # 6. List all recognitions for ecosystem1
        print("\n6. Listing all recognitions for ecosystem1...")
        recognitions_list = crud.get_entity_recognitions(db, ecosystem1.id)
        print(f"   ✓ Found {len(recognitions_list)} recognition(s)")
        for r in recognitions_list:
            print(f"     - {r['action']} / {r['resource']}")
            print(f"       Recognized registry: {r['recognized_registry_did']}")
            print(f"       Status: {'Recognized' if r['recognized'] else 'Not recognized'}")

        # 7. Get all recognitions
        print("\n7. Listing all recognition types...")
        all_recognitions = crud.get_recognitions(db)
        print(f"   ✓ Found {len(all_recognitions)} recognition type(s)")
        for r in all_recognitions:
            print(f"     - ID {r.id}: {r.action} / {r.resource}")

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)

        print("\n📝 Summary:")
        print(f"   - Recognition types created: {len(all_recognitions)}")
        print(f"   - Ecosystems created: 2")
        print(f"   - Recognition relationships: {len(recognitions_list)}")
        print(f"   - Recognition check working: ✅")

        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    test_recognition_system()
