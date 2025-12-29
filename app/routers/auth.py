"""
Authentication routes for Google OAuth
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from app.auth import oauth, get_authorized_emails, is_auth_configured
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """
    Initiate Google OAuth login flow
    """
    if not is_auth_configured():
        return HTMLResponse(
            content="""
            <html>
                <head><title>Authentication Not Configured</title></head>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1>⚠️ Authentication Not Configured</h1>
                    <p>Please configure Google OAuth in your .env file:</p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>GOOGLE_CLIENT_ID</li>
                        <li>GOOGLE_CLIENT_SECRET</li>
                        <li>AUTHORIZED_EMAILS (comma-separated list)</li>
                        <li>SECRET_KEY</li>
                    </ul>
                    <p><a href="/admin/ui">Go back</a></p>
                </body>
            </html>
            """,
            status_code=503
        )

    # Get the redirect URI - this should match what's configured in Google Console
    redirect_uri = request.url_for('auth_callback')
    logger.info(f"Initiating OAuth flow with redirect URI: {redirect_uri}")

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request):
    """
    Handle Google OAuth callback
    """
    if not is_auth_configured():
        raise HTTPException(status_code=503, detail="Authentication not configured")

    try:
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            user_info = await oauth.google.parse_id_token(request, token)

        logger.info(f"User logged in: {user_info.get('email')}")

        # Check if user is authorized
        user_email = user_info.get('email')
        authorized_emails = get_authorized_emails()

        if user_email not in authorized_emails:
            # Create a sanitized list for display (show only if 3 or fewer emails)
            if len(authorized_emails) <= 3:
                email_display = ", ".join(authorized_emails)
            else:
                email_display = f"{len(authorized_emails)} authorized accounts"

            return HTMLResponse(
                content=f"""
                <html>
                    <head><title>Access Denied</title></head>
                    <body style="font-family: Arial; padding: 50px; text-align: center;">
                        <h1>🚫 Access Denied</h1>
                        <p>Your email address (<strong>{user_email}</strong>) is not authorized to access this admin interface.</p>
                        <p>Only {email_display} can access this system.</p>
                        <p>If you believe this is an error, contact the system administrator.</p>
                        <p><a href="/admin/ui">Go back</a></p>
                    </body>
                </html>
                """,
                status_code=403
            )

        # Store user info in session
        request.session['user'] = {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
        }

        # Redirect to admin UI
        return RedirectResponse(url='/admin/ui')

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Login Error</title></head>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1>❌ Login Error</h1>
                    <p>An error occurred during login: {str(e)}</p>
                    <p><a href="/admin/auth/login">Try again</a></p>
                </body>
            </html>
            """,
            status_code=400
        )


@router.get("/logout")
async def logout(request: Request):
    """
    Logout and clear session
    """
    request.session.clear()
    return RedirectResponse(url='/admin/ui')


@router.get("/me")
async def get_current_user_info(request: Request):
    """
    Get current user information (for checking auth status)
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if user is authorized
    authorized_emails = get_authorized_emails()
    if user.get('email') not in authorized_emails:
        raise HTTPException(status_code=403, detail="Not authorized")

    return user


@router.get("/authorized-users")
async def get_authorized_users(request: Request):
    """
    Get list of authorized email addresses (requires authentication)
    """
    # Verify user is authenticated
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Check if user is authorized
    authorized_emails = get_authorized_emails()
    if user.get('email') not in authorized_emails:
        raise HTTPException(status_code=403, detail="Not authorized")

    return {
        "authorized_emails": authorized_emails,
        "total": len(authorized_emails)
    }
