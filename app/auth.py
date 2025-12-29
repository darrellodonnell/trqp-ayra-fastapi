"""
Authentication and authorization for the admin API using Google OAuth
"""
import os
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from itsdangerous import URLSafeTimedSerializer
import logging

logger = logging.getLogger(__name__)

# OAuth Configuration from environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-random-secret-key-in-production")

# Support both single email (backward compatible) and multiple emails
AUTHORIZED_EMAIL = os.getenv("AUTHORIZED_EMAIL")  # Legacy single email support
AUTHORIZED_EMAILS_STR = os.getenv("AUTHORIZED_EMAILS")  # New comma-separated list

# Parse authorized emails list
AUTHORIZED_EMAILS = []
if AUTHORIZED_EMAILS_STR:
    # Split by comma and strip whitespace from each email
    AUTHORIZED_EMAILS = [email.strip() for email in AUTHORIZED_EMAILS_STR.split(",") if email.strip()]
elif AUTHORIZED_EMAIL:
    # Backward compatibility: if only AUTHORIZED_EMAIL is set, use it
    AUTHORIZED_EMAILS = [AUTHORIZED_EMAIL.strip()]

# Validate configuration
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    logger.warning(
        "Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET "
        "in your .env file to enable authentication."
    )

if not AUTHORIZED_EMAILS:
    logger.warning(
        "No authorized emails configured. Set AUTHORIZED_EMAILS in your .env file "
        "to specify which Google accounts can access the admin interface."
    )
else:
    logger.info(f"Configured {len(AUTHORIZED_EMAILS)} authorized user(s) for admin access")

# Initialize OAuth
oauth = OAuth()

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Session serializer
serializer = URLSafeTimedSerializer(SECRET_KEY)


def get_session_middleware():
    """
    Returns SessionMiddleware configured with the secret key
    """
    return SessionMiddleware(
        app=None,  # Will be set when added to FastAPI app
        secret_key=SECRET_KEY,
        session_cookie="admin_session",
        max_age=3600 * 24,  # 24 hours
        same_site="lax",
        https_only=False  # Set to True in production with HTTPS
    )


def get_current_user(request: Request) -> dict:
    """
    Dependency to get the current authenticated user from session.
    Raises HTTPException if user is not authenticated or not authorized.
    """
    # Check if authentication is configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )

    if not AUTHORIZED_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No authorized emails configured. Please set AUTHORIZED_EMAILS in .env file."
        )

    # Get user from session
    user = request.session.get('user')

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is authorized
    user_email = user.get('email')
    if user_email not in AUTHORIZED_EMAILS:
        authorized_list = ", ".join(AUTHORIZED_EMAILS)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Only the following accounts are authorized: {authorized_list}"
        )

    return user


def optional_auth(request: Request) -> Optional[dict]:
    """
    Optional authentication - returns user if authenticated, None otherwise.
    Does not raise exceptions.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return None

    user = request.session.get('user')
    if not user:
        return None

    # Check if user is authorized
    user_email = user.get('email')
    if user_email not in AUTHORIZED_EMAILS:
        return None

    return user


def is_auth_configured() -> bool:
    """
    Check if authentication is properly configured
    """
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and AUTHORIZED_EMAILS)


def get_authorized_emails() -> list:
    """
    Get the list of authorized email addresses
    """
    return AUTHORIZED_EMAILS.copy()
