# Google OAuth Setup Guide

This document explains how to configure Google OAuth authentication for the Ayra TRQP Admin interface.

## Overview

The admin interface is now protected with Google OAuth authentication. Only the Google account specified in the `AUTHORIZED_EMAIL` or `AUTHORIZED_EMAILS` environment variable will be able to access the admin interface.

## Setup Instructions

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Note your project name for reference

### 2. Enable Google OAuth

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "Google Identity"
3. Click **Enable**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (for testing) or **Internal** (for organization use)
   - App name: `Ayra TRQP Admin`
   - User support email: Your email
   - Developer contact information: Your email
   - Click **Save and Continue**
   - Scopes: No need to add any scopes, click **Save and Continue**
   - Test users (if External): Add your Google account email
   - Click **Save and Continue**

4. Back in **Credentials**, click **Create Credentials** > **OAuth client ID**
5. Application type: **Web application**
6. Name: `Ayra TRQP Admin Client`

7. **Authorized redirect URIs** - Add these URLs:
   - For local development: `http://localhost:8000/admin/auth/callback`
   - For production: `https://sandbox-tr.ayra.network/admin/auth/callback`

   Replace the production example with your actual public admin domain if different.

8. Click **Create**
9. Copy the **Client ID** and **Client Secret** that appear

### 4. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set the following values:

   ```bash
   # Google OAuth Configuration
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=https://sandbox-tr.ayra.network/admin/auth/callback
   AUTHORIZED_EMAILS=user1@gmail.com,user2@gmail.com,user3@gmail.com
   SECRET_KEY=your-random-secret-key
   ```

3. **Generate a secure SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Copy the output and paste it as your `SECRET_KEY` value.

4. **Set GOOGLE_REDIRECT_URI in production** to the exact public HTTPS callback URL registered in Google Cloud Console. For local development, you can leave it unset and the app will fall back to `http://localhost:8000/admin/auth/callback`.

5. **Set AUTHORIZED_EMAILS** to a comma-separated list of Google account email addresses. Only these accounts will be able to access the admin interface.

   Examples:
   - Single user: `AUTHORIZED_EMAILS=admin@example.com`
   - Multiple users: `AUTHORIZED_EMAILS=admin@example.com,manager@example.com,developer@example.com`

   **Note:** For backward compatibility, `AUTHORIZED_EMAIL` (singular) is still supported if `AUTHORIZED_EMAILS` is not set.

### 5. Test the Configuration

1. Start the application:
   ```bash
   python main.py
   ```

2. Navigate to the admin interface:
   ```
   http://localhost:8000/admin/ui
   ```

3. You should see a login screen with "Sign in with Google" button

4. Click the button and sign in with the Google account specified in `AUTHORIZED_EMAIL`

5. After successful authentication, you should be redirected to the admin interface

## Production Deployment

### HTTPS Requirements

For production deployment with HTTPS:

1. Ensure your redirect URI in Google Cloud Console uses `https://`
2. Set `GOOGLE_REDIRECT_URI` to that same public HTTPS callback URL
3. Run uvicorn with proxy header support when the app sits behind AWS or another reverse proxy:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
   ```
4. Keep the local development callback (`http://localhost:8000/admin/auth/callback`) registered if you also use Google login locally

### Security Best Practices

1. **Never commit `.env` file** - it contains secrets
2. **Use strong SECRET_KEY** - generate a new random key for each environment
3. **Limit authorized emails** - only add trusted administrators
4. **Use HTTPS in production** - required for secure OAuth flow
5. **Regular key rotation** - rotate OAuth credentials periodically
6. **Monitor access logs** - track who accesses the admin interface

## Troubleshooting

### "Authentication not configured" error

- Check that all required environment variables are set in `.env`
- Verify the `.env` file is in the project root directory
- Restart the application after changing `.env`

### "Access Denied" after login

- Verify the email addresses in `AUTHORIZED_EMAILS` exactly match your Google accounts
- Check for typos or extra spaces in the email addresses
- Ensure the comma-separated list has no trailing commas

### "redirect_uri_mismatch" error

- The callback URL must exactly match what's configured in Google Cloud Console
- In production behind a proxy, set `GOOGLE_REDIRECT_URI` to the public HTTPS callback URL
- Check for:
  - http vs https
  - localhost vs 127.0.0.1
  - Port number (8000)
  - Trailing slashes

### Session expires immediately

- Check that `SECRET_KEY` is set and doesn't change between requests
- Verify session middleware is configured correctly
- Check browser cookie settings (must allow cookies)

## Managing Multiple Authorized Users

The system now supports multiple authorized users out of the box!

### Adding Users

Simply add email addresses to the `AUTHORIZED_EMAILS` variable in your `.env` file:

```bash
# Single user
AUTHORIZED_EMAILS=admin@example.com

# Multiple users (comma-separated, spaces are trimmed automatically)
AUTHORIZED_EMAILS=admin@example.com, manager@example.com, developer@example.com
```

### Viewing Authorized Users

Once authenticated, you can view the list of authorized users via the API:

```bash
curl -X GET http://localhost:8000/admin/auth/authorized-users \
  --cookie "admin_session=your-session-cookie"
```

Or check the application logs on startup to see the count of authorized users.

### Removing Users

To remove a user's access:

1. Edit your `.env` file and remove their email from `AUTHORIZED_EMAILS`
2. Restart the application
3. The user's existing session will be invalidated on their next request

### Best Practices

- Keep the list of authorized users minimal (only those who need admin access)
- Regularly review and audit the authorized users list
- Use a dedicated admin email address rather than personal emails when possible
- Document who has access and why in your internal documentation

## Support

For issues or questions:
- Check the FastAPI logs for error messages
- Review Google Cloud Console audit logs
- Verify OAuth consent screen configuration
- Ensure all redirect URIs are correctly configured
