"""
Lookup Endpoints
Implements lookup capabilities for Ayra TRQP
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models import (
    AssuranceLevelResponse,
    Authorization,
    DIDMethodType,
    DIDMethodListType,
    ProblemDetails
)
from app.database import get_db
from app import crud

router = APIRouter(tags=["lookup", "ayra-extension"])


@router.get(
    "/lookups/assuranceLevels",
    response_model=List[AssuranceLevelResponse],
    responses={
        200: {"description": "Supported assurance levels retrieved successfully"},
        401: {"model": ProblemDetails, "description": "Unauthorized request"},
        501: {"model": ProblemDetails, "description": "Method not implemented"}
    },
    summary="Lookup Supported Assurance Levels",
    operation_id="lookupSupportedAssuranceLevels"
)
async def lookup_supported_assurance_levels(
    ecosystem_did: Optional[str] = Query(None, description="Unique identifier of the ecosystem being queried"),
    db: Session = Depends(get_db)
) -> List[AssuranceLevelResponse]:
    """
    Retrieves the supported assurance levels for the specified ecosystem.

    Args:
        ecosystem_did: Optional ecosystem identifier to filter assurance levels
        db: Database session

    Returns:
        List of AssuranceLevelResponse objects

    Raises:
        HTTPException: 401 if unauthorized, 501 if not implemented
    """
    assurance_levels = crud.get_assurance_levels(db, egf_did=ecosystem_did)

    return [
        AssuranceLevelResponse(
            assurance_level=al.name,
            description=al.description,
            egf_did=al.egf_did
        )
        for al in assurance_levels
    ]


@router.get(
    "/lookups/authorizations",
    response_model=List[Authorization],
    responses={
        200: {"description": "A list of authorization responses"},
        404: {"model": ProblemDetails, "description": "Entity not found"},
        401: {"model": ProblemDetails, "description": "Unauthorized request"},
        501: {"model": ProblemDetails, "description": "Method not implemented"}
    },
    summary="Lookup Authorizations",
    operation_id="lookupAuthorizations"
)
async def lookup_authorizations(
    ecosystem_did: Optional[str] = Query(None, description="Ecosystem identifier"),
    db: Session = Depends(get_db)
) -> List[Authorization]:
    """
    Performs an authorization lookup based on the provided ecosystem identifier.
    These strings can be used in TRQP queries for this ecosystem (as `assertion_id` values).

    Args:
        ecosystem_did: Optional ecosystem identifier to filter authorizations
        db: Database session

    Returns:
        List of Authorization objects

    Raises:
        HTTPException: 404 if not found, 401 if unauthorized, 501 if not implemented
    """
    authorizations = crud.get_authorizations(db, ecosystem_did)

    return [
        Authorization(
            action=auth.action,
            resource=auth.resource,
            description=auth.description
        )
        for auth in authorizations
    ]


@router.get(
    "/lookups/didMethods",
    response_model=DIDMethodListType,
    responses={
        200: {"description": "Supported DID Methods retrieved successfully"},
        404: {"model": ProblemDetails, "description": "Ecosystem not found"},
        401: {"model": ProblemDetails, "description": "Unauthorized request"},
        501: {"model": ProblemDetails, "description": "Method not implemented"}
    },
    summary="Lookup Supported DID Methods",
    operation_id="lookupSupportedDIDMethods"
)
async def lookup_supported_did_methods(
    ecosystem_did: Optional[str] = Query(None, description="Unique identifier of the ecosystem being queried"),
    db: Session = Depends(get_db)
) -> DIDMethodListType:
    """
    Retrieves the supported DID Methods. AYRA is opinionated here.

    Args:
        ecosystem_did: Optional ecosystem identifier to filter DID methods
        db: Database session

    Returns:
        List of DIDMethodType objects

    Raises:
        HTTPException: 404 if ecosystem not found, 401 if unauthorized, 501 if not implemented
    """
    did_methods = crud.get_did_methods(db, egf_did=ecosystem_did)

    return [
        DIDMethodType(
            identifier=method.identifier,
            egf_did=method.egf_did,
            maximumAssuranceLevel=None  # TODO: Map from string to AssuranceLevelType if needed
        )
        for method in did_methods
    ]
