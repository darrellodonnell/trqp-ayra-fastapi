"""
TRQP Core Endpoints
Implements TRQP 2.0 compliant query endpoints
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from typing import Dict, Any

from app.models import (
    TrqpRecognitionQuery,
    TrqpRecognitionResponse,
    TrqpAuthorizationQuery,
    TrqpAuthorizationResponse,
    ProblemDetails
)

router = APIRouter(tags=["trqp-core"])


@router.post(
    "/recognition",
    response_model=TrqpRecognitionResponse,
    responses={
        200: {"description": "Recognition query successful"},
        404: {"model": ProblemDetails, "description": "Entity not found"},
        401: {"model": ProblemDetails, "description": "Unauthorized request"}
    },
    summary="Queries registry for recognition, by an ecosystem, of another ecosystem"
)
async def query_recognition(query: TrqpRecognitionQuery) -> TrqpRecognitionResponse:
    """
    Queries the trust registry to determine if one ecosystem recognizes another.

    This endpoint checks if the ecosystem identified by `authority_id` recognizes
    the trust registry identified by `entity_id` for the specified action and resource.

    Args:
        query: TrqpRecognitionQuery containing entity_id, authority_id, action, resource, and optional context

    Returns:
        TrqpRecognitionResponse indicating whether the recognition is valid

    Raises:
        HTTPException: 404 if entity not found, 401 if unauthorized
    """
    # Extract time from context or use current time
    time_evaluated = datetime.now(timezone.utc)
    time_requested = None

    if query.context and "time" in query.context:
        try:
            time_requested = query.context["time"]
            if isinstance(time_requested, str):
                time_requested = datetime.fromisoformat(time_requested.replace('Z', '+00:00'))
            time_evaluated = time_requested
        except (ValueError, AttributeError):
            pass

    # TODO: Implement actual recognition logic
    # This is a stub implementation that returns a default response

    # Example: Check if entity_id and authority_id are valid DIDs
    if not query.entity_id.startswith("did:"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://example.com/errors/entity-not-found",
                "title": "Entity Not Found",
                "status": 404,
                "detail": f"Entity with ID '{query.entity_id}' not found in the trust registry",
                "instance": "/recognition"
            }
        )

    # Stub response - in production, query your database/registry
    return TrqpRecognitionResponse(
        entity_id=query.entity_id,
        authority_id=query.authority_id,
        action=query.action,
        resource=query.resource,
        recognized=False,  # Default to not recognized - implement your logic here
        time_requested=time_requested,
        time_evaluated=time_evaluated,
        message="This is a stub implementation. Implement recognition logic.",
        context=query.context
    )


@router.post(
    "/authorization",
    response_model=TrqpAuthorizationResponse,
    responses={
        200: {"description": "Authorization query successful"},
        404: {"model": ProblemDetails, "description": "Entity not found"},
        401: {"model": ProblemDetails, "description": "Unauthorized request"}
    },
    summary="Queries registry for Authorization, by an Ecosystem, of an Entity"
)
async def query_authorization(query: TrqpAuthorizationQuery) -> TrqpAuthorizationResponse:
    """
    Queries the trust registry to determine if an entity has authorization in an ecosystem.

    This endpoint checks if the entity identified by `entity_id` is authorized by
    the ecosystem identified by `authority_id` for the specified action and resource.

    Args:
        query: TrqpAuthorizationQuery containing entity_id, authority_id, action, resource, and optional context

    Returns:
        TrqpAuthorizationResponse indicating whether the authorization is verified

    Raises:
        HTTPException: 404 if entity not found, 401 if unauthorized
    """
    # Extract time from context or use current time
    time_evaluated = datetime.now(timezone.utc)
    time_requested = None

    if query.context and "time" in query.context:
        try:
            time_requested = query.context["time"]
            if isinstance(time_requested, str):
                time_requested = datetime.fromisoformat(time_requested.replace('Z', '+00:00'))
            time_evaluated = time_requested
        except (ValueError, AttributeError):
            pass

    # TODO: Implement actual authorization logic
    # This is a stub implementation that returns a default response

    # Example: Check if entity_id and authority_id are valid DIDs
    if not query.entity_id.startswith("did:"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://example.com/errors/entity-not-found",
                "title": "Entity Not Found",
                "status": 404,
                "detail": f"Entity with ID '{query.entity_id}' not found in the trust registry",
                "instance": "/authorization"
            }
        )

    # Stub response - in production, query your database/registry
    return TrqpAuthorizationResponse(
        entity_id=query.entity_id,
        authority_id=query.authority_id,
        action=query.action,
        resource=query.resource,
        assertion_verified=False,  # Default to not verified - implement your logic here
        time_requested=time_requested,
        time_evaluated=time_evaluated,
        message="This is a stub implementation. Implement authorization logic.",
        context=query.context
    )
