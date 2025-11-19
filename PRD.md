# Product Requirements Document (PRD)
## Ayra TRQP Trust Registry

**Version:** 1.0
**Last Updated:** November 14, 2025
**Product:** Ayra Trust Registry Query Protocol (TRQP) Implementation

---

## 1. Executive Summary

The Ayra TRQP Trust Registry is a FastAPI-based implementation of the Trust Registry Query Protocol (TRQP) 2.0 specification. It provides a complete solution for managing decentralized trust relationships between ecosystems, organizations, and entities using Decentralized Identifiers (DIDs). The system supports both **authorizations** (what entities can do) and **recognitions** (which ecosystems recognize other registries).

### Key Features
- **TRQP 2.0 Compliance**: Full implementation of authorization and recognition query endpoints
- **Entity Management**: Support for ecosystems, organizations, persons, devices, and services
- **Authorization System**: Flexible action+resource permission model
- **Recognition System**: Cross-ecosystem recognition with temporal validity
- **Admin UI**: Modern web interface for complete registry management
- **DID Support**: Multiple DID methods (web, webvh, key, peer)
- **Hierarchical Trust**: Root ecosystems, child ecosystems, and governed entities

---

## 2. Product Overview

### 2.1 Purpose
Enable trust registry operators to:
- Manage entities in a trust network
- Define and assign authorizations
- Configure cross-ecosystem recognitions
- Query trust relationships programmatically
- Support verifiable credential ecosystems

### 2.2 Target Users
1. **Trust Registry Administrators**: Configure and manage registry data
2. **Ecosystem Operators**: Define governance rules and recognitions
3. **API Consumers**: Query trust relationships for credential verification
4. **Developers**: Integrate trust registry into verifiable credential workflows

---

## 3. Core Components

### 3.1 Database Architecture

#### 3.1.1 Entities Table
**Purpose**: Store all registered entities in the trust network

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `entity_did` | String | Unique DID identifier |
| `authority_id` | String (nullable) | DID of governing ecosystem (null for root ecosystems) |
| `name` | String | Human-readable name |
| `entity_type` | String | Type: ecosystem, organization, person, device, service |
| `status` | String | Status: active, inactive, suspended |
| `description` | Text | Optional description |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Relationships:**
- Many-to-many with Authorizations via `entity_authorizations`
- Many-to-many with Recognitions via `entity_recognitions` (ecosystems only)

#### 3.1.2 Authorizations Table
**Purpose**: Define action+resource permission types

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `action` | String | Action verb (e.g., "issue", "verify", "revoke") |
| `resource` | String | Resource identifier (e.g., "credential", "ayracard:businesscard") |
| `description` | Text | Optional description |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Examples:**
- `[issue] ayracard:businesscard` - Can issue Ayra Business Cards
- `[manage-issuers] ayracard:businesscard` - Can manage who issues Business Cards
- `[root] ayracard` - Root authority for entire Ayra Card system

#### 3.1.3 Recognitions Table
**Purpose**: Define recognition types for cross-ecosystem trust

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `action` | String | Recognition action (e.g., "recognize") |
| `resource` | String | What is recognized (e.g., "credential", "ecosystem") |
| `description` | Text | Optional description |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Examples:**
- `[recognize] credential` - Recognize credentials from other ecosystems
- `[recognize] ecosystem` - Recognize other ecosystems and their governance
- `[recognize] entity` - Recognize entities from other registries

#### 3.1.4 Entity Authorizations (Join Table)
**Purpose**: Link entities to their authorizations

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | Integer | Foreign key to entities |
| `authorization_id` | Integer | Foreign key to authorizations |

#### 3.1.5 Entity Recognitions (Association Table)
**Purpose**: Link ecosystems to their recognitions with temporal validity

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | Integer | Foreign key to entities (must be ecosystem) |
| `recognition_id` | Integer | Foreign key to recognitions |
| `recognized_registry_did` | String | DID of recognized registry |
| `recognized` | Boolean | True if recognized, false if explicitly not recognized |
| `valid_from` | DateTime (nullable) | Recognition start date |
| `valid_until` | DateTime (nullable) | Recognition expiration date |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

#### 3.1.6 DID Methods Table
**Purpose**: Track supported DID methods

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `identifier` | String | Method identifier (e.g., "web", "webvh", "key") |
| `egf_did` | String | Ecosystem Governance Framework DID |
| `maximum_assurance_level` | String | Max assurance level for this method |
| `description` | Text | Method description |

**Supported Methods:**
- `web` - DID Web Method
- `webvh` - DID Web Verifiable History (high-assurance)
- `key` - DID Key Method
- `peer` - DID Peer Method

#### 3.1.7 Assurance Levels Table
**Purpose**: Define identity verification levels

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `identifier` | String | URN identifier (e.g., "urn:assurance:loa1") |
| `name` | String | Short name (e.g., "LOA1") |
| `egf_did` | String | Ecosystem Governance Framework DID |
| `description` | Text | Level description |

**Standard Levels:**
- **LOA1**: Basic identity verification
- **LOA2**: Enhanced verification with document validation
- **LOA3**: High assurance with in-person verification

#### 3.1.8 Registry Configuration Tables

**Trust Registry Config:**
- `ecosystem_did`: DID of the ecosystem
- `trustregistry_did`: DID of the trust registry
- `egf_did`: Ecosystem Governance Framework DID
- `name`: Registry name
- `description`: Registry description
- `controllers`: JSON array of controller DIDs

**Registry Config (Admin UI):**
- `authority_id`: Default authority DID
- `egf_id`: Default EGF DID
- `name`: Registry name
- `description`: Registry description

---

## 4. API Architecture

### 4.1 Dual-API Design

The system implements a **dual-API architecture** with strict separation between public and internal endpoints:

#### 4.1.1 Public TRQP API (Root Level)
**Base Path:** `/`
**Purpose:** Public-facing API for querying trust relationships
**Documentation:** `/docs`, `/redoc`
**Security:** Read-only, rate-limited (production)

**Includes:**
- TRQP Core endpoints (`/authorization`, `/recognition`)
- Ayra Extension endpoints (`/metadata`, `/entities`)
- Lookup endpoints (`/lookups/*`)
- Health checks

**Consumers:** Verifiers, relying parties, credential wallets

#### 4.1.2 Admin API (Mounted at /admin)
**Base Path:** `/admin`
**Purpose:** Internal management and configuration
**Documentation:** `/admin/docs`, `/admin/redoc`
**Security:** ⚠️ **MUST** be protected with authentication in production

**Includes:**
- Admin UI (`/admin/ui`)
- Entity CRUD operations (`/admin/entities/*`)
- Authorization management (`/admin/authorizations/*`)
- Recognition management (`/admin/recognitions/*`)
- DID method configuration (`/admin/did-methods/*`)
- Assurance level configuration (`/admin/assurance-levels/*`)
- Registry configuration (`/admin/registry-config/*`)

**Consumers:** Trust registry administrators, ecosystem operators

### 4.2 OpenAPI Specifications

Each API maintains its own **separate OpenAPI/Swagger documentation**:

**Public API:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Admin API:**
- Swagger UI: `http://localhost:8000/admin/docs`
- ReDoc: `http://localhost:8000/admin/redoc`
- OpenAPI JSON: `http://localhost:8000/admin/openapi.json`

### 4.3 Deployment Considerations

**Production Deployment:**
1. **Public API** - Deploy to public internet with:
   - Rate limiting (e.g., 100 req/min per IP)
   - Caching (Redis/CloudFlare)
   - CDN distribution
   - DDoS protection

2. **Admin API** - Deploy with restricted access:
   - ✅ **REQUIRED**: API key or OAuth2 authentication
   - ✅ **REQUIRED**: IP whitelisting or VPN access
   - ✅ **REQUIRED**: Audit logging for all changes
   - ✅ **RECOMMENDED**: Role-based access control (RBAC)
   - ✅ **RECOMMENDED**: Admin UI only accessible via internal network

**Security Warning:** The admin API provides full CRUD access to trust registry data. In production, it **MUST NOT** be exposed to the public internet without robust authentication and authorization controls.

---

## 5. API Endpoints

### 5.1 TRQP Core Endpoints

#### 5.1.1 POST /authorization
**Purpose**: Query if an entity has authorization for an action+resource

**Request Body:**
```json
{
  "entity_id": "did:web:example.com",
  "authority_id": "did:webvh:SCID-ATN:ayra.forum",
  "action": "issue",
  "resource": "credential",
  "context": {}
}
```

**Response:**
```json
{
  "entity_id": "did:web:example.com",
  "authority_id": "did:webvh:SCID-ATN:ayra.forum",
  "action": "issue",
  "resource": "credential",
  "assertion_verified": true,
  "time_requested": "2025-01-01T00:00:00Z",
  "time_evaluated": "2025-01-01T00:00:05Z",
  "message": "Authorization verified successfully",
  "context": {}
}
```

#### 5.1.2 POST /recognition
**Purpose**: Query if an ecosystem recognizes another registry for an action+resource

**Request Body:**
```json
{
  "entity_id": "did:web:external-registry.com",
  "authority_id": "did:webvh:SCID-ATN:ayra.forum",
  "action": "recognize",
  "resource": "ecosystem",
  "context": {}
}
```

**Response:**
```json
{
  "entity_id": "did:web:external-registry.com",
  "authority_id": "did:webvh:SCID-ATN:ayra.forum",
  "action": "recognize",
  "resource": "ecosystem",
  "recognized": true,
  "time_requested": null,
  "time_evaluated": "2025-01-01T00:00:05Z",
  "message": "Ecosystem recognizes registry",
  "context": {}
}
```

**Features:**
- Temporal validity checking (valid_from/valid_until)
- Only active ecosystems can provide recognitions
- Returns meaningful error messages

### 5.2 Admin API Endpoints

#### 5.2.1 Entity Management

**GET /admin/entities**
- List all entities with their authorizations
- Returns array of entity objects

**POST /admin/entities**
- Create new entity
- Body: `entity_did`, `authority_id`, `name`, `entity_type`, `status`, `description`, `authorization_ids`

**GET /admin/entities/{id}**
- Get specific entity by ID

**PUT /admin/entities/{id}**
- Update entity
- Can update all fields including authorization assignments

**DELETE /admin/entities/{id}**
- Delete entity

**GET /admin/entities/active-authorities**
- List all active ecosystem entities for use as authorities

#### 4.2.2 Authorization Management

**GET /admin/authorizations**
- List all authorization types

**POST /admin/authorizations**
- Create new authorization type
- Body: `action`, `resource`, `description`

**PUT /admin/authorizations/{id}**
- Update authorization

**DELETE /admin/authorizations/{id}**
- Delete authorization

**POST /admin/entities/{entity_id}/authorizations/{auth_id}**
- Add authorization to entity

**DELETE /admin/entities/{entity_id}/authorizations/{auth_id}**
- Remove authorization from entity

#### 4.2.3 Recognition Management

**GET /admin/recognitions**
- List all recognition types

**POST /admin/recognitions**
- Create new recognition type
- Body: `action`, `resource`, `description`

**PUT /admin/recognitions/{id}**
- Update recognition

**DELETE /admin/recognitions/{id}**
- Delete recognition

**GET /admin/entities/{entity_id}/recognitions**
- List all recognitions for an ecosystem
- Returns recognition details including temporal validity

**POST /admin/entities/{entity_id}/recognitions**
- Add recognition to ecosystem
- Body: `entity_id`, `recognition_id`, `recognized_registry_did`, `recognized`, `valid_from`, `valid_until`

**DELETE /admin/entities/{entity_id}/recognitions/{recognition_id}**
- Remove recognition from ecosystem
- Query param: `recognized_registry_did`

#### 4.2.4 DID Methods Management

**GET /admin/did-methods**
- List all DID methods

**POST /admin/did-methods**
- Create DID method

**PUT /admin/did-methods/{id}**
- Update DID method

**DELETE /admin/did-methods/{id}**
- Delete DID method

#### 4.2.5 Assurance Levels Management

**GET /admin/assurance-levels**
- List all assurance levels

**POST /admin/assurance-levels**
- Create assurance level

**PUT /admin/assurance-levels/{id}**
- Update assurance level

**DELETE /admin/assurance-levels/{id}**
- Delete assurance level

#### 4.2.6 Registry Configuration

**GET /admin/registry-config**
- Get registry configuration

**POST /admin/registry-config**
- Create or update registry config

### 4.3 Ayra Extension Endpoints

**GET /metadata**
- Return TRQP metadata about the registry

**GET /entities**
- List entities with pagination
- Query params: `page`, `limit`

**GET /ecosystems/{ecosystem_did}/recognitions**
- List recognized ecosystems for a governance framework
- Returns array of recognition relationships

---

## 6. Admin User Interface

### 6.1 Overview
Modern, responsive web interface accessible at `/admin/ui`

**Design Principles:**
- Clean, professional gradient design (purple to pink)
- Card-based layout with shadows
- Tabbed navigation
- Real-time feedback with success/error alerts
- Mobile-responsive

### 6.2 Navigation Tabs

1. **🏢 Entities** - Manage all entities
2. **✅ Authorizations** - Manage authorization types
3. **🤝 Recognitions** - Manage recognition types
4. **⚙️ Registry Config** - Configure registry settings
5. **🔑 DID Methods** - Manage supported DID methods
6. **🛡️ Assurance Levels** - Manage assurance levels

### 6.3 Entities Tab

#### 6.3.1 Add Entity Form
**Fields:**
- Entity DID (required)
- Authority DID (dropdown of active ecosystems, optional for root ecosystems)
- Name
- Entity Type (dropdown: ecosystem, organization, person, device, service)
- Status (dropdown: active, inactive, suspended)
- Description

**Features:**
- Form validation
- Authority dropdown auto-populated from active ecosystems
- Success/error alerts

#### 6.3.2 Entity Table
**Columns:**
- Entity DID
- Name
- Authority DID (shows "*Root*" for null values)
- Type
- Status (color-coded badge)
- Authorizations (list of action+resource pairs, compact display)
- **Recognitions** (for ecosystems only, shows recognized registries)
- Actions (buttons)

**Action Buttons:**
- **Edit** - Update entity details
- **Authorizations** - Manage entity authorizations (modal)
- **Recognitions** - Manage ecosystem recognitions (modal, ecosystems only)
- **Delete** - Remove entity

**Recognition Display:**
- Shows `[action] resource → recognized_registry_did`
- Truncates DID to 25 characters
- Full DID visible on hover (tooltip)
- Shows "None" in gray for ecosystems without recognitions
- Shows "-" for non-ecosystem entities

#### 6.3.3 Authorization Modal
**Purpose**: Manage authorizations for an entity

**Sections:**
- **Current Authorizations**: List with Remove buttons
- **Available Authorizations**: List with Add buttons

**Features:**
- Real-time updates
- Prevents duplicate assignments
- Shows only available/unassigned authorizations

#### 6.3.4 Recognition Modal (Ecosystems Only)
**Purpose**: Manage recognitions for an ecosystem

**Sections:**
- **Current Recognitions**: List with details and Remove buttons
  - Shows: `[action] resource`
  - Registry: `recognized_registry_did`
  - Valid from/until dates (if set)
- **Add New Recognition**: Form to add recognition

**Add Recognition Form:**
- Recognition Type (dropdown, auto-populated)
- Recognized Registry DID (text input)
- Valid From (datetime picker, optional)
- Valid Until (datetime picker, optional)

**Features:**
- Only accessible for ecosystem entities
- Supports temporal validity
- ISO 8601 datetime formatting
- Real-time updates after add/remove

#### 5.3.5 Edit Entity Modal
**Purpose**: Update entity details

**Fields:**
- All entity fields editable
- Authority dropdown with active ecosystems
- Save/Cancel buttons

### 6.4 Authorizations Tab

#### 5.4.1 Add Authorization Form
**Fields:**
- Action (required, e.g., "issue", "verify", "revoke")
- Resource (required, e.g., "credential", "ayracard:businesscard")
- Description (optional)

**Features:**
- Creates action+resource permission types
- Used across all entities

#### 5.4.2 Authorization List
**Display:**
- `[action] / resource`
- Description
- Delete button

**Examples:**
- `[issue] / ayracard:businesscard` - Can issue Ayra Business Cards
- `[manage-issuers] / ayracard:businesscard` - Can manage Business Card issuers
- `[root] / ayracard` - Root authority for Ayra Card system

### 6.5 Recognitions Tab

#### 5.5.1 Add Recognition Type Form
**Fields:**
- Action (required, e.g., "recognize")
- Resource (required, e.g., "credential", "ecosystem", "entity")
- Description (optional)

**Info Message:**
"Recognition types define what ecosystems can recognize about other registries."

#### 5.5.2 Recognition Types List
**Display:**
- `[action] / resource`
- Description
- Delete button

**Examples:**
- `[recognize] / credential` - Recognition of credentials from other ecosystems
- `[recognize] / ecosystem` - Recognition of other ecosystems and governance
- `[recognize] / entity` - Recognition of entities from other registries

### 6.6 Registry Config Tab

**Fields:**
- Authority ID (default authority DID)
- EGF ID (Ecosystem Governance Framework DID)
- Name (registry name)
- Description

**Features:**
- Single configuration record
- Pre-populated with defaults
- Save button with validation

### 6.7 DID Methods Tab

**Management of supported DID methods:**
- Identifier (e.g., "web", "webvh", "key", "peer")
- EGF DID
- Maximum Assurance Level
- Description

### 5.8 Assurance Levels Tab

**Management of identity verification levels:**
- Identifier (URN format)
- Name (short name like "LOA1")
- EGF DID
- Description

---

## 7. Use Cases

### 7.1 Basic Entity Management

**Scenario**: Register a new organization in an ecosystem

**Steps:**
1. Admin opens Entities tab
2. Fills in Add Entity form:
   - Entity DID: `did:web:newcompany.com`
   - Authority: `did:webvh:SCID-ATN:ayra.forum`
   - Name: "New Company"
   - Type: "organization"
   - Status: "active"
3. Clicks "Add Entity"
4. Entity appears in table

### 7.2 Granting Authorization

**Scenario**: Allow an organization to issue credentials

**Steps:**
1. Admin finds entity in Entities tab
2. Clicks "Authorizations" button
3. Modal opens showing current/available authorizations
4. Clicks "Add" on `[issue] credential` authorization
5. Authorization added immediately
6. Modal updates to show new current authorization

### 7.3 Cross-Ecosystem Recognition

**Scenario**: Ayra Trust Network recognizes Bubba Group Ecosystem

**Steps:**
1. Admin finds "Ayra Trust Network" entity (ecosystem type)
2. Clicks "Recognitions" button
3. Modal opens with recognition management
4. Fills in Add Recognition form:
   - Recognition Type: `[recognize] ecosystem`
   - Recognized Registry DID: `did:web:bubbagroup.com`
   - Valid From: `2025-01-01T00:00:00`
   - Valid Until: `2026-01-01T00:00:00`
5. Clicks "Add Recognition"
6. Recognition appears in current recognitions list
7. Recognition also shows in Entities table

### 7.4 Querying Authorization (API)

**Scenario**: Verify if an entity can issue a specific credential

**API Call:**
```bash
curl -X POST https://registry.ayra.forum/authorization \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "did:web:issuer.com",
    "authority_id": "did:webvh:SCID-ATN:ayra.forum",
    "action": "issue",
    "resource": "ayracard:businesscard"
  }'
```

**Response:**
```json
{
  "assertion_verified": true,
  "message": "Entity is authorized"
}
```

### 7.5 Querying Recognition (API)

**Scenario**: Check if an ecosystem recognizes another registry

**API Call:**
```bash
curl -X POST https://registry.ayra.forum/recognition \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "did:web:external-registry.com",
    "authority_id": "did:webvh:SCID-ATN:ayra.forum",
    "action": "recognize",
    "resource": "ecosystem"
  }'
```

**Response:**
```json
{
  "recognized": true,
  "message": "Ecosystem recognizes registry"
}
```

### 7.6 Hierarchical Trust Setup

**Scenario**: Create a root ecosystem with child ecosystems

**Steps:**
1. Create root ecosystem:
   - DID: `did:webvh:SCID-ATN:ayra.forum`
   - Authority: *None* (null for root)
   - Type: "ecosystem"
   - Add `[root] ayracard` authorization

2. Create child ecosystem:
   - DID: `did:web:bubbagroup.com`
   - Authority: `did:webvh:SCID-ATN:ayra.forum`
   - Type: "ecosystem"
   - Add `[manage-issuers] ayracard:businesscard` authorization

3. Create organization under child ecosystem:
   - DID: `did:web:bubbabank.com`
   - Authority: `did:web:bubbagroup.com`
   - Type: "organization"
   - Add `[issue] ayracard:businesscard` authorization

**Result**: Three-tier hierarchy with delegated authorities

---

## 8. Data Models (Pydantic)

### 8.1 Core TRQP Models

```python
class TrqpAuthorizationQuery(BaseModel):
    entity_id: str
    authority_id: str
    action: str
    resource: str
    context: Optional[Dict[str, Any]] = {}

class TrqpAuthorizationResponse(BaseModel):
    entity_id: str
    authority_id: str
    action: str
    resource: str
    assertion_verified: bool
    time_requested: Optional[datetime]
    time_evaluated: datetime
    message: Optional[str]
    context: Optional[Dict[str, Any]] = {}

class TrqpRecognitionQuery(BaseModel):
    entity_id: str  # Registry being checked
    authority_id: str  # Ecosystem doing recognition
    action: str
    resource: str
    context: Optional[Dict[str, Any]] = {}

class TrqpRecognitionResponse(BaseModel):
    entity_id: str
    authority_id: str
    action: str
    resource: str
    recognized: bool
    time_requested: Optional[datetime]
    time_evaluated: datetime
    message: Optional[str]
    context: Optional[Dict[str, Any]] = {}
```

### 8.2 Admin Models

```python
class EntityCreate(BaseModel):
    entity_did: str
    authority_id: Optional[str] = None
    name: Optional[str]
    entity_type: Optional[str]
    status: str = "active"
    description: Optional[str]
    authorization_ids: Optional[List[int]]

class AuthorizationCreate(BaseModel):
    action: str
    resource: str
    description: Optional[str]

class RecognitionCreate(BaseModel):
    action: str
    resource: str
    description: Optional[str]

class EntityRecognitionCreate(BaseModel):
    entity_id: int
    recognition_id: int
    recognized_registry_did: str
    recognized: bool = True
    valid_from: Optional[str]  # ISO 8601
    valid_until: Optional[str]  # ISO 8601
```

---

## 9. Business Rules

### 9.1 Entity Rules

1. **Unique DIDs**: Each entity must have a unique DID
2. **Root Ecosystems**: Only ecosystems can have `authority_id = null`
3. **Non-Ecosystem Entities**: Must have an `authority_id` pointing to an ecosystem
4. **Status Values**: Must be one of: active, inactive, suspended
5. **Type Values**: ecosystem, organization, person, device, service

### 9.2 Authorization Rules

1. **Action+Resource Pairs**: Authorizations are defined by action+resource combinations
2. **Hierarchical Actions**: Actions like "root" imply broader authority
3. **Resource Namespacing**: Resources can use namespaces (e.g., "ayracard:businesscard")
4. **Any Entity Type**: All entity types can have authorizations

### 9.3 Recognition Rules

1. **Ecosystem Only**: Only entities with `entity_type = 'ecosystem'` can have recognitions
2. **Directional**: Recognition is one-way (A recognizes B ≠ B recognizes A)
3. **Temporal Validity**: Recognitions can have `valid_from` and `valid_until` dates
4. **Active Ecosystems Only**: Only `status = 'active'` ecosystems provide valid recognitions
5. **Time Checking**: Recognition queries check temporal validity against current time or provided context time

### 9.4 DID Method Rules

1. **Unique Identifiers**: Each DID method must have a unique identifier
2. **Case Sensitivity**: Method identifiers are case-sensitive
3. **Standard Methods**: Support for web, webvh, key, peer
4. **Assurance Levels**: Can define maximum assurance level per method

### 9.5 Assurance Level Rules

1. **URN Format**: Identifiers should follow URN format (e.g., "urn:assurance:loa1")
2. **Unique Names**: Each level must have a unique short name
3. **Ordering**: LOA1 < LOA2 < LOA3 in terms of verification strength

---

## 10. Technical Requirements

### 10.1 Technology Stack

- **Framework**: FastAPI 0.115.5
- **Server**: Uvicorn 0.32.1
- **ORM**: SQLAlchemy ≥2.0.36
- **Database**: SQLite (default), PostgreSQL (supported)
- **Validation**: Pydantic 2.10.2
- **Python**: 3.13+ (requires SQLAlchemy ≥2.0.36 for compatibility)

### 10.2 Database

**SQLite (Default):**
- File: `trqp.db`
- Connection: `sqlite:///./trqp.db`
- Advantages: Zero configuration, portable

**PostgreSQL (Optional):**
- Set `DATABASE_URL` environment variable
- Example: `postgresql://user:password@localhost/trqp_db`
- Install: `psycopg2-binary`

### 10.3 API Standards

- **REST**: RESTful API design
- **JSON**: All requests/responses in JSON
- **HTTP Status Codes**: Proper use of 200, 201, 204, 400, 404, 500
- **CORS**: Enabled for cross-origin requests
- **Error Handling**: RFC 7807 Problem Details format

### 10.4 Performance

- **Database Indexing**: DIDs, actions, resources, types indexed
- **Query Optimization**: Proper joins and filters
- **Pagination**: Support for large entity lists
- **Caching**: 15-minute cache for web fetches

### 10.5 Security

- **Input Validation**: Pydantic models validate all inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **DID Validation**: Basic DID format checking
- **HTTPS**: Should be deployed behind HTTPS proxy in production

---

## 11. Deployment

### 11.1 Installation

```bash
# Clone repository
git clone <repository-url>
cd trqp-ayra-fastapi

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Load seed data (optional)
python load_seed_data.py
```

### 11.2 Running the Server

**Development:**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 11.3 Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `PORT`: Server port (default: 8000)

### 11.4 Endpoints

- **Admin UI**: `http://localhost:8000/admin-ui`
- **API Docs**: `http://localhost:8000/docs`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

---

## 12. Testing

### 12.1 Test Script

**File**: `test_recognition_system.py`

**Tests:**
1. Create recognition types
2. Create/retrieve ecosystem entities
3. Add recognition relationships
4. Query recognitions (positive cases)
5. Query recognitions (negative cases)
6. List recognitions for ecosystems
7. Temporal validity checking

**Run:**
```bash
python test_recognition_system.py
```

### 12.2 API Testing

**Tools:**
- Swagger UI: `http://localhost:8000/docs`
- cURL commands
- Postman/Insomnia

**Example Tests:**
- Create entities via admin API
- Assign authorizations
- Query authorization endpoint
- Add recognitions
- Query recognition endpoint with temporal validity

---

## 13. Data Migration

### 13.1 Seed Data

**File**: `seed_data.sql`

**Includes:**
- Sample DID methods
- Assurance levels
- Authorization types
- Ecosystem hierarchy
- Entity examples with authorizations
- Recognition examples

### 13.2 Database Initialization

**Script**: `init_db.py`

**Actions:**
1. Creates all tables
2. Seeds default data (DID methods, assurance levels, basic authorizations/recognitions)
3. Creates registry configuration

### 13.3 Backup/Restore

**Backup:**
```bash
sqlite3 trqp.db .dump > backup.sql
```

**Restore:**
```bash
rm trqp.db
sqlite3 trqp.db < backup.sql
```

---

## 14. Future Enhancements

### 14.1 Planned Features

1. **Authentication**: Add API key or OAuth2 authentication
2. **Audit Logging**: Track all changes to entities, authorizations, recognitions
3. **Versioning**: Version control for authorization/recognition definitions
4. **Bulk Operations**: Import/export entities via CSV or JSON
5. **Search**: Advanced search and filtering in admin UI
6. **Notifications**: Webhook notifications for changes
7. **Analytics**: Dashboard showing entity statistics, recognition graphs
8. **Multi-tenancy**: Support multiple trust registries in one deployment

### 14.2 Integration Opportunities

1. **Verifiable Credential Issuers**: Integration with VC issuance platforms
2. **DID Resolvers**: Connect to DID resolution infrastructure
3. **Blockchain Anchoring**: Anchor trust registry state to blockchain
4. **Federation**: Cross-registry recognition protocols
5. **Monitoring**: Integration with monitoring tools (Prometheus, Grafana)

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **TRQP** | Trust Registry Query Protocol - specification for querying trust registries |
| **DID** | Decentralized Identifier - W3C standard for decentralized digital identifiers |
| **Authorization** | Permission for an entity to perform an action on a resource |
| **Recognition** | Acknowledgment by one ecosystem that another registry is trusted |
| **Ecosystem** | Governance framework defining rules for a trust network |
| **Entity** | Any registered participant (ecosystem, organization, person, device, service) |
| **Action** | Verb describing what can be done (issue, verify, revoke, etc.) |
| **Resource** | Subject of an action (credential, entity, specific credential type) |
| **Authority** | Ecosystem that governs another entity |
| **Root Ecosystem** | Top-level ecosystem with no governing authority (authority_id = null) |
| **Temporal Validity** | Time period during which a recognition is valid (valid_from to valid_until) |
| **LOA** | Level of Assurance - strength of identity verification |
| **EGF** | Ecosystem Governance Framework - rules and policies for an ecosystem |

---

## 16. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2025-11-17 | System | Added Section 4: API Architecture documenting dual-API design with separate public TRQP API and internal Admin API, including deployment considerations and security requirements |
| 1.0 | 2025-11-14 | System | Initial PRD creation with all implemented features |

---

## 17. Appendices

### Appendix A: Sample Data Structure

**Example Hierarchy:**
```
Root Ecosystem: Ayra Trust Network (did:webvh:SCID-ATN:ayra.forum)
├─ Authorization: [root] ayracard
│
├─ Child Ecosystem: Bubba Group (did:web:bubbagroup.com)
│  ├─ Authorization: [manage-issuers] ayracard:businesscard
│  │
│  └─ Organization: Bubba Bank (did:web:bubbabank.com)
│     └─ Authorization: [issue] ayracard:businesscard
│
└─ Child Ecosystem: First Person Network (did:webvh:SCID-FPN:firstperson.network)
   ├─ Authorization: [issue] ayracard:fpp-person-card
   └─ Recognition: [recognize] ecosystem → did:webvh:SCID-FPN:firstperson.network
```

### Appendix B: API Response Examples

**Successful Authorization Query:**
```json
{
  "entity_id": "did:web:bubbabank.com",
  "authority_id": "did:web:bubbagroup.com",
  "action": "issue",
  "resource": "ayracard:businesscard",
  "assertion_verified": true,
  "time_requested": null,
  "time_evaluated": "2025-11-14T22:00:00Z",
  "message": "Entity authorized to issue ayracard:businesscard",
  "context": {}
}
```

**Failed Authorization Query:**
```json
{
  "entity_id": "did:web:unauthorized.com",
  "authority_id": "did:web:bubbagroup.com",
  "action": "issue",
  "resource": "ayracard:businesscard",
  "assertion_verified": false,
  "time_requested": null,
  "time_evaluated": "2025-11-14T22:00:00Z",
  "message": "Entity not found or not authorized",
  "context": {}
}
```

**Recognition Query with Temporal Validity:**
```json
{
  "entity_id": "did:web:bubbagroup.com",
  "authority_id": "did:webvh:SCID-ATN:ayra.forum",
  "action": "recognize",
  "resource": "ecosystem",
  "recognized": true,
  "time_requested": null,
  "time_evaluated": "2025-11-14T22:00:00Z",
  "message": "Ecosystem recognizes registry (valid until 2026-01-01)",
  "context": {}
}
```

### Appendix C: UI Screenshots Description

1. **Entities Tab**: Table showing all entities with columns for DID, name, authority, type, status, authorizations, recognitions, and action buttons

2. **Recognitions Tab**: Form for creating recognition types and list of existing recognition types with delete buttons

3. **Recognition Modal**: Modal window for managing ecosystem recognitions, showing current recognitions with temporal validity and form to add new ones

4. **Authorization Modal**: Modal window showing current and available authorizations for an entity with add/remove buttons

---

**Document Status**: ✅ Complete
**Last Review**: November 14, 2025
**Next Review**: Quarterly or upon major feature updates
