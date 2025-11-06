"""
Pydantic models for Ayra TRQP Profile API
Based on OpenAPI 3.0.3 specification
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class ProblemDetails(BaseModel):
    """
    A Problem Details object as defined in RFC 7807.
    https://datatracker.ietf.org/doc/html/rfc7807
    """
    type: Optional[str] = Field(None, description="A URI reference that identifies the problem type")
    title: Optional[str] = Field(None, description="A short, human-readable summary of the problem")
    status: Optional[int] = Field(None, description="The HTTP status code")
    detail: Optional[str] = Field(None, description="A human-readable explanation specific to this occurrence")
    instance: Optional[str] = Field(None, description="A URI reference that identifies the specific occurrence")

    class Config:
        extra = "allow"


class TrqpRecognitionQuery(BaseModel):
    """
    A query request to check if an ecosystem recognizes another trust registry.
    Conforms with TRQP 2.0 trqp_recognition_request.jsonschema
    """
    entity_id: str = Field(
        ...,
        description="Unique identifier of the TRUST REGISTRY (DID) that is the subject of the query"
    )
    authority_id: str = Field(
        ...,
        description="Unique identifier of the ECOSYSTEM (DID) that is being queried"
    )
    action: str = Field(..., description="The action that the query is checking Recognition for")
    resource: str = Field(..., description="The resource that the query is checking Recognition for")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="A flexible context object with arbitrary key-value pairs"
    )


class TrqpAuthorizationQuery(BaseModel):
    """
    A query request to check if an entity has authorization in an ecosystem.
    Conforms with TRQP 2.0 trqp_authorization_request.jsonschema
    """
    entity_id: str = Field(
        ...,
        description="Unique identifier of the entity (DID) that is the subject of the query"
    )
    authority_id: str = Field(
        ...,
        description="Unique identifier of the ECOSYSTEM (DID) that is being queried"
    )
    action: str = Field(..., description="The action that the query is checking Authorization for")
    resource: str = Field(..., description="The resource that the query is checking Authorization for")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="A flexible context object with arbitrary key-value pairs"
    )


class TrqpRecognitionResponse(BaseModel):
    """
    A recognition response conforming to TRQP 2.0 specification.
    """
    entity_id: str = Field(..., description="The identifier of the subject of the recognition query")
    authority_id: str = Field(..., description="The id of the Authority entity")
    action: str = Field(..., description="The action that the query is checking Recognition for")
    resource: str = Field(..., description="The resource that the query is checking Recognition for")
    recognized: bool = Field(..., description="True if the assertion has been verified, false otherwise")
    time_requested: Optional[datetime] = Field(None, description="The server time that was requested")
    time_evaluated: datetime = Field(..., description="The server time that was used in the query")
    message: Optional[str] = Field(None, description="Additional details about the assertion")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="The context object that was supplied for the query"
    )


class TrqpAuthorizationResponse(BaseModel):
    """
    An authorization response conforming to TRQP 2.0 specification.
    """
    entity_id: str = Field(..., description="The identifier of the subject of the authorization")
    authority_id: str = Field(..., description="The id of the Authority entity")
    action: str = Field(..., description="The action that the query is checking Authorization for")
    resource: str = Field(..., description="The resource that the query is checking Authorization for")
    assertion_verified: bool = Field(..., description="True if the assertion has been verified")
    time_requested: Optional[datetime] = Field(None, description="The server time that was requested")
    time_evaluated: datetime = Field(..., description="The server time that was used in the query")
    message: Optional[str] = Field(None, description="Additional details about the assertion")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="The context object that was supplied for the query"
    )


class TrustRegistryMetadata(BaseModel):
    """
    Trust Registry Metadata
    """
    ecosystem_did: str = Field(..., description="Unique identifier of the Ecosystem (DID)")
    description: str = Field(..., max_length=4096, description="A description of the Trust Registry")
    trustregistry_did: Optional[str] = Field(None, description="Unique identifier of the Trust Registry (DID)")
    egf_did: Optional[str] = Field(None, description="The Primary EGF, identified by DID")
    name: Optional[str] = Field(None, description="Human-readable name of the Trust Registry")
    controllers: Optional[List[str]] = Field(
        None,
        min_items=1,
        description="List of unique identifiers representing the controllers"
    )

    class Config:
        extra = "allow"


class Authorization(BaseModel):
    """
    Authorization action and resource pair
    """
    action: str = Field(..., description="The action")
    resource: str = Field(..., description="The resource")
    description: Optional[str] = Field(
        None,
        description="Non-normative information about the action+resource pair"
    )


class AssuranceLevelResponse(BaseModel):
    """
    Assurance level information
    """
    assurance_level: str = Field(..., description="The assurance level")
    description: str = Field(..., description="Details about the assurance level")
    egf_did: Optional[str] = Field(None, description="EGF DID this assurance level applies to")


class AssuranceLevelType(BaseModel):
    """
    Assurance level as a first-class citizen of a Trust Registry.
    AssuranceLevel values MUST be defined in an EGF if they are used.
    """
    identifier: str = Field(..., description="URI identifier for the assurance level")
    name: str = Field(..., description="Name of the assurance level (e.g., LOA2)")
    description: str = Field(
        ...,
        description="Description including EGF definition, terms, obligations, liabilities, and indemnity"
    )


class DIDMethodType(BaseModel):
    """
    DID Method supported by the trust registry.
    May include the maximum assurance level that this DID Method can support.
    """
    identifier: str = Field(
        ...,
        description="DID Method identifier as maintained at W3C did-spec-registries"
    )
    egf_did: Optional[str] = Field(None, description="EGF DID this DID Method applies to")
    maximumAssuranceLevel: Optional[AssuranceLevelType] = Field(
        None,
        description="Maximum assurance level this DID Method can provide"
    )


# Type aliases
DIDMethodListType = List[DIDMethodType]
