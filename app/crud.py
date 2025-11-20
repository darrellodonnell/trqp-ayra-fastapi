"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import (
    DIDMethod, AssuranceLevel, Authorization, Entity,
    Recognition, EcosystemRecognition, TrustRegistryConfig,
    TrqpEndpoint,
    entity_recognitions
)


# DID Methods CRUD
def get_did_methods(db: Session, egf_did: Optional[str] = None) -> List[DIDMethod]:
    """Get all DID methods, optionally filtered by EGF DID"""
    query = db.query(DIDMethod)
    if egf_did:
        query = query.filter(DIDMethod.egf_did == egf_did)
    return query.all()


def get_did_method(db: Session, method_id: int) -> Optional[DIDMethod]:
    """Get a specific DID method by ID"""
    return db.query(DIDMethod).filter(DIDMethod.id == method_id).first()


def create_did_method(db: Session, identifier: str, egf_did: Optional[str] = None,
                      maximum_assurance_level: Optional[str] = None,
                      description: Optional[str] = None) -> DIDMethod:
    """Create a new DID method"""
    did_method = DIDMethod(
        identifier=identifier,
        egf_did=egf_did,
        maximum_assurance_level=maximum_assurance_level,
        description=description
    )
    db.add(did_method)
    db.commit()
    db.refresh(did_method)
    return did_method


def update_did_method(db: Session, method_id: int, **kwargs) -> Optional[DIDMethod]:
    """Update a DID method"""
    did_method = get_did_method(db, method_id)
    if did_method:
        for key, value in kwargs.items():
            if hasattr(did_method, key):
                setattr(did_method, key, value)
        db.commit()
        db.refresh(did_method)
    return did_method


def delete_did_method(db: Session, method_id: int) -> bool:
    """Delete a DID method"""
    did_method = get_did_method(db, method_id)
    if did_method:
        db.delete(did_method)
        db.commit()
        return True
    return False


# Assurance Levels CRUD
def get_assurance_levels(db: Session, egf_did: Optional[str] = None) -> List[AssuranceLevel]:
    """Get all assurance levels, optionally filtered by EGF DID"""
    query = db.query(AssuranceLevel)
    if egf_did:
        query = query.filter(AssuranceLevel.egf_did == egf_did)
    return query.all()


def get_assurance_level(db: Session, level_id: int) -> Optional[AssuranceLevel]:
    """Get a specific assurance level by ID"""
    return db.query(AssuranceLevel).filter(AssuranceLevel.id == level_id).first()


def create_assurance_level(db: Session, identifier: str, name: str, description: str,
                          egf_did: Optional[str] = None) -> AssuranceLevel:
    """Create a new assurance level"""
    assurance_level = AssuranceLevel(
        identifier=identifier,
        name=name,
        description=description,
        egf_did=egf_did
    )
    db.add(assurance_level)
    db.commit()
    db.refresh(assurance_level)
    return assurance_level


def update_assurance_level(db: Session, level_id: int, **kwargs) -> Optional[AssuranceLevel]:
    """Update an assurance level"""
    assurance_level = get_assurance_level(db, level_id)
    if assurance_level:
        for key, value in kwargs.items():
            if hasattr(assurance_level, key):
                setattr(assurance_level, key, value)
        db.commit()
        db.refresh(assurance_level)
    return assurance_level


def delete_assurance_level(db: Session, level_id: int) -> bool:
    """Delete an assurance level"""
    assurance_level = get_assurance_level(db, level_id)
    if assurance_level:
        db.delete(assurance_level)
        db.commit()
        return True
    return False


# Authorizations CRUD
def get_authorizations(db: Session, ecosystem_did: Optional[str] = None) -> List[Authorization]:
    """Get all authorizations"""
    return db.query(Authorization).all()


def get_authorization(db: Session, auth_id: int) -> Optional[Authorization]:
    """Get a specific authorization by ID"""
    return db.query(Authorization).filter(Authorization.id == auth_id).first()


def get_authorization_by_action_resource(db: Session, action: str, resource: str) -> Optional[Authorization]:
    """Get authorization by action and resource"""
    return db.query(Authorization).filter(
        Authorization.action == action,
        Authorization.resource == resource
    ).first()


def create_authorization(db: Session, action: str, resource: str,
                        description: Optional[str] = None) -> Authorization:
    """Create a new authorization"""
    authorization = Authorization(
        action=action,
        resource=resource,
        description=description
    )
    db.add(authorization)
    db.commit()
    db.refresh(authorization)
    return authorization


def update_authorization(db: Session, auth_id: int, **kwargs) -> Optional[Authorization]:
    """Update an authorization"""
    authorization = get_authorization(db, auth_id)
    if authorization:
        for key, value in kwargs.items():
            if hasattr(authorization, key):
                setattr(authorization, key, value)
        db.commit()
        db.refresh(authorization)
    return authorization


def delete_authorization(db: Session, auth_id: int) -> bool:
    """Delete an authorization"""
    authorization = get_authorization(db, auth_id)
    if authorization:
        db.delete(authorization)
        db.commit()
        return True
    return False


# Recognitions CRUD
def get_recognitions(db: Session) -> List[Recognition]:
    """Get all recognitions"""
    return db.query(Recognition).all()


def get_recognition(db: Session, recognition_id: int) -> Optional[Recognition]:
    """Get a specific recognition by ID"""
    return db.query(Recognition).filter(Recognition.id == recognition_id).first()


def get_recognition_by_action_resource(db: Session, action: str, resource: str) -> Optional[Recognition]:
    """Get recognition by action and resource"""
    return db.query(Recognition).filter(
        Recognition.action == action,
        Recognition.resource == resource
    ).first()


def create_recognition(db: Session, action: str, resource: str,
                      description: Optional[str] = None) -> Recognition:
    """Create a new recognition"""
    recognition = Recognition(
        action=action,
        resource=resource,
        description=description
    )
    db.add(recognition)
    db.commit()
    db.refresh(recognition)
    return recognition


def update_recognition(db: Session, recognition_id: int, **kwargs) -> Optional[Recognition]:
    """Update a recognition"""
    recognition = get_recognition(db, recognition_id)
    if recognition:
        for key, value in kwargs.items():
            if hasattr(recognition, key):
                setattr(recognition, key, value)
        db.commit()
        db.refresh(recognition)
    return recognition


def delete_recognition(db: Session, recognition_id: int) -> bool:
    """Delete a recognition"""
    recognition = get_recognition(db, recognition_id)
    if recognition:
        db.delete(recognition)
        db.commit()
        return True
    return False


# Entities CRUD
def get_entities(db: Session, authority_id: Optional[str] = None) -> List[Entity]:
    """Get all entities, optionally filtered by authority"""
    query = db.query(Entity)
    if authority_id:
        query = query.filter(Entity.authority_id == authority_id)
    return query.all()


def get_entity(db: Session, entity_id: int) -> Optional[Entity]:
    """Get a specific entity by ID"""
    return db.query(Entity).filter(Entity.id == entity_id).first()


def get_entity_by_did(db: Session, entity_did: str) -> Optional[Entity]:
    """Get entity by DID"""
    return db.query(Entity).filter(Entity.entity_did == entity_did).first()


def create_entity(db: Session, entity_did: str, authority_id: str,
                 name: Optional[str] = None, entity_type: Optional[str] = None,
                 status: str = "active", description: Optional[str] = None,
                 authorization_ids: Optional[List[int]] = None) -> Entity:
    """Create a new entity with authorizations"""
    entity = Entity(
        entity_did=entity_did,
        authority_id=authority_id,
        name=name,
        entity_type=entity_type,
        status=status,
        description=description
    )

    # Add authorizations if provided
    if authorization_ids:
        authorizations = db.query(Authorization).filter(Authorization.id.in_(authorization_ids)).all()
        entity.authorizations = authorizations

    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_entity(db: Session, entity_id: int, authorization_ids: Optional[List[int]] = None,
                 **kwargs) -> Optional[Entity]:
    """Update an entity"""
    entity = get_entity(db, entity_id)
    if entity:
        # Update regular fields
        for key, value in kwargs.items():
            if hasattr(entity, key) and key != 'authorizations':
                setattr(entity, key, value)

        # Update authorizations if provided
        if authorization_ids is not None:
            authorizations = db.query(Authorization).filter(Authorization.id.in_(authorization_ids)).all()
            entity.authorizations = authorizations

        db.commit()
        db.refresh(entity)
    return entity


def delete_entity(db: Session, entity_id: int) -> bool:
    """Delete an entity"""
    entity = get_entity(db, entity_id)
    if entity:
        db.delete(entity)
        db.commit()
        return True
    return False


def add_entity_authorization(db: Session, entity_id: int, authorization_id: int) -> Optional[Entity]:
    """Add an authorization to an entity"""
    entity = get_entity(db, entity_id)
    authorization = get_authorization(db, authorization_id)

    if entity and authorization:
        if authorization not in entity.authorizations:
            entity.authorizations.append(authorization)
            db.commit()
            db.refresh(entity)
    return entity


def remove_entity_authorization(db: Session, entity_id: int, authorization_id: int) -> Optional[Entity]:
    """Remove an authorization from an entity"""
    entity = get_entity(db, entity_id)
    authorization = get_authorization(db, authorization_id)

    if entity and authorization:
        if authorization in entity.authorizations:
            entity.authorizations.remove(authorization)
            db.commit()
            db.refresh(entity)
    return entity


# Trust Registry Config CRUD
def get_trust_registry_config(db: Session, ecosystem_did: Optional[str] = None) -> Optional[TrustRegistryConfig]:
    """Get trust registry configuration"""
    query = db.query(TrustRegistryConfig)
    if ecosystem_did:
        return query.filter(TrustRegistryConfig.ecosystem_did == ecosystem_did).first()
    return query.first()


def create_or_update_trust_registry_config(db: Session, ecosystem_did: str, **kwargs) -> TrustRegistryConfig:
    """Create or update trust registry configuration"""
    config = get_trust_registry_config(db, ecosystem_did)

    if config:
        # Update existing
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    else:
        # Create new
        config = TrustRegistryConfig(ecosystem_did=ecosystem_did, **kwargs)
        db.add(config)

    db.commit()
    db.refresh(config)
    return config


# Query operations for TRQP endpoints
def check_entity_authorization(db: Session, entity_did: str, authority_id: str,
                              action: str, resource: str) -> bool:
    """Check if an entity has a specific authorization"""
    entity = db.query(Entity).filter(
        Entity.entity_did == entity_did,
        Entity.authority_id == authority_id,
        Entity.status == "active"
    ).first()

    if not entity:
        return False

    # Check if entity has the authorization
    for auth in entity.authorizations:
        if auth.action == action and auth.resource == resource:
            return True

    return False


def get_entity_authorizations_list(db: Session, entity_did: str, authority_id: str) -> List[Authorization]:
    """Get all authorizations for an entity"""
    entity = db.query(Entity).filter(
        Entity.entity_did == entity_did,
        Entity.authority_id == authority_id
    ).first()

    return entity.authorizations if entity else []


# Entity Recognition operations
def add_entity_recognition(db: Session, entity_id: int, recognition_id: int,
                          recognized_registry_did: str, recognized: bool = True,
                          valid_from: Optional[datetime] = None,
                          valid_until: Optional[datetime] = None) -> Optional[Entity]:
    """Add a recognition to an entity (ecosystem)"""
    from sqlalchemy import insert

    entity = get_entity(db, entity_id)
    recognition = get_recognition(db, recognition_id)

    if entity and recognition:
        # Check if entity is an ecosystem
        if entity.entity_type != "ecosystem":
            return None  # Only ecosystems can have recognitions

        # Insert into entity_recognitions table
        stmt = insert(entity_recognitions).values(
            entity_id=entity_id,
            recognition_id=recognition_id,
            recognized_registry_did=recognized_registry_did,
            recognized=recognized,
            valid_from=valid_from,
            valid_until=valid_until
        )
        db.execute(stmt)
        db.commit()
        db.refresh(entity)
    return entity


def remove_entity_recognition(db: Session, entity_id: int, recognition_id: int,
                              recognized_registry_did: str) -> Optional[Entity]:
    """Remove a recognition from an entity"""
    from sqlalchemy import delete

    entity = get_entity(db, entity_id)
    if entity:
        stmt = delete(entity_recognitions).where(
            entity_recognitions.c.entity_id == entity_id,
            entity_recognitions.c.recognition_id == recognition_id,
            entity_recognitions.c.recognized_registry_did == recognized_registry_did
        )
        db.execute(stmt)
        db.commit()
        db.refresh(entity)
    return entity


def get_entity_recognitions(db: Session, entity_id: int) -> List[dict]:
    """Get all recognitions for an entity with details"""
    from sqlalchemy import select

    stmt = select(
        entity_recognitions.c.recognition_id,
        entity_recognitions.c.recognized_registry_did,
        entity_recognitions.c.recognized,
        entity_recognitions.c.valid_from,
        entity_recognitions.c.valid_until,
        Recognition.action,
        Recognition.resource,
        Recognition.description
    ).join(
        Recognition,
        entity_recognitions.c.recognition_id == Recognition.id
    ).where(
        entity_recognitions.c.entity_id == entity_id
    )

    results = db.execute(stmt).fetchall()

    return [
        {
            "recognition_id": r.recognition_id,
            "recognized_registry_did": r.recognized_registry_did,
            "recognized": r.recognized,
            "valid_from": r.valid_from.isoformat() if r.valid_from else None,
            "valid_until": r.valid_until.isoformat() if r.valid_until else None,
            "action": r.action,
            "resource": r.resource,
            "description": r.description
        }
        for r in results
    ]


def check_ecosystem_recognition(db: Session, recognizing_ecosystem_did: str,
                                recognized_registry_did: str,
                                action: str, resource: str,
                                check_time: Optional[datetime] = None) -> bool:
    """Check if an ecosystem recognizes another registry for a specific action+resource"""
    from sqlalchemy import select

    if check_time is None:
        check_time = datetime.utcnow()

    # Get the recognizing ecosystem entity
    ecosystem = db.query(Entity).filter(
        Entity.entity_did == recognizing_ecosystem_did,
        Entity.entity_type == "ecosystem",
        Entity.status == "active"
    ).first()

    if not ecosystem:
        return False

    # Check if the ecosystem has the recognition
    stmt = select(entity_recognitions).join(
        Recognition,
        entity_recognitions.c.recognition_id == Recognition.id
    ).where(
        entity_recognitions.c.entity_id == ecosystem.id,
        entity_recognitions.c.recognized_registry_did == recognized_registry_did,
        entity_recognitions.c.recognized == True,
        (entity_recognitions.c.valid_from == None) | (entity_recognitions.c.valid_from <= check_time),
        (entity_recognitions.c.valid_until == None) | (entity_recognitions.c.valid_until >= check_time),    
        Recognition.action == action,
        Recognition.resource == resource
    )

    result = db.execute(stmt).fetchone()

    # Temporal validity is already checked in the SQL WHERE clause
    return result is not None


def get_ecosystem_recognitions_list(db: Session, ecosystem_did: str,
                                   check_time: Optional[datetime] = None) -> List[dict]:
    """Get all active recognitions for an ecosystem"""
    from sqlalchemy import select

    if check_time is None:
        check_time = datetime.utcnow()

    ecosystem = db.query(Entity).filter(
        Entity.entity_did == ecosystem_did,
        Entity.entity_type == "ecosystem"
    ).first()

    if not ecosystem:
        return []

    stmt = select(
        entity_recognitions.c.recognized_registry_did,
        entity_recognitions.c.recognized,
        entity_recognitions.c.valid_from,
        entity_recognitions.c.valid_until,
        Recognition.action,
        Recognition.resource,
        Recognition.description
    ).join(
        Recognition,
        entity_recognitions.c.recognition_id == Recognition.id
    ).where(
        entity_recognitions.c.entity_id == ecosystem.id,
        entity_recognitions.c.recognized == True
    )

    results = db.execute(stmt).fetchall()

    # Filter by temporal validity
    valid_results = []
    for r in results:
        if r.valid_from and r.valid_from > check_time:
            continue
        if r.valid_until and r.valid_until < check_time:
            continue
        valid_results.append({
            "recognized_registry_did": r.recognized_registry_did,
            "action": r.action,
            "resource": r.resource,
            "description": r.description,
            "valid_from": r.valid_from,
            "valid_until": r.valid_until
        })

    return valid_results


# TRQP Endpoints CRUD
def get_trqp_endpoints(db: Session, active_only: bool = False) -> List[TrqpEndpoint]:
    """Get all TRQP endpoints, optionally filtered by active status"""
    query = db.query(TrqpEndpoint)
    if active_only:
        query = query.filter(TrqpEndpoint.is_active == True)
    return query.order_by(TrqpEndpoint.name).all()


def get_trqp_endpoint(db: Session, endpoint_id: int) -> Optional[TrqpEndpoint]:
    """Get a specific TRQP endpoint by ID"""
    return db.query(TrqpEndpoint).filter(TrqpEndpoint.id == endpoint_id).first()


def create_trqp_endpoint(db: Session, name: str, base_url: str,
                         description: Optional[str] = None,
                         is_active: bool = True) -> TrqpEndpoint:
    """Create a new TRQP endpoint"""
    endpoint = TrqpEndpoint(
        name=name,
        base_url=base_url.rstrip('/'),  # Remove trailing slash if present
        description=description,
        is_active=is_active
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


def update_trqp_endpoint(db: Session, endpoint_id: int, **kwargs) -> Optional[TrqpEndpoint]:
    """Update a TRQP endpoint"""
    endpoint = get_trqp_endpoint(db, endpoint_id)
    if endpoint:
        # Normalize base_url if provided
        if 'base_url' in kwargs and kwargs['base_url']:
            kwargs['base_url'] = kwargs['base_url'].rstrip('/')

        for key, value in kwargs.items():
            if hasattr(endpoint, key):
                setattr(endpoint, key, value)
        db.commit()
        db.refresh(endpoint)
    return endpoint


def delete_trqp_endpoint(db: Session, endpoint_id: int) -> bool:
    """Delete a TRQP endpoint"""
    endpoint = get_trqp_endpoint(db, endpoint_id)
    if endpoint:
        db.delete(endpoint)
        db.commit()
        return True
    return False
