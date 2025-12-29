#!/usr/bin/env python
"""
Test script to verify OAuth authentication configuration
Run this before starting the server to verify .env is loaded correctly
"""

from dotenv import load_dotenv
load_dotenv()

from app.auth import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    AUTHORIZED_EMAILS,
    SECRET_KEY,
    is_auth_configured
)

print("=" * 60)
print("OAuth Authentication Configuration Test")
print("=" * 60)
print()

# Check each required variable
checks = []

if GOOGLE_CLIENT_ID:
    print("✅ GOOGLE_CLIENT_ID: Loaded")
    print(f"   Value: {GOOGLE_CLIENT_ID[:20]}...")
    checks.append(True)
else:
    print("❌ GOOGLE_CLIENT_ID: Not set")
    checks.append(False)

print()

if GOOGLE_CLIENT_SECRET:
    print("✅ GOOGLE_CLIENT_SECRET: Loaded")
    print(f"   Value: {GOOGLE_CLIENT_SECRET[:10]}...")
    checks.append(True)
else:
    print("❌ GOOGLE_CLIENT_SECRET: Not set")
    checks.append(False)

print()

if SECRET_KEY and SECRET_KEY != "change-this-to-a-random-secret-key-in-production":
    print("✅ SECRET_KEY: Loaded (custom value)")
    print(f"   Value: {SECRET_KEY[:10]}...")
    checks.append(True)
elif SECRET_KEY:
    print("⚠️  SECRET_KEY: Using default value (should change for production)")
    checks.append(True)
else:
    print("❌ SECRET_KEY: Not set")
    checks.append(False)

print()

if AUTHORIZED_EMAILS:
    print(f"✅ AUTHORIZED_EMAILS: {len(AUTHORIZED_EMAILS)} user(s) configured")
    for i, email in enumerate(AUTHORIZED_EMAILS, 1):
        print(f"   {i}. {email}")
    checks.append(True)
else:
    print("❌ AUTHORIZED_EMAILS: Not set")
    checks.append(False)

print()
print("=" * 60)

if all(checks):
    print("✅ ALL CHECKS PASSED!")
    print(f"✅ Authentication is configured: {is_auth_configured()}")
    print()
    print("You can now start the server with: python main.py")
    print()
    print("Redirect URIs to configure in Google Cloud Console:")
    print("  - http://localhost:8000/admin/auth/callback")

    import os
    external_url = os.getenv('EXTERNAL_URL', '').strip()
    if external_url:
        callback_url = external_url.rstrip('/') + '/admin/auth/callback'
        print(f"  - {callback_url}")
else:
    print("❌ CONFIGURATION INCOMPLETE")
    print()
    print("Please check your .env file and ensure all required variables are set.")
    print("See .env.example for reference.")

print("=" * 60)
