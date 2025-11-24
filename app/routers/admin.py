"""
Admin Endpoints
Provides CRUD operations for managing lookup values and entities
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app import crud


router = APIRouter(tags=["admin"])


# Pydantic schemas for admin operations
class DIDMethodCreate(BaseModel):
    identifier: str = Field(..., description="DID method identifier (e.g., 'web', 'key')")
    egf_did: Optional[str] = Field(None, description="EGF DID this method applies to")
    maximum_assurance_level: Optional[str] = Field(None, description="Maximum assurance level")
    description: Optional[str] = Field(None, description="Description of the DID method")


class DIDMethodUpdate(BaseModel):
    identifier: Optional[str] = None
    egf_did: Optional[str] = None
    maximum_assurance_level: Optional[str] = None
    description: Optional[str] = None


class DIDMethodResponse(BaseModel):
    id: int
    identifier: str
    egf_did: Optional[str]
    maximum_assurance_level: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


class AssuranceLevelCreate(BaseModel):
    identifier: str = Field(..., description="URI identifier for the assurance level")
    name: str = Field(..., description="Short name (e.g., 'LOA1', 'LOA2')")
    description: str = Field(..., description="Description of the assurance level")
    egf_did: Optional[str] = Field(None, description="EGF DID this assurance level applies to")


class AssuranceLevelUpdate(BaseModel):
    identifier: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    egf_did: Optional[str] = None


class AssuranceLevelResponseAdmin(BaseModel):
    id: int
    identifier: str
    name: str
    description: str
    egf_did: Optional[str]

    class Config:
        from_attributes = True


class AuthorizationCreate(BaseModel):
    action: str = Field(..., description="Action (e.g., 'issue', 'verify', 'revoke')")
    resource: str = Field(..., description="Resource (e.g., 'credential', 'entity')")
    description: Optional[str] = Field(None, description="Description of the authorization")


class AuthorizationUpdate(BaseModel):
    action: Optional[str] = None
    resource: Optional[str] = None
    description: Optional[str] = None


class AuthorizationResponseAdmin(BaseModel):
    id: int
    action: str
    resource: str
    description: Optional[str]

    class Config:
        from_attributes = True


class RecognitionCreate(BaseModel):
    action: str = Field(..., description="Action (e.g., 'recognize')")
    resource: str = Field(..., description="Resource (e.g., 'credential', 'entity', 'ecosystem')")
    description: Optional[str] = Field(None, description="Description of the recognition")


class RecognitionUpdate(BaseModel):
    action: Optional[str] = None
    resource: Optional[str] = None
    description: Optional[str] = None


class RecognitionResponseAdmin(BaseModel):
    id: int
    action: str
    resource: str
    description: Optional[str]

    class Config:
        from_attributes = True


class EntityRecognitionCreate(BaseModel):
    recognition_id: int = Field(..., description="ID of the recognition type")
    recognized_registry_did: str = Field(..., description="DID of the recognized registry/ecosystem")
    recognized: bool = Field(True, description="Whether this is recognized (true) or explicitly not recognized (false)")
    valid_from: Optional[str] = Field(None, description="ISO 8601 datetime when recognition starts")
    valid_until: Optional[str] = Field(None, description="ISO 8601 datetime when recognition expires")


class EntityRecognitionResponse(BaseModel):
    recognition_id: int
    recognized_registry_did: str
    recognized: bool
    valid_from: Optional[str]
    valid_until: Optional[str]
    action: str
    resource: str
    description: Optional[str]


class EntityCreate(BaseModel):
    entity_did: str = Field(..., description="DID URI of the entity")
    authority_id: Optional[str] = Field(None, description="DID of the authority/ecosystem (optional for root ecosystems)")
    name: Optional[str] = Field(None, description="Human-readable name")
    entity_type: Optional[str] = Field(None, description="Type of entity (ecosystem, organization, person, etc.)")
    status: str = Field("active", description="Status (active, inactive, suspended)")
    description: Optional[str] = Field(None, description="Description of the entity")
    authorization_ids: Optional[List[int]] = Field(None, description="List of authorization IDs")


class EntityUpdate(BaseModel):
    entity_did: Optional[str] = None
    authority_id: Optional[str] = None
    name: Optional[str] = None
    entity_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    authorization_ids: Optional[List[int]] = None


class EntityResponse(BaseModel):
    id: int
    entity_did: str
    authority_id: Optional[str]
    name: Optional[str]
    entity_type: Optional[str]
    status: str
    description: Optional[str]
    authorizations: List[AuthorizationResponseAdmin]

    class Config:
        from_attributes = True


class RegistryConfigCreate(BaseModel):
    authority_id: str = Field(..., description="Default authority DID for entities")
    egf_id: Optional[str] = Field(None, description="Ecosystem Governance Framework DID")
    name: Optional[str] = Field(None, description="Registry name")
    description: Optional[str] = Field(None, description="Registry description")


class RegistryConfigResponse(BaseModel):
    authority_id: str
    egf_id: Optional[str]
    name: Optional[str]
    description: Optional[str]


# Registry Configuration
@router.get("/registry-config", response_model=RegistryConfigResponse)
async def get_registry_config(db: Session = Depends(get_db)):
    """Get registry configuration"""
    # For now, we'll use a simple config stored as a single-row table
    # In a real implementation, you might want to use a config file or environment variables
    config = db.execute(
        text("SELECT authority_id, egf_id, name, description FROM registry_config LIMIT 1")
    ).fetchone()

    if config:
        return RegistryConfigResponse(
            authority_id=config[0],
            egf_id=config[1],
            name=config[2],
            description=config[3]
        )

    # Return default config if none exists
    return RegistryConfigResponse(
        authority_id="did:example:ecosystem456",
        egf_id="did:example:egf789",
        name="Ayra Trust Registry",
        description="Trust Registry for Ayra Network"
    )


@router.post("/registry-config", response_model=RegistryConfigResponse)
async def save_registry_config(config: RegistryConfigCreate, db: Session = Depends(get_db)):
    """Save registry configuration"""
    try:
        # Validate DIDs
        if not config.authority_id.startswith("did:"):
            raise HTTPException(status_code=400, detail="authority_id must be a valid DID URI")
        if config.egf_id and not config.egf_id.startswith("did:"):
            raise HTTPException(status_code=400, detail="egf_id must be a valid DID URI")

        # Validate that authority_id exists as an active ecosystem entity
        authority_entity = crud.get_entity_by_did(db, config.authority_id)
        if not authority_entity:
            raise HTTPException(status_code=400, detail="authority_id must reference an existing entity")
        if authority_entity.status != "active":
            raise HTTPException(status_code=400, detail="authority_id must reference an active entity")
        if authority_entity.entity_type != "ecosystem":
            raise HTTPException(status_code=400, detail="authority_id must reference an ecosystem entity")

        # Delete existing config and insert new one (simple upsert)
        db.execute(text("DELETE FROM registry_config"))
        db.execute(
            text("""INSERT INTO registry_config (authority_id, egf_id, name, description)
                    VALUES (:authority_id, :egf_id, :name, :description)"""),
            {
                "authority_id": config.authority_id,
                "egf_id": config.egf_id,
                "name": config.name,
                "description": config.description
            }
        )
        db.commit()

        return RegistryConfigResponse(
            authority_id=config.authority_id,
            egf_id=config.egf_id,
            name=config.name,
            description=config.description
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error saving configuration: {str(e)}")


# DID Methods Management
@router.get("/did-methods", response_model=List[DIDMethodResponse])
async def list_did_methods(db: Session = Depends(get_db)):
    """List all DID methods"""
    return crud.get_did_methods(db)


@router.post("/did-methods", response_model=DIDMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_did_method(method: DIDMethodCreate, db: Session = Depends(get_db)):
    """Create a new DID method"""
    try:
        return crud.create_did_method(
            db,
            identifier=method.identifier,
            egf_did=method.egf_did,
            maximum_assurance_level=method.maximum_assurance_level,
            description=method.description
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating DID method: {str(e)}")


@router.put("/did-methods/{method_id}", response_model=DIDMethodResponse)
async def update_did_method(method_id: int, method: DIDMethodUpdate, db: Session = Depends(get_db)):
    """Update a DID method"""
    updated = crud.update_did_method(db, method_id, **method.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="DID method not found")
    return updated


@router.delete("/did-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_did_method(method_id: int, db: Session = Depends(get_db)):
    """Delete a DID method"""
    if not crud.delete_did_method(db, method_id):
        raise HTTPException(status_code=404, detail="DID method not found")


# Assurance Levels Management
@router.get("/assurance-levels", response_model=List[AssuranceLevelResponseAdmin])
async def list_assurance_levels(db: Session = Depends(get_db)):
    """List all assurance levels"""
    return crud.get_assurance_levels(db)


@router.post("/assurance-levels", response_model=AssuranceLevelResponseAdmin, status_code=status.HTTP_201_CREATED)
async def create_assurance_level(level: AssuranceLevelCreate, db: Session = Depends(get_db)):
    """Create a new assurance level"""
    try:
        return crud.create_assurance_level(
            db,
            identifier=level.identifier,
            name=level.name,
            description=level.description,
            egf_did=level.egf_did
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating assurance level: {str(e)}")


@router.put("/assurance-levels/{level_id}", response_model=AssuranceLevelResponseAdmin)
async def update_assurance_level(level_id: int, level: AssuranceLevelUpdate, db: Session = Depends(get_db)):
    """Update an assurance level"""
    updated = crud.update_assurance_level(db, level_id, **level.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Assurance level not found")
    return updated


@router.delete("/assurance-levels/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assurance_level(level_id: int, db: Session = Depends(get_db)):
    """Delete an assurance level"""
    if not crud.delete_assurance_level(db, level_id):
        raise HTTPException(status_code=404, detail="Assurance level not found")


# Authorizations Management
@router.get("/authorizations", response_model=List[AuthorizationResponseAdmin])
async def list_authorizations_admin(db: Session = Depends(get_db)):
    """List all authorizations"""
    return crud.get_authorizations(db)


@router.post("/authorizations", response_model=AuthorizationResponseAdmin, status_code=status.HTTP_201_CREATED)
async def create_authorization(auth: AuthorizationCreate, db: Session = Depends(get_db)):
    """Create a new authorization (action+resource pair)"""
    try:
        return crud.create_authorization(
            db,
            action=auth.action,
            resource=auth.resource,
            description=auth.description
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating authorization: {str(e)}")


@router.put("/authorizations/{auth_id}", response_model=AuthorizationResponseAdmin)
async def update_authorization(auth_id: int, auth: AuthorizationUpdate, db: Session = Depends(get_db)):
    """Update an authorization"""
    updated = crud.update_authorization(db, auth_id, **auth.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Authorization not found")
    return updated


@router.delete("/authorizations/{auth_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_authorization(auth_id: int, db: Session = Depends(get_db)):
    """Delete an authorization"""
    if not crud.delete_authorization(db, auth_id):
        raise HTTPException(status_code=404, detail="Authorization not found")


# Recognitions Management
@router.get("/recognitions", response_model=List[RecognitionResponseAdmin])
async def list_recognitions_admin(db: Session = Depends(get_db)):
    """List all recognitions"""
    return crud.get_recognitions(db)


@router.post("/recognitions", response_model=RecognitionResponseAdmin, status_code=status.HTTP_201_CREATED)
async def create_recognition(recog: RecognitionCreate, db: Session = Depends(get_db)):
    """Create a new recognition (action+resource pair)"""
    try:
        return crud.create_recognition(
            db,
            action=recog.action,
            resource=recog.resource,
            description=recog.description
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating recognition: {str(e)}")


@router.put("/recognitions/{recognition_id}", response_model=RecognitionResponseAdmin)
async def update_recognition(recognition_id: int, recog: RecognitionUpdate, db: Session = Depends(get_db)):
    """Update a recognition"""
    updated = crud.update_recognition(db, recognition_id, **recog.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Recognition not found")
    return updated


@router.delete("/recognitions/{recognition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recognition(recognition_id: int, db: Session = Depends(get_db)):
    """Delete a recognition"""
    if not crud.delete_recognition(db, recognition_id):
        raise HTTPException(status_code=404, detail="Recognition not found")


# Entities Management
@router.get("/entities/active-authorities", response_model=List[dict])
async def list_active_authorities(db: Session = Depends(get_db)):
    """List all active ecosystem entities that can be used as authorities"""
    entities = db.query(crud.Entity).filter(
        crud.Entity.status == "active",
        crud.Entity.entity_type == "ecosystem"
    ).all()
    return [
        {
            "id": e.id,
            "entity_did": e.entity_did,
            "name": e.name or e.entity_did
        }
        for e in entities
    ]


@router.get("/entities", response_model=List[EntityResponse])
async def list_entities(authority_id: Optional[str] = None, db: Session = Depends(get_db)):
    """List all entities, optionally filtered by authority"""
    return crud.get_entities(db, authority_id)


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Get a specific entity by ID"""
    entity = crud.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    """Create a new entity with authorizations"""
    try:
        # Validate that entity_did is a DID
        if not entity.entity_did.startswith("did:"):
            raise HTTPException(status_code=400, detail="entity_did must be a valid DID URI")

        # Check if entity already exists
        existing = crud.get_entity_by_did(db, entity.entity_did)
        if existing:
            raise HTTPException(status_code=400, detail="Entity with this DID already exists")

        # Validate authority_id if provided
        if entity.authority_id:
            # authority_id must be a valid DID
            if not entity.authority_id.startswith("did:"):
                raise HTTPException(status_code=400, detail="authority_id must be a valid DID URI")

            # Validate that authority_id exists as an active ecosystem entity
            authority_entity = crud.get_entity_by_did(db, entity.authority_id)
            if not authority_entity:
                raise HTTPException(status_code=400, detail="authority_id must reference an existing entity")
            if authority_entity.status != "active":
                raise HTTPException(status_code=400, detail="authority_id must reference an active entity")
            if authority_entity.entity_type != "ecosystem":
                raise HTTPException(status_code=400, detail="authority_id must reference an ecosystem entity")
        elif entity.entity_type != "ecosystem":
            # Non-ecosystem entities must have an authority
            raise HTTPException(status_code=400, detail="Non-ecosystem entities must have an authority_id")

        return crud.create_entity(
            db,
            entity_did=entity.entity_did,
            authority_id=entity.authority_id,
            name=entity.name,
            entity_type=entity.entity_type,
            status=entity.status,
            description=entity.description,
            authorization_ids=entity.authorization_ids
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating entity: {str(e)}")


@router.put("/entities/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: int, entity: EntityUpdate, db: Session = Depends(get_db)):
    """Update an entity"""
    try:
        # Get entity data including only fields that were explicitly set
        entity_data = entity.dict(exclude_unset=True)

        # Validate DIDs if provided
        if entity.entity_did and not entity.entity_did.startswith("did:"):
            raise HTTPException(status_code=400, detail="entity_did must be a valid DID URI")

        # Validate authority_id if it's being changed
        if "authority_id" in entity_data:
            if entity_data["authority_id"]:  # Has a value (not None or empty string)
                # authority_id must be a valid DID
                if not entity_data["authority_id"].startswith("did:"):
                    raise HTTPException(status_code=400, detail="authority_id must be a valid DID URI")

                # Validate that authority_id exists as an active ecosystem entity
                authority_entity = crud.get_entity_by_did(db, entity_data["authority_id"])
                if not authority_entity:
                    raise HTTPException(status_code=400, detail="authority_id must reference an existing entity")
                if authority_entity.status != "active":
                    raise HTTPException(status_code=400, detail="authority_id must reference an active entity")
                if authority_entity.entity_type != "ecosystem":
                    raise HTTPException(status_code=400, detail="authority_id must reference an ecosystem entity")
            else:
                # Removing authority (setting to None) - get current entity to check if it's an ecosystem
                current_entity = crud.get_entity(db, entity_id)
                if not current_entity:
                    raise HTTPException(status_code=404, detail="Entity not found")

                # Determine the entity type to use for validation
                # If entity_type is being updated, use the new type; otherwise use the current type
                entity_type_for_validation = entity_data.get("entity_type", current_entity.entity_type)

                if entity_type_for_validation != "ecosystem":
                    raise HTTPException(status_code=400, detail="Non-ecosystem entities must have an authority_id")

        updated = crud.update_entity(db, entity_id, **entity_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Entity not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating entity: {str(e)}")


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    """Delete an entity"""
    if not crud.delete_entity(db, entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")


@router.post("/entities/{entity_id}/authorizations/{auth_id}", response_model=EntityResponse)
async def add_entity_authorization(entity_id: int, auth_id: int, db: Session = Depends(get_db)):
    """Add an authorization to an entity"""
    entity = crud.add_entity_authorization(db, entity_id, auth_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity or authorization not found")
    return entity


@router.delete("/entities/{entity_id}/authorizations/{auth_id}", response_model=EntityResponse)
async def remove_entity_authorization(entity_id: int, auth_id: int, db: Session = Depends(get_db)):
    """Remove an authorization from an entity"""
    entity = crud.remove_entity_authorization(db, entity_id, auth_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity or authorization not found")
    return entity


# Entity Recognition Association Endpoints
@router.get("/entities/{entity_id}/recognitions", response_model=List[EntityRecognitionResponse])
async def list_entity_recognitions(entity_id: int, db: Session = Depends(get_db)):
    """List all recognitions for an entity (ecosystem)"""
    entity = crud.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    if entity.entity_type != "ecosystem":
        raise HTTPException(status_code=400, detail="Only ecosystems can have recognitions")

    recognitions = crud.get_entity_recognitions(db, entity_id)
    return recognitions


@router.post("/entities/{entity_id}/recognitions")
async def add_entity_recognition(
    entity_id: int,
    recog_create: EntityRecognitionCreate,
    db: Session = Depends(get_db)
):
    """Add a recognition to an entity (ecosystem)"""
    from datetime import datetime

    # Get the entity to check its DID
    entity = crud.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Entity not found"
        )

    # Validate that the entity is an ecosystem
    if entity.entity_type != "ecosystem":
        raise HTTPException(
            status_code=400,
            detail="Only ecosystems can have recognitions"
        )

    # Prevent self-reference
    if entity.entity_did == recog_create.recognized_registry_did:
        raise HTTPException(
            status_code=400,
            detail="An entity cannot recognize itself"
        )

    # Validate that the recognized registry DID exists in the system
    recognized_entity = crud.get_entity_by_did(db, recog_create.recognized_registry_did)
    if not recognized_entity:
        raise HTTPException(
            status_code=400,
            detail=f"Recognized registry DID '{recog_create.recognized_registry_did}' does not exist in the system"
        )

    # Parse datetime strings if provided
    valid_from = None
    valid_until = None
    if recog_create.valid_from:
        try:
            valid_from = datetime.fromisoformat(recog_create.valid_from.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid valid_from datetime format")

    if recog_create.valid_until:
        try:
            valid_until = datetime.fromisoformat(recog_create.valid_until.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid valid_until datetime format")

    entity = crud.add_entity_recognition(
        db,
        entity_id=entity_id,
        recognition_id=recog_create.recognition_id,
        recognized_registry_did=recog_create.recognized_registry_did,
        recognized=recog_create.recognized,
        valid_from=valid_from,
        valid_until=valid_until
    )

    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Entity or recognition not found"
        )

    return {"message": "Recognition added successfully", "entity_id": entity_id}


@router.delete("/entities/{entity_id}/recognitions/{recognition_id}")
async def remove_entity_recognition(
    entity_id: int,
    recognition_id: int,
    recognized_registry_did: str,
    db: Session = Depends(get_db)
):
    """Remove a recognition from an entity"""
    entity = crud.remove_entity_recognition(db, entity_id, recognition_id, recognized_registry_did)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity or recognition not found")

    return {"message": "Recognition removed successfully", "entity_id": entity_id}


# ===== TRQP Endpoints Admin =====

class TrqpEndpointCreate(BaseModel):
    name: str = Field(..., description="Friendly name for the TRQP endpoint")
    base_url: str = Field(..., description="Base URL of the TRQP API")
    description: Optional[str] = Field(None, description="Description of the endpoint")
    is_active: bool = Field(True, description="Whether the endpoint is active")


class TrqpEndpointUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TrqpEndpointResponse(BaseModel):
    id: int
    name: str
    base_url: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/trqp-endpoints", response_model=List[TrqpEndpointResponse])
async def list_trqp_endpoints(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all TRQP endpoints"""
    endpoints = crud.get_trqp_endpoints(db, active_only=active_only)
    return endpoints


@router.get("/trqp-endpoints/{endpoint_id}", response_model=TrqpEndpointResponse)
async def get_trqp_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific TRQP endpoint"""
    endpoint = crud.get_trqp_endpoint(db, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="TRQP endpoint not found")
    return endpoint


@router.post("/trqp-endpoints", response_model=TrqpEndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_trqp_endpoint(
    endpoint_data: TrqpEndpointCreate,
    db: Session = Depends(get_db)
):
    """Create a new TRQP endpoint"""
    endpoint = crud.create_trqp_endpoint(
        db,
        name=endpoint_data.name,
        base_url=endpoint_data.base_url,
        description=endpoint_data.description,
        is_active=endpoint_data.is_active
    )
    return endpoint


@router.put("/trqp-endpoints/{endpoint_id}", response_model=TrqpEndpointResponse)
async def update_trqp_endpoint(
    endpoint_id: int,
    endpoint_data: TrqpEndpointUpdate,
    db: Session = Depends(get_db)
):
    """Update a TRQP endpoint"""
    update_data = endpoint_data.dict(exclude_unset=True)
    endpoint = crud.update_trqp_endpoint(db, endpoint_id, **update_data)
    if not endpoint:
        raise HTTPException(status_code=404, detail="TRQP endpoint not found")
    return endpoint


@router.delete("/trqp-endpoints/{endpoint_id}")
async def delete_trqp_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db)
):
    """Delete a TRQP endpoint"""
    success = crud.delete_trqp_endpoint(db, endpoint_id)
    if not success:
        raise HTTPException(status_code=404, detail="TRQP endpoint not found")
    return {"message": "TRQP endpoint deleted successfully"}


# ===== TRQP Proxy (to avoid CORS issues) =====

class TrqpProxyRequest(BaseModel):
    base_url: str = Field(..., description="Base URL of the TRQP endpoint")
    entity_id: str = Field(..., description="Entity DID to query")
    authority_id: str = Field(..., description="Authority DID")
    action: str = Field(..., description="Action to check")
    resource: str = Field(..., description="Resource to check")


@router.post("/trqp-proxy/authorization")
async def proxy_trqp_authorization(request: TrqpProxyRequest):
    """
    Proxy a TRQP authorization request to avoid CORS issues.
    Makes the request server-side and returns the result.
    """
    import httpx

    target_url = f"{request.base_url.rstrip('/')}/authorization"

    payload = {
        "entity_id": request.entity_id,
        "authority_id": request.authority_id,
        "action": request.action,
        "resource": request.resource
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                target_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            # Return the response from the remote server
            return {
                "success": True,
                "status_code": response.status_code,
                "target_url": target_url,
                "request_payload": payload,
                "response": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else response.text
            }
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail={
                "success": False,
                "target_url": target_url,
                "request_payload": payload,
                "error": "Request timed out"
            }
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "target_url": target_url,
                "request_payload": payload,
                "error": f"Connection error: {str(e)}"
            }
        )
