PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE did_methods (
	id INTEGER NOT NULL, 
	identifier VARCHAR NOT NULL, 
	egf_did VARCHAR, 
	maximum_assurance_level VARCHAR, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO did_methods VALUES(1,'web',NULL,NULL,'DID Web Method','2025-11-06 09:33:11.208853','2025-11-06 09:33:11.208854');
INSERT INTO did_methods VALUES(2,'key',NULL,NULL,'DID Key Method','2025-11-06 09:33:11.208855','2025-11-06 09:33:11.208855');
INSERT INTO did_methods VALUES(3,'peer',NULL,NULL,'DID Peer Method','2025-11-06 09:33:11.208856','2025-11-06 09:33:11.208856');
INSERT INTO did_methods VALUES(5,'webvh','did:webvh:SCID123456SCID:ayra.forum',NULL,'DID Web Verifiable History - high-assurance ','2025-11-06 09:35:00.446983','2025-11-06 09:35:00.446987');
CREATE TABLE assurance_levels (
	id INTEGER NOT NULL, 
	identifier VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	egf_did VARCHAR, 
	description TEXT NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO assurance_levels VALUES(1,'urn:assurance:loa1','LOA1',NULL,'Level of Assurance 1 - Basic identity verification','2025-11-06 09:33:11.208036','2025-11-06 09:33:11.208040');
INSERT INTO assurance_levels VALUES(2,'urn:assurance:loa2','LOA2',NULL,'Level of Assurance 2 - Enhanced identity verification with document validation','2025-11-06 09:33:11.208041','2025-11-06 09:33:11.208042');
INSERT INTO assurance_levels VALUES(3,'urn:assurance:loa3','LOA3',NULL,'Level of Assurance 3 - High assurance with in-person verification','2025-11-06 09:33:11.208042','2025-11-06 09:33:11.208043');
CREATE TABLE authorizations (
	id INTEGER NOT NULL, 
	action VARCHAR NOT NULL, 
	resource VARCHAR NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO authorizations VALUES(5,'manage-issuers','ayracard:businesscard','The `manage-issuers` ACTION and `ayracard:businesscard` RESOURCE pair allows the assigned entity, typically an ecosystem, to manage issuance (add/remove the `issue` for `ayracard:businesscard` in their ecosystem) of the Ayra Business Card.','2025-11-06 09:41:36.863542','2025-11-06 09:41:36.863551');
INSERT INTO authorizations VALUES(6,'issue','ayracard:businesscard','Entities with this Action+Resource pair have the right to issue an Ayra Business Card.','2025-11-06 09:42:09.957267','2025-11-06 09:42:09.957278');
INSERT INTO authorizations VALUES(7,'issue','ayracard:fpp-person-card','Can issue an FPP Person Card','2025-11-06 12:09:02.928884','2025-11-06 12:09:02.928891');
INSERT INTO authorizations VALUES(8,'manage-issuer','ayracard:fpp-person-card','Can manage Issuers of FPP Person Card','2025-11-06 12:14:42.109073','2025-11-06 12:14:42.109082');
INSERT INTO authorizations VALUES(9,'root','ayracard','The root of the Ayra Card System','2025-11-06 16:01:37.154105','2025-11-06 16:01:37.154108');
INSERT INTO authorizations VALUES(10,'root','ayracard:businesscard',NULL,'2025-11-06 16:01:46.211376','2025-11-06 16:01:46.211382');
CREATE TABLE ecosystem_recognitions (
	id INTEGER NOT NULL, 
	recognizing_ecosystem_did VARCHAR NOT NULL, 
	recognized_registry_did VARCHAR NOT NULL, 
	action VARCHAR NOT NULL, 
	resource VARCHAR NOT NULL, 
	recognized BOOLEAN, 
	valid_from DATETIME, 
	valid_until DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE trust_registry_config (
	id INTEGER NOT NULL, 
	ecosystem_did VARCHAR NOT NULL, 
	trustregistry_did VARCHAR, 
	egf_did VARCHAR, 
	name VARCHAR, 
	description TEXT NOT NULL, 
	controllers TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (ecosystem_did)
);
INSERT INTO trust_registry_config VALUES(1,'did:example:ecosystem456','did:example:trustregistry123','did:example:egf789','Ayra Trust Registry','Example Trust Registry for the Ayra Trust Network','["did:example:controller1", "did:example:controller2"]','2025-11-06 09:33:11.209112','2025-11-06 09:33:11.209113');
CREATE TABLE entity_authorizations (
	entity_id INTEGER NOT NULL, 
	authorization_id INTEGER NOT NULL, 
	PRIMARY KEY (entity_id, authorization_id), 
	FOREIGN KEY(entity_id) REFERENCES entities (id), 
	FOREIGN KEY(authorization_id) REFERENCES authorizations (id)
);
INSERT INTO entity_authorizations VALUES(1,6);
INSERT INTO entity_authorizations VALUES(2,5);
INSERT INTO entity_authorizations VALUES(3,7);
INSERT INTO entity_authorizations VALUES(3,8);
INSERT INTO entity_authorizations VALUES(4,9);
INSERT INTO entity_authorizations VALUES(4,10);
CREATE TABLE registry_config (
	id INTEGER NOT NULL, 
	authority_id VARCHAR NOT NULL, 
	egf_id VARCHAR, 
	name VARCHAR, 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO registry_config VALUES(1,'did:webvh:SCID-FPN:firstperson.network',NULL,'Test Registry','Test Description',NULL,NULL);
CREATE TABLE IF NOT EXISTS "entities" (
    id INTEGER PRIMARY KEY,
    entity_did VARCHAR UNIQUE NOT NULL,
    authority_id VARCHAR,
    name VARCHAR,
    entity_type VARCHAR,
    status VARCHAR DEFAULT 'active',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO entities VALUES(1,'did:web:bubbabank.com','did:web:bubbagroup.com','Bubba Bank','organization','active',NULL,'2025-11-06 09:48:26.183483','2025-11-06 16:48:05.225806');
INSERT INTO entities VALUES(2,'did:web:bubbagroup.com',NULL,'Bubba Group Ecosystem','ecosystem','active',NULL,'2025-11-06 09:49:04.606840','2025-11-06 16:47:03.678529');
INSERT INTO entities VALUES(3,'did:webvh:SCID-FPN:firstperson.network',NULL,'First Person Network','ecosystem','active',NULL,'2025-11-06 12:09:46.963828','2025-11-06 13:34:51.016200');
INSERT INTO entities VALUES(4,'did:webvh:SCID-ATN:ayra.forum',NULL,'Ayra Trust Network','ecosystem','active','Ayra Trust Network','2025-11-06 13:32:34.502548','2025-11-06 16:00:59.233241');
CREATE UNIQUE INDEX ix_did_methods_identifier ON did_methods (identifier);
CREATE INDEX ix_did_methods_id ON did_methods (id);
CREATE INDEX ix_assurance_levels_id ON assurance_levels (id);
CREATE UNIQUE INDEX ix_assurance_levels_identifier ON assurance_levels (identifier);
CREATE INDEX ix_authorizations_resource ON authorizations (resource);
CREATE INDEX ix_authorizations_id ON authorizations (id);
CREATE INDEX ix_authorizations_action ON authorizations (action);
CREATE INDEX ix_ecosystem_recognitions_recognized_registry_did ON ecosystem_recognitions (recognized_registry_did);
CREATE INDEX ix_ecosystem_recognitions_recognizing_ecosystem_did ON ecosystem_recognitions (recognizing_ecosystem_did);
CREATE INDEX ix_ecosystem_recognitions_id ON ecosystem_recognitions (id);
CREATE INDEX ix_trust_registry_config_id ON trust_registry_config (id);
CREATE INDEX ix_registry_config_id ON registry_config (id);
CREATE UNIQUE INDEX ix_entities_entity_did ON entities (entity_did);
CREATE INDEX ix_entities_id ON entities (id);
CREATE INDEX ix_entities_authority_id ON entities (authority_id);
COMMIT;
