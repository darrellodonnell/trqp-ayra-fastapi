# Ayra TRQP Admin Guide

This guide explains how to use the Admin UI and API to manage your Trust Registry.

## Admin UI

The Admin UI provides a web-based interface for managing lookup values and entities.

### Accessing the Admin UI

1. Start the server:
   ```bash
   python3 main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/admin/ui
   ```

### Features

The Admin UI has four main tabs:

#### 1. DID Methods
Manage supported DID methods for your trust registry.

**Fields:**
- **Identifier** (required): The DID method name (e.g., `web`, `key`, `peer`, `sov`)
- **EGF DID** (optional): The Ecosystem Governance Framework DID this method applies to
- **Maximum Assurance Level** (optional): The highest assurance level this method can support
- **Description** (optional): A human-readable description

**Actions:**
- Add new DID methods
- View all DID methods
- Delete existing DID methods

#### 2. Assurance Levels
Define levels of assurance for identity verification.

**Fields:**
- **Identifier** (required): URI identifier (e.g., `urn:assurance:loa1`)
- **Name** (required): Short name (e.g., `LOA1`, `LOA2`, `LOA3`)
- **Description** (required): Detailed description of what this level means
- **EGF DID** (optional): The EGF this assurance level applies to

**Actions:**
- Add new assurance levels
- View all assurance levels
- Delete existing assurance levels

#### 3. Authorizations
Manage action+resource authorization pairs.

**Fields:**
- **Action** (required): The action being authorized (e.g., `issue`, `verify`, `revoke`)
- **Resource** (required): The resource the action applies to (e.g., `credential`, `entity`)
- **Description** (optional): What this authorization permits

**Actions:**
- Add new authorizations
- View all authorizations
- Delete existing authorizations

**Examples of Authorizations:**
- `issue` + `credential` - Authorization to issue verifiable credentials
- `verify` + `credential` - Authorization to verify credentials
- `revoke` + `credential` - Authorization to revoke credentials
- `register` + `entity` - Authorization to register new entities

#### 4. Entities
Register entities in the trust registry with their authorizations.

**Fields:**
- **Entity DID** (required): The DID URI of the entity (e.g., `did:example:entity123`)
- **Authority DID** (required): The DID of the ecosystem/authority (e.g., `did:example:ecosystem456`)
- **Name** (optional): Human-readable name of the entity
- **Type** (optional): Type of entity (`organization`, `person`, `device`, `service`)
- **Status** (required): Current status (`active`, `inactive`, `suspended`)
- **Description** (optional): Additional information about the entity
- **Authorizations**: Select one or more authorizations to grant to this entity

**Actions:**
- Add new entities with authorizations
- View all entities and their authorizations
- Delete existing entities

## Admin API

All admin functionality is available through REST API endpoints.

### Base URL
```
http://localhost:8000/admin
```

### Authentication
Currently, the admin API is open. In production, you should implement authentication and authorization.

### Endpoints

#### DID Methods

**List all DID methods**
```bash
GET /admin/did-methods

curl http://localhost:8000/admin/did-methods
```

**Create a DID method**
```bash
POST /admin/did-methods

curl -X POST http://localhost:8000/admin/did-methods \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "web",
    "egf_did": "did:example:egf123",
    "maximum_assurance_level": "LOA2",
    "description": "DID Web Method"
  }'
```

**Update a DID method**
```bash
PUT /admin/did-methods/{method_id}

curl -X PUT http://localhost:8000/admin/did-methods/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

**Delete a DID method**
```bash
DELETE /admin/did-methods/{method_id}

curl -X DELETE http://localhost:8000/admin/did-methods/1
```

#### Assurance Levels

**List all assurance levels**
```bash
GET /admin/assurance-levels

curl http://localhost:8000/admin/assurance-levels
```

**Create an assurance level**
```bash
POST /admin/assurance-levels

curl -X POST http://localhost:8000/admin/assurance-levels \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "urn:assurance:loa1",
    "name": "LOA1",
    "description": "Level of Assurance 1 - Basic identity verification",
    "egf_did": "did:example:egf123"
  }'
```

**Update an assurance level**
```bash
PUT /admin/assurance-levels/{level_id}

curl -X PUT http://localhost:8000/admin/assurance-levels/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

**Delete an assurance level**
```bash
DELETE /admin/assurance-levels/{level_id}

curl -X DELETE http://localhost:8000/admin/assurance-levels/1
```

#### Authorizations

**List all authorizations**
```bash
GET /admin/authorizations

curl http://localhost:8000/admin/authorizations
```

**Create an authorization**
```bash
POST /admin/authorizations

curl -X POST http://localhost:8000/admin/authorizations \
  -H "Content-Type: application/json" \
  -d '{
    "action": "issue",
    "resource": "credential",
    "description": "Authorization to issue verifiable credentials"
  }'
```

**Update an authorization**
```bash
PUT /admin/authorizations/{auth_id}

curl -X PUT http://localhost:8000/admin/authorizations/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

**Delete an authorization**
```bash
DELETE /admin/authorizations/{auth_id}

curl -X DELETE http://localhost:8000/admin/authorizations/1
```

#### Entities

**List all entities**
```bash
GET /admin/entities

# Optional: Filter by authority
GET /admin/entities?authority_id=did:example:ecosystem456

curl http://localhost:8000/admin/entities
```

**Get a specific entity**
```bash
GET /admin/entities/{entity_id}

curl http://localhost:8000/admin/entities/1
```

**Create an entity**
```bash
POST /admin/entities

curl -X POST http://localhost:8000/admin/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_did": "did:example:entity123",
    "authority_id": "did:example:ecosystem456",
    "name": "Example Organization",
    "entity_type": "organization",
    "status": "active",
    "description": "An example organization",
    "authorization_ids": [1, 2, 3]
  }'
```

**Update an entity**
```bash
PUT /admin/entities/{entity_id}

curl -X PUT http://localhost:8000/admin/entities/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive",
    "authorization_ids": [1, 2]
  }'
```

**Delete an entity**
```bash
DELETE /admin/entities/{entity_id}

curl -X DELETE http://localhost:8000/admin/entities/1
```

**Add an authorization to an entity**
```bash
POST /admin/entities/{entity_id}/authorizations/{auth_id}

curl -X POST http://localhost:8000/admin/entities/1/authorizations/3
```

**Remove an authorization from an entity**
```bash
DELETE /admin/entities/{entity_id}/authorizations/{auth_id}

curl -X DELETE http://localhost:8000/admin/entities/1/authorizations/3
```

## Database Management

### Database Location
By default, the application uses SQLite and stores the database in:
```
./trqp.db
```

### Initialize Database
To manually initialize or reset the database:
```bash
python init_db.py
```

This will:
1. Create all database tables
2. Seed default data (DID methods, assurance levels, authorizations)

### Change Database
To use PostgreSQL or another database, update the `DATABASE_URL` environment variable:

```bash
# In .env file or environment
DATABASE_URL=postgresql://user:password@localhost/trqp_db
```

## Workflow Examples

### Example 1: Setting Up a New Trust Registry

1. **Define Assurance Levels**
   - Go to Assurance Levels tab
   - Add LOA1, LOA2, LOA3 levels

2. **Add Supported DID Methods**
   - Go to DID Methods tab
   - Add `web`, `key`, `peer` methods

3. **Create Authorization Types**
   - Go to Authorizations tab
   - Add `issue:credential`, `verify:credential`, `revoke:credential`

4. **Register Entities**
   - Go to Entities tab
   - Add entity with DID
   - Assign relevant authorizations

### Example 2: Registering an Issuer

1. Go to Entities tab
2. Fill in:
   - Entity DID: `did:web:issuer.example.com`
   - Authority DID: `did:example:ayra-ecosystem`
   - Name: "Example Credential Issuer"
   - Type: "organization"
   - Status: "active"
3. Select authorizations:
   - ✓ issue - credential
   - ✓ revoke - credential
4. Click "Add Entity"

### Example 3: Querying Authorization (API Usage)

After registering an entity, you can query its authorization:

```bash
curl -X POST http://localhost:8000/authorization \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "did:web:issuer.example.com",
    "authority_id": "did:example:ayra-ecosystem",
    "action": "issue",
    "resource": "credential"
  }'
```

Response:
```json
{
  "entity_id": "did:web:issuer.example.com",
  "authority_id": "did:example:ayra-ecosystem",
  "action": "issue",
  "resource": "credential",
  "assertion_verified": true,
  "time_evaluated": "2025-01-15T10:30:00Z",
  "message": "Entity is authorized"
}
```

## Security Considerations

### Production Deployment

Before deploying to production:

1. **Add Authentication**
   - Implement OAuth2, JWT, or API key authentication for admin endpoints
   - Add role-based access control (RBAC)

2. **Use HTTPS**
   - Enable TLS/SSL
   - Use proper certificates

3. **Database Security**
   - Use PostgreSQL or another production database
   - Enable encryption at rest
   - Use strong passwords
   - Regular backups

4. **Rate Limiting**
   - Implement rate limiting on admin endpoints
   - Protect against brute force attacks

5. **Audit Logging**
   - Log all admin actions
   - Track who made what changes and when

6. **CORS Configuration**
   - Update CORS settings to allow only trusted domains
   - Remove wildcard (`*`) from allowed origins

## Troubleshooting

### Database Issues

**Problem**: Database file not found
```bash
# Solution: Initialize the database
python init_db.py
```

**Problem**: SQLite database locked
```bash
# Solution: Close any other connections to the database
# Or delete trqp.db and reinitialize
rm trqp.db
python init_db.py
```

### API Issues

**Problem**: 404 errors on admin endpoints
```bash
# Solution: Make sure the server is running and admin router is included
# Check that app/routers/admin.py exists
# Verify main.py includes: app.include_router(admin.router)
```

**Problem**: 422 Validation errors
```bash
# Solution: Check that required fields are provided
# Ensure DID fields start with "did:"
# Verify authorization_ids are valid integers
```

## Support

For issues and questions:
- Check the main README.md for general setup
- Review API documentation at http://localhost:8000/docs
- Open an issue on GitHub
