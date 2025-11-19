 
# Ayra TRQP Profile API - FastAPI Implementation

A FastAPI implementation of the Trust Registry Query Protocol (TRQP) 2.0 for the Ayra Trust Network.

## Overview

This project provides a RESTful API harness implementing the Ayra TRQP Profile specification. It includes:

- TRQP 2.0 compliant core query endpoints
- Ayra-specific extensions for entity and ecosystem management
- Lookup endpoints for assurance levels, authorizations, and DID methods
- Full OpenAPI/Swagger documentation
- **Admin UI and API for managing lookup values and entities**
- **SQLite database with full CRUD operations**

## Features

### TRQP Core Endpoints
- `POST /recognition` - Query ecosystem recognition of another trust registry
- `POST /authorization` - Query entity authorization within an ecosystem

### Ayra Extension Endpoints
- `GET /metadata` - Retrieve Trust Registry metadata
- `GET /entities/{entity_id}` - Get specific entity information
- `GET /entities/{entity_did}/authorizations` - List entity authorizations
- `GET /ecosystems/{ecosystem_did}/recognitions` - List recognized ecosystems

### Lookup Endpoints
- `GET /lookups/assuranceLevels` - Lookup supported assurance levels
- `GET /lookups/authorizations` - Lookup available authorizations
- `GET /lookups/didMethods` - Lookup supported DID methods

### Admin Features (NEW!)
- **Web-based Admin UI** at `/admin-ui` for managing:
  - DID Methods
  - Assurance Levels
  - Authorizations (action+resource pairs)
  - Entities with their authorizations
- **Admin REST API** at `/admin/*` with full CRUD operations
- **SQLite Database** for persistent storage (easily swappable to PostgreSQL)

## Project Structure

```
trqp-ayra-fastapi/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main FastAPI application
│   ├── models.py             # Pydantic models for all schemas
│   ├── database.py           # Database models and configuration
│   ├── crud.py               # CRUD operations
│   ├── static/
│   │   └── admin.html        # Admin UI
│   └── routers/
│       ├── __init__.py
│       ├── trqp_core.py      # TRQP core endpoints
│       ├── ayra_extension.py # Ayra extension endpoints
│       ├── lookup.py         # Lookup endpoints
│       └── admin.py          # Admin API endpoints
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration example
├── init_db.py               # Database initialization script
├── ADMIN_GUIDE.md           # Comprehensive admin documentation
└── README.md                # This file
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd trqp-ayra-fastapi
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip3 install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

### 1. Run the Application

The application automatically initializes the database on startup.

**Development Mode** (with auto-reload):
```bash
python3 main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Access the Application

The application runs two separate APIs:

#### Public TRQP API (Root level)
- **Landing Page**: http://localhost:8000/welcome
- **API Root**: http://localhost:8000/
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

#### Admin API (Under /admin)
- **Admin UI**: http://localhost:8000/admin/ui 🆕
- **Admin API Root**: http://localhost:8000/admin/
- **Swagger UI**: http://localhost:8000/admin/docs
- **ReDoc**: http://localhost:8000/admin/redoc
- **OpenAPI Spec**: http://localhost:8000/admin/openapi.json

### Database Initialization

The database is automatically initialized on first run with:
- 4 DID Methods (web, key, peer, webvh)
- 3 Assurance Levels (LOA1, LOA2, LOA3)
- Sample Authorizations and Recognitions
- Default Trust Registry Configuration

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs - Interactive API documentation
- **ReDoc**: http://localhost:8000/redoc - Alternative documentation view

## Usage Examples

### Query Recognition

```bash
curl -X POST "http://localhost:8000/recognition" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "did:example:trustregistry123",
    "authority_id": "did:example:ecosystem456",
    "action": "recognize",
    "resource": "trust_registry",
    "context": {
      "time": "2025-01-15T10:00:00Z"
    }
  }'
```

### Query Authorization

```bash
curl -X POST "http://localhost:8000/authorization" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "did:example:entity123",
    "authority_id": "did:example:ecosystem456",
    "action": "issue",
    "resource": "credential",
    "context": {}
  }'
```

### Get Trust Registry Metadata

```bash
curl -X GET "http://localhost:8000/metadata?egf_did=did:example:egf789"
```

### Lookup Authorizations

```bash
curl -X GET "http://localhost:8000/lookups/authorizations?ecosystem_did=did:example:ecosystem456"
```

### Lookup DID Methods

```bash
curl -X GET "http://localhost:8000/lookups/didMethods?ecosystem_did=did:example:ecosystem456"
```

## Admin Management

### Using the Admin UI

1. Start the server and navigate to http://localhost:8000/admin/ui
2. Use the tabbed interface to manage:
   - **DID Methods**: Add/remove supported DID methods
   - **Assurance Levels**: Define identity verification levels
   - **Authorizations**: Create action+resource pairs
   - **Recognitions**: Define recognition types for cross-ecosystem trust
   - **Entities**: Register entities with their authorizations and recognitions

### Example Workflow

1. **Add an Authorization:**
   - Go to "Authorizations" tab
   - Action: `issue`
   - Resource: `credential`
   - Description: "Authorization to issue credentials"

2. **Register an Entity:**
   - Go to "Entities" tab
   - Entity DID: `did:web:issuer.example.com`
   - Authority DID: `did:example:ecosystem456`
   - Select the "issue:credential" authorization
   - Status: active
   - Click "Add Entity"

3. **Query Authorization:**
   ```bash
   curl -X POST "http://localhost:8000/authorization" \
     -H "Content-Type: application/json" \
     -d '{
       "entity_id": "did:web:issuer.example.com",
       "authority_id": "did:example:ecosystem456",
       "action": "issue",
       "resource": "credential"
     }'
   ```

For detailed admin documentation, see [ADMIN_GUIDE.md](ADMIN_GUIDE.md).

## Implementation Status

✅ **Implemented**:
- SQLite database with full CRUD operations
- Admin UI for managing lookup values and entities
- Admin REST API endpoints
- Lookup endpoints using database
- Database seeding with default data

🚧 **To Do for Production**:
1. **Add Authentication**: Implement OAuth2, JWT, or other auth mechanisms for admin endpoints
2. **Configure CORS**: Update CORS settings for your production domains
3. **Use Production Database**: Switch from SQLite to PostgreSQL
4. **Add Validation**: Implement DID validation and resolution
5. **Add Caching**: Consider Redis or similar for performance
6. **Error Handling**: Enhance error handling and logging
7. **Testing**: Add unit tests, integration tests, and e2e tests
8. **Update TRQP Core**: Connect authorization/recognition queries to database

## Development

### Adding New Endpoints

1. Define Pydantic models in [app/models.py](app/models.py)
2. Create router in `app/routers/`
3. Include router in [app/main.py](app/main.py)

### Environment Variables

See [.env.example](.env.example) for available configuration options.

## Specification

This implementation follows the Ayra TRQP Profile specification:
https://github.com/ayraforum/ayra-trust-registry-resources/blob/main/trqp_ayra_profile_swagger.yaml

## License

See [LICENSE](LICENSE) file for details.

## TODO

* ✅ ~~Attach a back-end with real data to support sandbox use~~
* ✅ ~~Add database integration (PostgreSQL/MongoDB)~~
* Implement authentication and authorization for admin endpoints
* Add unit and integration tests
* Add Docker containerization
* Add CI/CD pipeline
* Implement DID resolution
* Add rate limiting
* Add API versioning strategy
* Add monitoring and metrics (Prometheus/Grafana)
* Connect TRQP core endpoints to database queries
* Add audit logging for admin operations

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions, please open an issue on GitHub.