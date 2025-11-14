"""
Database models and configuration
Uses SQLite for simplicity - can be easily swapped for PostgreSQL
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL - defaults to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trqp.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Association table for many-to-many relationship between entities and authorizations
entity_authorizations = Table(
    'entity_authorizations',
    Base.metadata,
    Column('entity_id', Integer, ForeignKey('entities.id'), primary_key=True),
    Column('authorization_id', Integer, ForeignKey('authorizations.id'), primary_key=True)
)

# Association table for many-to-many relationship between entities and recognitions
entity_recognitions = Table(
    'entity_recognitions',
    Base.metadata,
    Column('entity_id', Integer, ForeignKey('entities.id'), primary_key=True),
    Column('recognition_id', Integer, ForeignKey('recognitions.id'), primary_key=True),
    Column('recognized_registry_did', String, nullable=False),  # The registry being recognized
    Column('recognized', Boolean, default=True),  # Whether it's recognized or not
    Column('valid_from', DateTime, nullable=True),  # When recognition starts
    Column('valid_until', DateTime, nullable=True),  # When recognition expires
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)


class DIDMethod(Base):
    """DID Method supported by the trust registry"""
    __tablename__ = "did_methods"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True, nullable=False)
    egf_did = Column(String, nullable=True)
    maximum_assurance_level = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssuranceLevel(Base):
    """Assurance levels supported by the trust registry"""
    __tablename__ = "assurance_levels"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    egf_did = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Authorization(Base):
    """Authorization action+resource pairs"""
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False, index=True)
    resource = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entities = relationship("Entity", secondary=entity_authorizations, back_populates="authorizations")

    def __repr__(self):
        return f"<Authorization(action='{self.action}', resource='{self.resource}')>"


class Recognition(Base):
    """Recognition action+resource pairs - similar to authorizations but for ecosystem recognitions"""
    __tablename__ = "recognitions"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False, index=True)
    resource = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - using viewonly to avoid conflicts with the association table pattern
    entities = relationship(
        "Entity",
        secondary=entity_recognitions,
        back_populates="recognitions",
        viewonly=True
    )

    def __repr__(self):
        return f"<Recognition(action='{self.action}', resource='{self.resource}')>"


class Entity(Base):
    """Entities registered in the trust registry"""
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_did = Column(String, unique=True, index=True, nullable=False)
    authority_id = Column(String, nullable=True, index=True)  # Single DID for the authority (null for root ecosystems)
    name = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)  # ecosystem, organization, person, etc.
    status = Column(String, default="active")  # active, inactive, suspended
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    authorizations = relationship("Authorization", secondary=entity_authorizations, back_populates="entities")
    recognitions = relationship(
        "Recognition",
        secondary=entity_recognitions,
        back_populates="entities",
        viewonly=True
    )

    def __repr__(self):
        return f"<Entity(did='{self.entity_did}', authority='{self.authority_id}')>"


class EcosystemRecognition(Base):
    """Ecosystem recognition records"""
    __tablename__ = "ecosystem_recognitions"

    id = Column(Integer, primary_key=True, index=True)
    recognizing_ecosystem_did = Column(String, nullable=False, index=True)
    recognized_registry_did = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    recognized = Column(Boolean, default=False)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrustRegistryConfig(Base):
    """Trust Registry configuration and metadata"""
    __tablename__ = "trust_registry_config"

    id = Column(Integer, primary_key=True, index=True)
    ecosystem_did = Column(String, unique=True, nullable=False)
    trustregistry_did = Column(String, nullable=True)
    egf_did = Column(String, nullable=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    controllers = Column(Text, nullable=True)  # JSON string of controller DIDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RegistryConfig(Base):
    """Simple registry configuration for admin UI"""
    __tablename__ = "registry_config"

    id = Column(Integer, primary_key=True, index=True)
    authority_id = Column(String, nullable=False)
    egf_id = Column(String, nullable=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def seed_default_data():
    """Seed database with some default data"""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(DIDMethod).first():
            print("Database already seeded")
            return

        # Add default DID methods
        did_methods = [
            DIDMethod(identifier="web", description="DID Web Method"),
            DIDMethod(identifier="key", description="DID Key Method"),
            DIDMethod(identifier="peer", description="DID Peer Method"),
            DIDMethod(identifier="webvh", description="Web Verifiable History"),
        ]
        db.add_all(did_methods)

        # Add default assurance levels
        assurance_levels = [
            AssuranceLevel(
                identifier="urn:assurance:loa1",
                name="LOA1",
                description="Level of Assurance 1 - Basic identity verification"
            ),
            AssuranceLevel(
                identifier="urn:assurance:loa2",
                name="LOA2",
                description="Level of Assurance 2 - Enhanced identity verification with document validation"
            ),
            AssuranceLevel(
                identifier="urn:assurance:loa3",
                name="LOA3",
                description="Level of Assurance 3 - High assurance with in-person verification"
            ),
        ]
        db.add_all(assurance_levels)

        # Add default authorizations
        authorizations = [
            Authorization(
                action="issue",
                resource="ayracard:businesscard",
                description="Authorization to issue verifiable credentials"
            ),
            Authorization(
                action="manager-issuers",
                resource="ayracard:businesscard",
                description="Authorization to managed Issuers in their ecosystem"
            ),
            Authorization(
                action="root",
                resource="ayracard",
                description="Root authority for Ayra™ Card ecosystem"
            ),
            Authorization(
                action="issue",
                resource="PoP",
                description="Issue Proof of Person credentials"
            ),
        ]
        db.add_all(authorizations)

        # Add default recognitions
        recognitions = [
            Recognition(
                action="recognize-of",
                resource="ecosystem",
                description="Recognition of other ecosystems and their governance"
            ),
        ]
        db.add_all(recognitions)

        # Add default trust registry config
        config = TrustRegistryConfig(
            ecosystem_did="did:webvh:SCID-ATN:ayra.forum",
            trustregistry_did="did:webvh:SCID-ATNTR:ayra.forum/atntr",
            egf_did="did:webvh:SCID-ATNGF:ayra.forum/atngf",
            name="Ayra Trust Network Registry",
            description="Example Trust Registry for the Ayra Trust Network",
            controllers='["did:example:controller1", "did:example:controller2"]'
        )
        db.add(config)

        # Add default registry config for admin UI
        registry_config = RegistryConfig(
            authority_id="did:webvh:SCID-ATN:ayra.forum",
            egf_id="did:webvh:SCID-ATNGF:ayra.forum/atngf",
            name="Ayra Trust Registry",
            description="Default Trust Registry Configuration"
        )
        db.add(registry_config)

        db.commit()
        print("Database seeded successfully")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
