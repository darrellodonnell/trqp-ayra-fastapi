"""
Public TRQP Profile API
Trust Registry Query Protocol (TRQP) 2.0 compliant endpoints
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging

from app import __version__
from app.routers import trqp_core, ayra_extension, lookup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Public API application
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

# Include PUBLIC routers only
app.include_router(trqp_core.router, tags=["trqp-core"])
app.include_router(ayra_extension.router, tags=["ayra-extensions"])
app.include_router(lookup.router, tags=["lookup"])


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
            "openapi_spec": "/openapi.json"
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
            "swagger_ui": "/admin/docs"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    return {
        "status": "healthy",
        "api": "public",
        "version": __version__
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler following RFC 7807 Problem Details
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
    Customize OpenAPI schema for TRQP compliance
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
            "name": "trqp-core",
            "description": "Trust Registry Query Protocol 2.0 core endpoints for authorization and recognition queries"
        },
        {
            "name": "ayra-extensions",
            "description": "Ayra-specific extensions for metadata and entity information"
        },
        {
            "name": "lookup",
            "description": "Lookup endpoints for discovering supported values and configurations"
        },
        {
            "name": "Information",
            "description": "API information and discovery endpoints"
        },
        {
            "name": "Health",
            "description": "Health check and monitoring endpoints"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
