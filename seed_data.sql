-- Ayra Trust Registry - Sample Data Export
-- This file contains sample data for bootstrapping a new Ayra TRQP database
-- Generated: 2025-11-06

-- DID Methods
INSERT INTO did_methods (identifier, egf_did, maximum_assurance_level, description, created_at, updated_at) VALUES
('web', NULL, NULL, 'DID Web Method', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('key', NULL, NULL, 'DID Key Method', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('peer', NULL, NULL, 'DID Peer Method', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('webvh', 'did:webvh:SCID123456SCID:ayra.forum', NULL, 'DID Web Verifiable History - high-assurance', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Assurance Levels
INSERT INTO assurance_levels (identifier, name, egf_did, description, created_at, updated_at) VALUES
('urn:assurance:loa1', 'LOA1', NULL, 'Level of Assurance 1 - Basic identity verification', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('urn:assurance:loa2', 'LOA2', NULL, 'Level of Assurance 2 - Enhanced identity verification with document validation', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('urn:assurance:loa3', 'LOA3', NULL, 'Level of Assurance 3 - High assurance with in-person verification', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Authorizations (Action + Resource pairs)
INSERT INTO authorizations (action, resource, description, created_at, updated_at) VALUES
('root', 'ayracard', 'The root of the Ayra Card System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('root', 'ayracard:businesscard', 'Root authority for Ayra Business Card', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('manage-issuers', 'ayracard:businesscard', 'The manage-issuers ACTION and ayracard:businesscard RESOURCE pair allows the assigned entity, typically an ecosystem, to manage issuance (add/remove the issue for ayracard:businesscard in their ecosystem) of the Ayra Business Card.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('issue', 'ayracard:businesscard', 'Entities with this Action+Resource pair have the right to issue an Ayra Business Card.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('issue', 'ayracard:fpp-person-card', 'Can issue an FPP Person Card', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('manage-issuer', 'ayracard:fpp-person-card', 'Can manage Issuers of FPP Person Card', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Entities (hierarchical structure)
-- Note: Root ecosystems have NULL authority_id
INSERT INTO entities (entity_did, authority_id, name, entity_type, status, description, created_at, updated_at) VALUES ('did:webvh:SCID-ATN:ayra.forum', NULL, 'Ayra Trust Network', 'ecosystem', 'active', 'Ayra Trust Network', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
INSERT INTO entities (entity_did, authority_id, name, entity_type, status, description, created_at, updated_at) VALUES ('did:web:bubbagroup.com', NULL, 'Bubba Group Ecosystem', 'ecosystem', 'active', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
INSERT INTO entities (entity_did, authority_id, name, entity_type, status, description, created_at, updated_at) VALUES ('did:webvh:SCID-FPN:firstperson.network', NULL, 'First Person Network', 'ecosystem', 'active', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
INSERT INTO entities (entity_did, authority_id, name, entity_type, status, description, created_at, updated_at) VALUES ('did:web:bubbabank.com', 'did:web:bubbagroup.com', 'Bubba Bank', 'organization', 'active', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Entity-Authorization mappings
INSERT INTO entity_authorizations (entity_id, authorization_id) VALUES (1, 1);
INSERT INTO entity_authorizations (entity_id, authorization_id) VALUES (1, 2);
INSERT INTO entity_authorizations (entity_id, authorization_id) VALUES (2, 3);
INSERT INTO entity_authorizations (entity_id, authorization_id) VALUES (3, 5);
INSERT INTO entity_authorizations (entity_id, authorization_id) VALUES (3, 6);
INSERT INTO entity_authorizations (entity_id, authorization_id) VALUES (4, 4);

-- Trust Registry Config
INSERT INTO trust_registry_config (ecosystem_did, trustregistry_did, egf_did, name, description, controllers, created_at, updated_at) VALUES
('did:webvh:SCID-ATN:ayra.forum/atn', 'did:webvh:SCID-ATNTR:ayra.forum/atntr', 'did:webvh:SCID-ATNGF:ayra.forum/atngf', 'Ayra Trust Registry', 'Example Trust Registry for the Ayra Trust Network', '["did:example:controller1", "did:example:controller2"]', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Registry Config (for admin UI)
INSERT INTO registry_config (authority_id, egf_id, name, description, created_at, updated_at) VALUES
('did:webvh:SCID-FPN:firstperson.network', NULL, 'Test Registry', 'Test Description', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
