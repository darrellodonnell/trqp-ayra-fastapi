# Server Startup Checklist

## Quick Configuration Test

Before starting the server, run this test to verify your OAuth configuration:

```bash
python test_auth_config.py
```

This will verify:
- ✅ GOOGLE_CLIENT_ID is loaded
- ✅ GOOGLE_CLIENT_SECRET is loaded
- ✅ SECRET_KEY is configured
- ✅ AUTHORIZED_EMAILS contains your authorized users
- ✅ Show required redirect URIs for Google Cloud Console

## Starting the Server

Once the test passes, start the server:

```bash
python main.py
```

You should see in the logs:
```
INFO - Configured 2 authorized user(s) for admin access
```

## Accessing the Application

### Public API
- Swagger UI: http://localhost:8000/docs
- Public endpoints: http://localhost:8000/

### Admin Interface
- Admin UI: http://localhost:8000/admin/ui
- Admin API Docs: http://localhost:8000/admin/docs

**Production URL:** https://sandbox-tr.ayra.technology/admin/ui

## Authorized Users

Currently configured users:
1. darrell.odonnell@ayra.forum
2. sheldon.regular@gmail.com

## Google Cloud Console Setup

Ensure your OAuth 2.0 Client has these redirect URIs configured:

**Development:**
```
http://localhost:8000/admin/auth/callback
```

**Production:**
```
https://sandbox-tr.ayra.technology/admin/auth/callback
```

To update redirect URIs:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** > **Credentials**
3. Click on your OAuth 2.0 Client ID: `128426268918-uqcq6pet5mbrd1g4hma4b7vijldhi62c`
4. Add/verify the redirect URIs above
5. Click **Save**

## Troubleshooting

### "Authentication Not Configured" Error

**Solution:** The `.env` file is now loaded automatically in `main.py`. Just restart the server.

**Verification:**
```bash
python test_auth_config.py
```

### "redirect_uri_mismatch" Error

**Cause:** The redirect URI in your request doesn't match what's configured in Google Cloud Console.

**Solution:**
- Check that both URIs are configured (local + production)
- Ensure no typos or trailing slashes
- Verify the correct Client ID is being used

### "Access Denied" After Login

**Cause:** Your Google account is not in the `AUTHORIZED_EMAILS` list.

**Solution:**
1. Edit `.env` file
2. Add your email to `AUTHORIZED_EMAILS` (comma-separated)
3. Restart the server

### Session Expires Immediately

**Cause:** `SECRET_KEY` is changing between requests or not set.

**Solution:**
- Verify `SECRET_KEY` is set in `.env`
- Ensure it's not the default placeholder value
- Restart the server after changing

## Adding New Authorized Users

1. Edit `.env` file:
   ```bash
   AUTHORIZED_EMAILS=darrell.odonnell@ayra.forum,sheldon.regular@gmail.com,new-user@example.com
   ```

2. Restart the server:
   ```bash
   # Stop current server (Ctrl+C)
   python main.py
   ```

3. Verify in logs:
   ```
   INFO - Configured 3 authorized user(s) for admin access
   ```

## Security Reminders

- ✅ `.env` file is in `.gitignore` (never commit secrets)
- ✅ `SECRET_KEY` is a random secure value
- ✅ HTTPS is required for production (`https_only=True` in production)
- ✅ Only necessary users have admin access
- ✅ OAuth credentials are from Google Cloud Console
- ⚠️  Regularly review and audit authorized users
- ⚠️  Rotate OAuth credentials periodically

## Quick Commands

```bash
# Test configuration
python test_auth_config.py

# Start server
python main.py

# Check logs for auth configuration
# Should see: "Configured X authorized user(s) for admin access"

# View authorized users (requires authentication)
curl -X GET http://localhost:8000/admin/auth/authorized-users \
  --cookie "admin_session=your-session"
```

## Support

For issues or questions, see:
- [OAUTH_SETUP.md](OAUTH_SETUP.md) - Detailed setup guide
- [AUTHENTICATION_SUMMARY.md](AUTHENTICATION_SUMMARY.md) - Implementation details
