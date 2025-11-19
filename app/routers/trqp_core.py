"""
TRQP Core Endpoints
Implements TRQP 2.0 compliant query endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any

from app.models import (
    TrqpRecognitionQuery,
    TrqpRecognitionResponse,
    TrqpAuthorizationQuery,
    TrqpAuthorizationResponse,
    ProblemDetails
)
from app.database import get_db
from app import crud

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
async def query_recognition(query: TrqpRecognitionQuery, db: Session = Depends(get_db)) -> TrqpRecognitionResponse:
    """
    Queries the trust registry to determine if one ecosystem recognizes another.

    This endpoint checks if the ecosystem identified by `authority_id` recognizes
    the trust registry identified by `entity_id` for the specified action and resource.

    Args:
        query: TrqpRecognitionQuery containing entity_id, authority_id, action, resource, and optional context
        db: Database session

    Returns:
        TrqpRecognitionResponse indicating whether the recognition is valid

    Raises:
        HTTPException: 404 if entity not found, 401 if unauthorized
    """
    # Extract time from context or use current time
    time_evaluated = datetime.now(timezone.utc)
    time_requested = None
    check_time = time_evaluated

    if query.context and "time" in query.context:
        try:
            time_requested = query.context["time"]
            if isinstance(time_requested, str):
                time_requested = datetime.fromisoformat(time_requested.replace('Z', '+00:00'))
            time_evaluated = time_requested
            check_time = time_requested
        except (ValueError, AttributeError):
            pass

    # Validate DIDs
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

    if not query.authority_id.startswith("did:"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://example.com/errors/entity-not-found",
                "title": "Authority Not Found",
                "status": 404,
                "detail": f"Authority with ID '{query.authority_id}' not found in the trust registry",
                "instance": "/recognition"
            }
        )

    # Check if the recognizing ecosystem exists
    recognizing_ecosystem = crud.get_entity_by_did(db, query.authority_id)
    if not recognizing_ecosystem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://example.com/errors/entity-not-found",
                "title": "Recognizing Ecosystem Not Found",
                "status": 404,
                "detail": f"Recognizing ecosystem '{query.authority_id}' not found",
                "instance": "/recognition"
            }
        )

    if recognizing_ecosystem.entity_type != "ecosystem":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "https://example.com/errors/invalid-entity-type",
                "title": "Invalid Entity Type",
                "status": 400,
                "detail": f"Authority '{query.authority_id}' is not an ecosystem",
                "instance": "/recognition"
            }
        )

    # Check if the recognized registry exists (optional - it might be external)
    recognized_registry = crud.get_entity_by_did(db, query.entity_id)

    # Use the new CRUD function to check recognition
    recognized = crud.check_ecosystem_recognition(
        db,
        recognizing_ecosystem_did=query.authority_id,
        recognized_registry_did=query.entity_id,
        action=query.action,
        resource=query.resource,
        check_time=check_time
    )

    message = None
    if recognized:
        message = f"Ecosystem '{query.authority_id}' recognizes registry '{query.entity_id}' for action '{query.action}' on resource '{query.resource}'"
    else:
        message = f"Ecosystem '{query.authority_id}' does not recognize registry '{query.entity_id}' for action '{query.action}' on resource '{query.resource}'"

    return TrqpRecognitionResponse(
        entity_id=query.entity_id,
        authority_id=query.authority_id,
        action=query.action,
        resource=query.resource,
        recognized=recognized,
        time_requested=time_requested,
        time_evaluated=time_evaluated,
        message=message,
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
async def query_authorization(query: TrqpAuthorizationQuery, db: Session = Depends(get_db)) -> TrqpAuthorizationResponse:
    """
    Queries the trust registry to determine if an entity has authorization in an ecosystem.

    This endpoint checks if the entity identified by `entity_id` is authorized by
    the ecosystem identified by `authority_id` for the specified action and resource.

    Args:
        query: TrqpAuthorizationQuery containing entity_id, authority_id, action, resource, and optional context
        db: Database session

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

    # Validate DIDs
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

    if not query.authority_id.startswith("did:"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://example.com/errors/authority-not-found",
                "title": "Authority Not Found",
                "status": 404,
                "detail": f"Authority with ID '{query.authority_id}' not found in the trust registry",
                "instance": "/authorization"
            }
        )

    # Check if the entity exists
    entity = crud.get_entity_by_did(db, query.entity_id)
    if not entity:
        return TrqpAuthorizationResponse(
            entity_id=query.entity_id,
            authority_id=query.authority_id,
            action=query.action,
            resource=query.resource,
            authorized=False,
            time_requested=time_requested,
            time_evaluated=time_evaluated,
            message=f"Entity '{query.entity_id}' not found in the trust registry",
            context=query.context
        )

    # Check if the entity's authority matches the queried authority
    if entity.authority_id != query.authority_id:
        return TrqpAuthorizationResponse(
            entity_id=query.entity_id,
            authority_id=query.authority_id,
            action=query.action,
            resource=query.resource,
            authorized=False,
            time_requested=time_requested,
            time_evaluated=time_evaluated,
            message=f"Entity '{query.entity_id}' is not governed by authority '{query.authority_id}'",
            context=query.context
        )

    # Check if entity is active
    if entity.status != "active":
        return TrqpAuthorizationResponse(
            entity_id=query.entity_id,
            authority_id=query.authority_id,
            action=query.action,
            resource=query.resource,
            authorized=False,
            time_requested=time_requested,
            time_evaluated=time_evaluated,
            message=f"Entity '{query.entity_id}' is not active (status: {entity.status})",
            context=query.context
        )

    # Get entity authorizations
    authorizations = crud.get_entity_authorizations_list(db, query.entity_id, query.authority_id)

    # Check if entity has the requested authorization
    has_authorization = any(
        auth.action == query.action and auth.resource == query.resource
        for auth in authorizations
    )

    if has_authorization:
        message = f"Entity '{query.entity_id}' is authorized by '{query.authority_id}' for action '{query.action}' on resource '{query.resource}'"
    else:
        message = f"Entity '{query.entity_id}' is NOT authorized by '{query.authority_id}' for action '{query.action}' on resource '{query.resource}'"

    return TrqpAuthorizationResponse(
        entity_id=query.entity_id,
        authority_id=query.authority_id,
        action=query.action,
        resource=query.resource,
        authorized=has_authorization,
        time_requested=time_requested,
        time_evaluated=time_evaluated,
        message=message,
        context=query.context
    )
