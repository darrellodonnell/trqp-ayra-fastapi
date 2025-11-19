"""
Internal Admin API
Administrative endpoints for managing the trust registry
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import os

from app import __version__
from app.routers import admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Admin API application
app = FastAPI(
    title="Ayra Trust Registry - Admin API",
    version=__version__,
    description="""
    # Trust Registry Administration API

    **⚠️ INTERNAL USE ONLY - REQUIRES AUTHENTICATION**

    This API provides administrative endpoints for managing the Ayra Trust Registry.
    It should **NOT** be exposed to the public internet without proper authentication
    and authorization controls.

    ## Features

    ### 🏢 Entity Management
    - Create, update, delete entities (ecosystems, organizations, persons, devices, services)
    - Manage entity hierarchies and authority relationships
    - View entity authorizations and recognitions

    ### ✅ Authorization Management
    - Define authorization types (action+resource pairs)
    - Assign authorizations to entities
    - Remove authorizations from entities

    ### 🤝 Recognition Management
    - Define recognition types for cross-ecosystem trust
    - Assign recognitions to ecosystems with temporal validity
    - Manage recognized registries per ecosystem

    ### 🔑 DID Method Management
    - Configure supported DID methods
    - Set maximum assurance levels per method
    - Associate methods with governance frameworks

    ### 🛡️ Assurance Level Management
    - Define identity verification levels (LOA1, LOA2, LOA3, etc.)
    - Configure assurance level policies
    - Associate with governance frameworks

    ### ⚙️ Registry Configuration
    - Set default authority and governance framework
    - Configure registry metadata
    - Manage registry controllers

    ## Security Recommendations

    **Production Deployment:**
    1. ✅ Enable API key authentication
    2. ✅ Use OAuth2/OIDC for user authentication
    3. ✅ Implement role-based access control (RBAC)
    4. ✅ Deploy behind VPN or IP whitelist
    5. ✅ Enable audit logging for all changes
    6. ✅ Use HTTPS with valid certificates
    7. ✅ Rate limiting and request throttling
    8. ✅ Regular security audits

    ## Admin UI

    A web-based admin interface is available at `/ui` for managing the registry
    through a user-friendly interface.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/admin"  # All routes will be prefixed with /admin
)

# Configure CORS (more restrictive for admin API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        # Add your admin UI domains here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include ADMIN router
app.include_router(admin.router, prefix="", tags=["Admin"])


@app.get("/", tags=["Information"])
async def admin_root():
    """
    Admin API information and available endpoints
    """
    return {
        "name": "Ayra Trust Registry - Admin API",
        "version": __version__,
        "description": "Internal administration API for trust registry management",
        "warning": "⚠️ INTERNAL USE ONLY - Authentication required in production",
        "documentation": {
            "swagger_ui": "/admin/docs",
            "redoc": "/admin/redoc",
            "openapi_spec": "/admin/openapi.json",
            "admin_ui": "/admin/ui"
        },
        "endpoints": {
            "entities": "/admin/entities",
            "authorizations": "/admin/authorizations",
            "recognitions": "/admin/recognitions",
            "did_methods": "/admin/did-methods",
            "assurance_levels": "/admin/assurance-levels",
            "registry_config": "/admin/registry-config"
        },
        "public_api": {
            "url": "/",
            "swagger_ui": "/docs",
            "description": "Public TRQP query API"
        }
    }


@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
async def admin_ui():
    """
    Web-based Admin UI for managing the trust registry
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), "static", "admin.html"), "r") as f:
            html_content = f.read()

        # No need to modify API_BASE - paths in admin.html are already relative
        # (e.g., /entities, /authorizations) and will resolve correctly since
        # the admin app is mounted at /admin in main.py
        return html_content
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Admin UI Not Found</title></head>
                <body>
                    <h1>Admin UI Not Found</h1>
                    <p>The admin UI HTML file is missing. Please check the deployment.</p>
                    <p><a href="/admin/docs">View API Documentation</a></p>
                </body>
            </html>
            """,
            status_code=404
        )


@app.get("/health", tags=["Health"])
async def admin_health_check():
    """
    Health check endpoint for admin API monitoring
    """
    return {
        "status": "healthy",
        "api": "admin",
        "version": __version__
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler following RFC 7807 Problem Details
    """
    logger.error(f"Admin API unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://example.com/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred in the admin API",
            "instance": str(request.url)
        }
    )


def custom_openapi():
    """
    Customize OpenAPI schema for admin API
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Ayra Trust Registry - Admin API",
        version=__version__,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes (for future authentication)
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for admin access (not currently enforced)"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for admin access (not currently enforced)"
        }
    }

    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "Admin",
            "description": "Administrative endpoints for managing trust registry data"
        },
        {
            "name": "Information",
            "description": "API information and discovery"
        },
        {
            "name": "UI",
            "description": "Web-based admin interface"
        },
        {
            "name": "Health",
            "description": "Health check and monitoring"
        }
    ]

    # Add servers - use EXTERNAL_URL if set (useful for ngrok tunneling)
    external_url = os.getenv("EXTERNAL_URL", "").strip()

    if external_url:
        # External URL is set (e.g., ngrok tunnel) - append /admin for admin API
        admin_url = external_url.rstrip('/') + '/admin'
        openapi_schema["servers"] = [
            {
                "url": admin_url,
                "description": "Current Deployment - Admin API"
            },
            {
                "url": "http://localhost:8000/admin",
                "description": "Local Development - Admin API"
            }
        ]
    else:
        # Default servers for standard deployment
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000/admin",
                "description": "Local Development - Admin API"
            },
            {
                "url": "https://admin.registry.ayra.forum",
                "description": "Production Admin API (internal only)"
            }
        ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
