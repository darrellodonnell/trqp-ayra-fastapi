"""
Main application entry point
Combines public TRQP API and internal Admin API
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import os

from app import __version__
from app.database import init_db, seed_default_data
from app.routers import trqp_core, ayra_extension, lookup

# Initialize database on startup
init_db()
seed_default_data()

# Create main application with public API
app = FastAPI(
    title="Ayra TRQP Profile API",
    version=__version__,
    description="""
    # Trust Registry Query Protocol (TRQP) 2.0 Profile API

    This specification defines a RESTful TRQP profile for use in the Ayra™ Trust Network.
    It provides public endpoints for querying trust relationships, entity authorizations,
    and ecosystem recognitions.

    ## About TRQP

    The Trust Registry Query Protocol (TRQP) enables verifiable credential ecosystems to
    query trust registries to determine if entities are authorized to perform specific
    actions on resources, and if ecosystems recognize other registries.

    ## API Categories

    ### 🔍 TRQP Core Endpoints
    Query authorization and recognition status:
    - **POST /authorization** - Check if an entity has authorization
    - **POST /recognition** - Check if an ecosystem recognizes another registry

    ### 🌐 Ayra Extension Endpoints
    Extended functionality for the Ayra Trust Network:
    - **GET /metadata** - Retrieve Trust Registry metadata
    - **GET /entities** - List registered entities (paginated)
    - **GET /entities/{entity_did}/authorizations** - List entity authorizations
    - **GET /ecosystems/{ecosystem_did}/recognitions** - List ecosystem recognitions

    ### 📋 Lookup Endpoints
    Discover supported values and configurations:
    - **GET /lookups/assuranceLevels** - Identity assurance levels
    - **GET /lookups/authorizations** - Available authorization types
    - **GET /lookups/didMethods** - Supported DID methods

    ## Admin API

    A separate Admin API is available at `/admin` for managing the trust registry.
    See `/admin/docs` for administrative endpoints.

    ## Authentication

    Currently no authentication is required for public queries.
    In production, consider implementing API keys or OAuth2.

    ## Rate Limiting

    No rate limiting is currently enforced.
    Production deployments should implement appropriate rate limits.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Ayra Trust Network",
        "url": "https://ayra.forum",
        "email": "support@ayra.forum"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include PUBLIC routers
app.include_router(trqp_core.router, tags=["TRQP Core"])
app.include_router(ayra_extension.router, tags=["Ayra Extensions"])
app.include_router(lookup.router, tags=["Lookups"])

# Mount the admin API at /admin
from app.main_admin import app as admin_app
app.mount("/admin", admin_app)


@app.get("/admin-ui", include_in_schema=False)
async def redirect_admin_ui():
    """
    Redirect /admin-ui to /admin/ui for backwards compatibility
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/admin/ui")


@app.get("/", tags=["Information"])
async def root():
    """
    Root endpoint providing API information and available endpoints
    """
    return {
        "name": "Ayra TRQP Profile API",
        "version": __version__,
        "description": "Trust Registry Query Protocol (TRQP) 2.0 Implementation",
        "specification": "https://trustoverip.org/trqp/",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json",
            "landing_page": "/welcome"
        },
        "endpoints": {
            "trqp_core": {
                "authorization": "/authorization",
                "recognition": "/recognition"
            },
            "ayra_extensions": {
                "metadata": "/metadata",
                "entities_list": "/entities",
                "entity_authorizations": "/entities/{entity_did}/authorizations",
                "ecosystem_recognitions": "/ecosystems/{ecosystem_did}/recognitions"
            },
            "lookups": {
                "assurance_levels": "/lookups/assuranceLevels",
                "authorizations": "/lookups/authorizations",
                "did_methods": "/lookups/didMethods"
            }
        },
        "admin_api": {
            "url": "/admin",
            "description": "Separate admin API for registry management",
            "swagger_ui": "/admin/docs",
            "admin_ui": "/admin/ui"
        }
    }


@app.get("/welcome", response_class=HTMLResponse, include_in_schema=False)
async def landing_page():
    """
    Landing page with links to both API documentation
    """
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Ayra Trust Registry</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    max-width: 1200px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .container {
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                h1 {
                    color: #2d3748;
                    margin-bottom: 10px;
                }
                .version {
                    color: #718096;
                    font-size: 14px;
                    margin-bottom: 30px;
                }
                .api-section {
                    margin: 30px 0;
                    padding: 25px;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                }
                .api-section:hover {
                    border-color: #667eea;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
                }
                .api-section h2 {
                    color: #2d3748;
                    margin-top: 0;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .api-section p {
                    color: #4a5568;
                    line-height: 1.6;
                }
                .links {
                    display: flex;
                    gap: 15px;
                    flex-wrap: wrap;
                    margin-top: 15px;
                }
                a {
                    display: inline-block;
                    padding: 10px 20px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    transition: all 0.2s;
                }
                a:hover {
                    background: #5568d3;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                }
                .warning {
                    background: #fff5f5;
                    border-left: 4px solid #fc8181;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }
                .warning strong {
                    color: #c53030;
                }
                .badge {
                    display: inline-block;
                    padding: 3px 10px;
                    background: #48bb78;
                    color: white;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-left: 10px;
                }
                .badge.internal {
                    background: #ed8936;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .feature {
                    padding: 20px;
                    background: #f7fafc;
                    border-radius: 8px;
                    border-left: 3px solid #667eea;
                }
                .feature h3 {
                    margin-top: 0;
                    color: #2d3748;
                    font-size: 16px;
                }
                .feature p {
                    margin: 0;
                    font-size: 14px;
                    color: #718096;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Ayra Trust Registry</h1>
                <p class="version">Version """ + __version__ + """ | TRQP 2.0 Implementation</p>

                <div class="api-section">
                    <h2>
                        🌐 Public TRQP API
                        <span class="badge">PUBLIC</span>
                    </h2>
                    <p>
                        Trust Registry Query Protocol (TRQP) 2.0 compliant endpoints for querying
                        trust relationships, entity authorizations, and ecosystem recognitions.
                        This API is designed for public consumption by verifiers and relying parties.
                    </p>
                    <div class="links">
                        <a href="/docs">📚 Swagger UI</a>
                        <a href="/redoc">📖 ReDoc</a>
                        <a href="/openapi.json">⚙️ OpenAPI Spec</a>
                    </div>
                    <div class="features">
                        <div class="feature">
                            <h3>🔍 TRQP Core</h3>
                            <p>Authorization and recognition queries</p>
                        </div>
                        <div class="feature">
                            <h3>🌟 Ayra Extensions</h3>
                            <p>Metadata, entities, and relationship lookups</p>
                        </div>
                        <div class="feature">
                            <h3>📋 Lookups</h3>
                            <p>DID methods, assurance levels, authorization types</p>
                        </div>
                    </div>
                </div>

                <div class="api-section">
                    <h2>
                        🛠️ Admin API
                        <span class="badge internal">INTERNAL</span>
                    </h2>
                    <div class="warning">
                        <strong>⚠️ INTERNAL USE ONLY</strong><br>
                        This API should NOT be exposed to the public internet without proper
                        authentication and authorization controls. It provides full CRUD access
                        to trust registry data.
                    </div>
                    <p>
                        Administrative endpoints for managing entities, authorizations, recognitions,
                        DID methods, assurance levels, and registry configuration. Includes a web-based
                        admin UI for easy management.
                    </p>
                    <div class="links">
                        <a href="/admin/ui">🎨 Admin UI</a>
                        <a href="/admin/docs">📚 Swagger UI</a>
                        <a href="/admin/redoc">📖 ReDoc</a>
                        <a href="/admin/openapi.json">⚙️ OpenAPI Spec</a>
                    </div>
                    <div class="features">
                        <div class="feature">
                            <h3>🏢 Entity Management</h3>
                            <p>Create and manage ecosystems, organizations, persons</p>
                        </div>
                        <div class="feature">
                            <h3>✅ Authorizations</h3>
                            <p>Define and assign authorization types</p>
                        </div>
                        <div class="feature">
                            <h3>🤝 Recognitions</h3>
                            <p>Manage cross-ecosystem trust relationships</p>
                        </div>
                        <div class="feature">
                            <h3>🔑 DID Methods</h3>
                            <p>Configure supported DID methods</p>
                        </div>
                        <div class="feature">
                            <h3>🛡️ Assurance Levels</h3>
                            <p>Define identity verification levels</p>
                        </div>
                        <div class="feature">
                            <h3>⚙️ Registry Config</h3>
                            <p>Set default authority and governance</p>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e2e8f0; color: #718096; font-size: 14px;">
                    <p>
                        <strong>About TRQP:</strong> The Trust Registry Query Protocol enables verifiable
                        credential ecosystems to query trust registries to determine if entities are
                        authorized to perform specific actions on resources, and if ecosystems recognize
                        other registries.
                    </p>
                    <p>
                        📚 <a href="https://trustoverip.org/trqp/" style="background: transparent; color: #667eea; padding: 0;">
                            Learn more about TRQP
                        </a>
                    </p>
                </div>
            </div>
        </body>
    </html>
    """


def custom_openapi():
    """
    Customize OpenAPI schema for TRQP compliance
    """
    if app.openapi_schema:
        return app.openapi_schema

    # Filter out admin routes and mounted apps from public API documentation
    from fastapi.routing import Mount
    public_routes = [
        route for route in app.routes
        if not (
            isinstance(route, Mount) or
            (hasattr(route, 'path') and route.path.startswith('/admin'))
        )
    ]

    openapi_schema = get_openapi(
        title="Ayra TRQP Profile API",
        version=__version__,
        description=app.description,
        routes=public_routes,
    )

    # Add servers - use EXTERNAL_URL if set (useful for ngrok tunneling)
    external_url = os.getenv("EXTERNAL_URL", "").strip()

    if external_url:
        # External URL is set (e.g., ngrok tunnel)
        openapi_schema["servers"] = [
            {
                "url": external_url,
                "description": "Current Deployment"
            },
            {
                "url": "http://localhost:8000",
                "description": "Local Development"
            }
        ]
    else:
        # Default servers for standard deployment
        openapi_schema["servers"] = [
            {
                "url": "https://registry.ayra.forum",
                "description": "Production Trust Registry"
            },
            {
                "url": "https://sandbox.ayra.forum",
                "description": "Sandbox Trust Registry"
            },
            {
                "url": "http://localhost:8000",
                "description": "Local Development"
            }
        ]

    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "TRQP Core",
            "description": "Trust Registry Query Protocol 2.0 core endpoints for authorization and recognition queries"
        },
        {
            "name": "Ayra Extensions",
            "description": "Ayra-specific extensions for metadata and entity information"
        },
        {
            "name": "Lookups",
            "description": "Lookup endpoints for discovering supported values and configurations"
        },
        {
            "name": "Information",
            "description": "API information and discovery endpoints"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
