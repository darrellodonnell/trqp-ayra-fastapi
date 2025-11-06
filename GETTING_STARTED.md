# Getting Started with Ayra TRQP Admin

Welcome! This guide will help you get up and running with the Trust Registry management system.

## What Can You Do?

This system allows you to:

1. **Manage DID Methods** - Define which DID methods (web, key, peer, etc.) your trust registry supports
2. **Define Assurance Levels** - Set up identity verification levels (LOA1, LOA2, LOA3, etc.)
3. **Create Authorizations** - Define what actions can be performed on what resources (e.g., "issue" a "credential")
4. **Register Entities** - Add entities (organizations, people) and grant them specific authorizations

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Initialize the Database

```bash
python init_db.py
```

This creates a SQLite database with example data.

### Step 3: Start the Server

```bash
python -m app.main
```

### Step 4: Open the Admin UI

Navigate to: **http://localhost:8000/admin-ui**

## Your First Entity Registration

Let's walk through registering a credential issuer:

### 1. Create an Authorization (if not already exists)

- Go to the **Authorizations** tab
- Fill in:
  - Action: `issue`
  - Resource: `credential`
  - Description: `Can issue verifiable credentials`
- Click **Add Authorization**

### 2. Register the Entity

- Go to the **Entities** tab
- Fill in:
  - Entity DID: `did:web:issuer.example.com`
  - Authority DID: `did:example:ayra-ecosystem`
  - Name: `Example Credential Issuer`
  - Type: `organization`
  - Status: `active`
- Check the box for `issue - credential` under Authorizations
- Click **Add Entity**

### 3. Test the Authorization

Open a terminal and run:

```bash
curl -X POST "http://localhost:8000/authorization" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "did:web:issuer.example.com",
    "authority_id": "did:example:ayra-ecosystem",
    "action": "issue",
    "resource": "credential"
  }'
```

Note: The TRQP core endpoints (POST /authorization and POST /recognition) currently return stub responses. You'll need to update [app/routers/trqp_core.py](app/routers/trqp_core.py) to connect them to the database using the CRUD operations in [app/crud.py](app/crud.py).

## Understanding the UI

### DID Methods Tab
Lists all supported DID methods. The default installation includes:
- `web` - DID Web Method
- `key` - DID Key Method
- `peer` - DID Peer Method
- `sov` - Sovrin DID Method

### Assurance Levels Tab
Identity verification levels. Defaults include:
- **LOA1** - Basic identity verification
- **LOA2** - Enhanced verification with documents
- **LOA3** - High assurance with in-person verification

### Authorizations Tab
Action+Resource pairs that define what entities can do. Defaults include:
- `issue:credential` - Can issue credentials
- `verify:credential` - Can verify credentials
- `revoke:credential` - Can revoke credentials
- `register:entity` - Can register new entities

### Entities Tab
Registered entities with their authorizations. Initially empty - you add entities here!

## Using the REST API

All admin functionality is available via REST API:

### List Entities
```bash
curl http://localhost:8000/admin/entities
```

### Add an Entity via API
```bash
curl -X POST http://localhost:8000/admin/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_did": "did:web:verifier.example.com",
    "authority_id": "did:example:ayra-ecosystem",
    "name": "Example Verifier",
    "entity_type": "organization",
    "status": "active",
    "authorization_ids": [2]
  }'
```

### Update an Entity
```bash
curl -X PUT http://localhost:8000/admin/entities/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive"
  }'
```

### Delete an Entity
```bash
curl -X DELETE http://localhost:8000/admin/entities/1
```

## Database

The system uses SQLite by default, storing data in `trqp.db`.

### View the Database

```bash
sqlite3 trqp.db
sqlite> .tables
sqlite> SELECT * FROM entities;
sqlite> .quit
```

### Reset the Database

```bash
rm trqp.db
python init_db.py
```

### Use PostgreSQL Instead

1. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/trqp_db
   ```

2. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

3. Restart the server

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the Swagger UI!

## Common Use Cases

### Use Case 1: University Issuing Diplomas

1. Add authorization: `issue` + `diploma`
2. Register university:
   - Entity DID: `did:web:university.edu`
   - Grant `issue:diploma` authorization
3. University can now issue diplomas (verified via TRQP queries)

### Use Case 2: Employer Verifying Credentials

1. Add authorization: `verify` + `credential`
2. Register employer:
   - Entity DID: `did:web:employer.com`
   - Grant `verify:credential` authorization
3. Employer can verify credentials from authorized issuers

### Use Case 3: Multi-Level Issuers

1. Add authorizations:
   - `issue:basic-credential`
   - `issue:advanced-credential`
2. Register two entities:
   - Basic Issuer: only `issue:basic-credential`
   - Advanced Issuer: both authorizations
3. Control what each entity can issue

## Troubleshooting

### Port Already in Use
```bash
# Change the port
uvicorn app.main:app --port 8001
```

### Database Errors
```bash
# Reset database
rm trqp.db
python init_db.py
```

### Can't Access Admin UI
Make sure:
1. Server is running: `python -m app.main`
2. Navigate to: `http://localhost:8000/admin-ui` (note the dash)
3. Check console for errors

### Authorization Not Working
Remember: The TRQP POST endpoints are still stubs. You need to:
1. Open [app/routers/trqp_core.py](app/routers/trqp_core.py)
2. Replace stub logic with database queries using `crud.check_entity_authorization()`

## Next Steps

1. **Read the Admin Guide**: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for comprehensive documentation
2. **Explore the Code**: Check out the well-commented source files
3. **Test TRQP Queries**: Use the `/authorization` and `/recognition` endpoints
4. **Add Authentication**: Secure your admin endpoints for production
5. **Deploy**: Consider Docker, Kubernetes, or cloud platforms

## Support

- **General Setup**: See [README.md](README.md)
- **Admin Details**: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- **API Docs**: http://localhost:8000/docs
- **Issues**: Open a GitHub issue

## Summary

You now have a fully functional Trust Registry management system with:

✅ Web UI for easy management
✅ REST API for programmatic access
✅ SQLite database (easily swappable)
✅ TRQP-compliant endpoints
✅ Pre-seeded example data

Happy managing! 🎉
