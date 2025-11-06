"""
Main FastAPI Application
Ayra TRQP Profile API Implementation
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
import logging
import os

from app import __version__
from app.routers import trqp_core, ayra_extension, lookup, admin
from app.database import init_db, seed_default_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database on startup
init_db()
seed_default_data()
logger.info("Database initialized")

# Create FastAPI application
app = FastAPI(
    title="Ayra TRQP Profile API",
    version=__version__,
    description="""
    This specification defines a RESTful TRQP profile for use in the Ayra™ Trust Network.
    It includes endpoints for retrieving Trust Registry metadata,
    authorization data, verifying entity authorization status,
    and checking ecosystem recognition.

    ## TRQP Core Endpoints
    - POST /recognition - Query ecosystem recognition
    - POST /authorization - Query entity authorization

    ## Ayra Extension Endpoints
    - GET /metadata - Retrieve Trust Registry metadata
    - GET /entities/{entity_id} - Get entity information
    - GET /entities/{entity_did}/authorizations - List entity authorizations
    - GET /ecosystems/{ecosystem_did}/recognitions - List recognized ecosystems

    ## Lookup Endpoints
    - GET /lookups/assuranceLevels - Lookup supported assurance levels
    - GET /lookups/authorizations - Lookup available authorizations
    - GET /lookups/didMethods - Lookup supported DID methods
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trqp_core.router)
app.include_router(ayra_extension.router)
app.include_router(lookup.router)
app.include_router(admin.router)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information
    """
    return {
        "name": "Ayra TRQP Profile API",
        "version": __version__,
        "description": "Trust Registry Query Protocol (TRQP) Implementation",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "admin_ui": "/admin-ui"
        },
        "endpoints": {
            "trqp_core": ["/recognition", "/authorization"],
            "ayra_extension": [
                "/metadata",
                "/entities/{entity_id}",
                "/entities/{entity_did}/authorizations",
                "/ecosystems/{ecosystem_did}/recognitions"
            ],
            "lookup": [
                "/lookups/assuranceLevels",
                "/lookups/authorizations",
                "/lookups/didMethods"
            ],
            "admin": [
                "/admin/did-methods",
                "/admin/assurance-levels",
                "/admin/authorizations",
                "/admin/entities"
            ]
        }
    }


@app.get("/admin-ui", response_class=HTMLResponse, tags=["admin"])
async def admin_ui():
    """
    Admin UI for managing lookup values and entities
    """
    with open(os.path.join(os.path.dirname(__file__), "static", "admin.html"), "r") as f:
        return f.read()


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": __version__
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://example.com/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred",
            "instance": str(request.url)
        }
    )


def custom_openapi():
    """
    Customize OpenAPI schema to match the original specification
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Ayra TRQP Profile API",
        version=__version__,
        description=app.description,
        routes=app.routes,
    )

    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "https://example-trust-registry.com",
            "description": "Production server (example)"
        },
        {
            "url": "https://sandbox-trust-registry.com",
            "description": "Sandbox server (example)"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
