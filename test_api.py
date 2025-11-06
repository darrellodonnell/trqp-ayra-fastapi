"""
Example test script for Ayra TRQP Profile API
Demonstrates how to interact with the API endpoints
"""

import requests
import json
from datetime import datetime, timezone

# Base URL for the API
BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Helper function to pretty print API responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def test_root():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print_response("ROOT ENDPOINT", response)


def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)


def test_recognition_query():
    """Test the recognition query endpoint"""
    query = {
        "entity_id": "did:example:trustregistry123",
        "authority_id": "did:example:ecosystem456",
        "action": "recognize",
        "resource": "trust_registry",
        "context": {
            "time": datetime.now(timezone.utc).isoformat()
        }
    }
    response = requests.post(f"{BASE_URL}/recognition", json=query)
    print_response("RECOGNITION QUERY", response)


def test_authorization_query():
    """Test the authorization query endpoint"""
    query = {
        "entity_id": "did:example:entity789",
        "authority_id": "did:example:ecosystem456",
        "action": "issue",
        "resource": "credential",
        "context": {}
    }
    response = requests.post(f"{BASE_URL}/authorization", json=query)
    print_response("AUTHORIZATION QUERY", response)


def test_get_metadata():
    """Test the metadata endpoint"""
    response = requests.get(f"{BASE_URL}/metadata?egf_did=did:example:egf789")
    print_response("GET METADATA", response)


def test_get_entity():
    """Test the entity information endpoint"""
    entity_id = "did:example:entity123"
    response = requests.get(f"{BASE_URL}/entities/{entity_id}")
    print_response(f"GET ENTITY: {entity_id}", response)


def test_list_entity_authorizations():
    """Test the entity authorizations endpoint"""
    entity_did = "did:example:entity789"
    response = requests.get(f"{BASE_URL}/entities/{entity_did}/authorizations")
    print_response(f"LIST ENTITY AUTHORIZATIONS: {entity_did}", response)


def test_list_ecosystem_recognitions():
    """Test the ecosystem recognitions endpoint"""
    ecosystem_did = "did:example:ecosystem456"
    response = requests.get(f"{BASE_URL}/ecosystems/{ecosystem_did}/recognitions")
    print_response(f"LIST ECOSYSTEM RECOGNITIONS: {ecosystem_did}", response)


def test_lookup_assurance_levels():
    """Test the assurance levels lookup endpoint"""
    response = requests.get(f"{BASE_URL}/lookups/assuranceLevels?ecosystem_did=did:example:ecosystem456")
    print_response("LOOKUP ASSURANCE LEVELS", response)


def test_lookup_authorizations():
    """Test the authorizations lookup endpoint"""
    response = requests.get(f"{BASE_URL}/lookups/authorizations?ecosystem_did=did:example:ecosystem456")
    print_response("LOOKUP AUTHORIZATIONS", response)


def test_lookup_did_methods():
    """Test the DID methods lookup endpoint"""
    response = requests.get(f"{BASE_URL}/lookups/didMethods?ecosystem_did=did:example:ecosystem456")
    print_response("LOOKUP DID METHODS", response)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Ayra TRQP Profile API - Test Suite")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the server is running before executing tests!")
    print("="*60)

    try:
        # Basic endpoints
        test_root()
        test_health()

        # TRQP Core endpoints
        test_recognition_query()
        test_authorization_query()

        # Ayra Extension endpoints
        test_get_metadata()
        test_get_entity()
        test_list_entity_authorizations()
        test_list_ecosystem_recognitions()

        # Lookup endpoints
        test_lookup_assurance_levels()
        test_lookup_authorizations()
        test_lookup_did_methods()

        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n" + "="*60)
        print("ERROR: Could not connect to the API server")
        print(f"Please make sure the server is running at {BASE_URL}")
        print("Run: python -m app.main")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")


if __name__ == "__main__":
    main()
