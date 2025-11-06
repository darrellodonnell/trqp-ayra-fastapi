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


router = APIRouter(prefix="/admin", tags=["admin"])


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


class EntityCreate(BaseModel):
    entity_did: str = Field(..., description="DID URI of the entity")
    authority_id: str = Field(..., description="DID of the authority/ecosystem")
    name: Optional[str] = Field(None, description="Human-readable name")
    entity_type: Optional[str] = Field(None, description="Type of entity (organization, person, etc.)")
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
    authority_id: str
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


# Entities Management
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
        # Validate that entity_did and authority_id are DIDs
        if not entity.entity_did.startswith("did:"):
            raise HTTPException(status_code=400, detail="entity_did must be a valid DID URI")
        if not entity.authority_id.startswith("did:"):
            raise HTTPException(status_code=400, detail="authority_id must be a valid DID URI")

        # Check if entity already exists
        existing = crud.get_entity_by_did(db, entity.entity_did)
        if existing:
            raise HTTPException(status_code=400, detail="Entity with this DID already exists")

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
        # Validate DIDs if provided
        if entity.entity_did and not entity.entity_did.startswith("did:"):
            raise HTTPException(status_code=400, detail="entity_did must be a valid DID URI")
        if entity.authority_id and not entity.authority_id.startswith("did:"):
            raise HTTPException(status_code=400, detail="authority_id must be a valid DID URI")

        updated = crud.update_entity(db, entity_id, **entity.dict(exclude_unset=True))
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
