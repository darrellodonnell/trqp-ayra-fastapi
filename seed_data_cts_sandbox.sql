-- Ayra CTS Sandbox Trust Registry seed data
-- Restores the minimal entity and policy state expected by the CTS sandbox flows.

-- DID Methods
INSERT INTO did_methods (identifier, egf_did, maximum_assurance_level, description, created_at, updated_at) VALUES
('web', NULL, NULL, 'DID Web Method', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('key', NULL, NULL, 'DID Key Method', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('peer', NULL, NULL, 'DID Peer Method', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('webvh', 'did:webvh:ayra.forum', NULL, 'DID Web Verifiable History - high-assurance', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Assurance Levels
INSERT INTO assurance_levels (identifier, name, egf_did, description, created_at, updated_at) VALUES
('urn:assurance:loa1', 'LOA1', NULL, 'Level of Assurance 1 - Basic identity verification', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('urn:assurance:loa2', 'LOA2', NULL, 'Level of Assurance 2 - Enhanced identity verification with document validation', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('urn:assurance:loa3', 'LOA3', NULL, 'Level of Assurance 3 - High assurance with in-person verification', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Authorization types used by CTS
INSERT INTO authorizations (action, resource, description, created_at, updated_at) VALUES
('root', 'ayracard', 'Root authority for Ayra Card ecosystem', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('manage-issuers', 'ayracard:businesscard', 'Authority to manage business card issuers in an ecosystem', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('issue', 'ayracard:businesscard', 'Authority to issue Ayra business cards', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Recognition types used by CTS
INSERT INTO recognitions (action, resource, description, created_at, updated_at) VALUES
('recognize', 'ecosystem', 'Recognition of other ecosystems and their governance', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('member-of', 'ayratrustnetwork', 'Recognition that an ecosystem is a member of the Ayra Trust Network', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Entities
INSERT INTO entities (entity_did, authority_id, name, entity_type, status, description, created_at, updated_at) VALUES
('did:webvh:ayra.forum', NULL, 'Ayra Trust Network', 'ecosystem', 'active', 'Ayra Trust Network root ecosystem', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('did:web:sandbox.ayra.network', NULL, 'Ayra Sandbox Ecosystem', 'ecosystem', 'active', 'Sandbox ecosystem used by CTS', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('did:web:ayra-cts-issuer.ngrok.app:issuer', 'did:web:sandbox.ayra.network', 'CTS Issuer', 'organization', 'active', 'Reference CTS issuer', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Entity authorization bindings
INSERT INTO entity_authorizations (entity_id, authorization_id)
SELECT e.id, a.id
FROM entities e
JOIN authorizations a ON a.action = 'root' AND a.resource = 'ayracard'
WHERE e.entity_did = 'did:webvh:ayra.forum';

INSERT INTO entity_authorizations (entity_id, authorization_id)
SELECT e.id, a.id
FROM entities e
JOIN authorizations a ON a.action = 'manage-issuers' AND a.resource = 'ayracard:businesscard'
WHERE e.entity_did = 'did:web:sandbox.ayra.network';

INSERT INTO entity_authorizations (entity_id, authorization_id)
SELECT e.id, a.id
FROM entities e
JOIN authorizations a ON a.action = 'issue' AND a.resource = 'ayracard:businesscard'
WHERE e.entity_did = 'did:web:ayra-cts-issuer.ngrok.app:issuer';

-- ATN recognizes the sandbox ecosystem as a member of the Ayra Trust Network
INSERT INTO entity_recognitions (
    entity_id,
    recognition_id,
    recognized_registry_did,
    recognized,
    valid_from,
    valid_until,
    created_at,
    updated_at
)
SELECT
    e.id,
    r.id,
    'did:web:sandbox.ayra.network',
    1,
    NULL,
    NULL,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM entities e
JOIN recognitions r ON r.action = 'member-of' AND r.resource = 'ayratrustnetwork'
WHERE e.entity_did = 'did:webvh:ayra.forum';

-- Trust Registry metadata/config
INSERT INTO trust_registry_config (
    ecosystem_did,
    trustregistry_did,
    egf_did,
    name,
    description,
    controllers,
    created_at,
    updated_at
) VALUES (
    'did:web:sandbox.ayra.network',
    'did:web:sandbox.ayra.network#TRQP',
    'did:webvh:ayra.forum',
    'Ayra Sandbox Trust Registry',
    'CTS sandbox trust registry configuration',
    '["did:webvh:ayra.forum"]',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

INSERT INTO registry_config (
    authority_id,
    egf_id,
    name,
    description,
    created_at,
    updated_at
) VALUES (
    'did:webvh:ayra.forum',
    'did:webvh:ayra.forum',
    'Ayra Sandbox Trust Registry',
    'CTS sandbox registry configuration',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Helpful endpoint row for admin UI/testing
INSERT INTO trqp_endpoints (name, base_url, description, is_active, created_at, updated_at) VALUES
('CTS Sandbox TR', 'https://sandbox-tr.ayra.network', 'Sandbox TR endpoint used by CTS', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
