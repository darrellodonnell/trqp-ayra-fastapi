# Database Management

This document describes how to manage the Ayra TRQP database, including initialization, seeding, and backups.

## Database Files

- `trqp.db` - SQLite database file (created automatically)
- `seed_data.sql` - Sample data for bootstrapping a new database
- `database_export.sql` - Full database dump (all tables and data)
- `load_seed_data.py` - Python script to reset and seed the database

## Quick Start

### 1. Initialize Database with Sample Data

To create a fresh database with sample data:

```bash
python load_seed_data.py
```

This will:
- Drop all existing tables (asks for confirmation)
- Recreate the schema
- Load sample data from `seed_data.sql`
- Verify the data was loaded correctly

### 2. Reset Database (Keep Schema, Clear Data)

If you want to start fresh but keep the schema:

```bash
rm trqp.db
python init_db.py
```

This uses the default seed data from `app/database.py:seed_default_data()`.

### 3. Add Data Without Dropping Existing

To add sample data without dropping existing data:

```bash
python load_seed_data.py --keep-existing
```

**Note:** This may fail if there are duplicate DIDs or other unique constraint violations.

## Sample Data Structure

The seed data includes a hierarchical trust registry structure:

### Root Ecosystem
- **Ayra Trust Network** (`did:webvh:SCID-ATN:ayra.forum`)
  - Has root authorizations for the entire Ayra Card system

### Child Ecosystems
- **Bubba Group Ecosystem** (`did:web:bubbagroup.com`)
  - Can manage issuers for Ayra Business Cards

- **First Person Network** (`did:webvh:SCID-FPN:firstperson.network`)
  - Can issue and manage FPP Person Cards

### Organizations
- **Bubba Bank** (`did:web:bubbabank.com`)
  - Governed by Bubba Group Ecosystem
  - Can issue Ayra Business Cards

### Authorizations

| Action | Resource | Description |
|--------|----------|-------------|
| root | ayracard | Root authority for Ayra Card System |
| root | ayracard:businesscard | Root authority for Business Cards |
| manage-issuers | ayracard:businesscard | Can manage Business Card issuers |
| issue | ayracard:businesscard | Can issue Business Cards |
| issue | ayracard:fpp-person-card | Can issue FPP Person Cards |
| manage-issuer | ayracard:fpp-person-card | Can manage FPP Person Card issuers |

### DID Methods

- `web` - DID Web Method
- `key` - DID Key Method
- `peer` - DID Peer Method
- `webvh` - DID Web Verifiable History (high-assurance)

### Assurance Levels

- `LOA1` - Basic identity verification
- `LOA2` - Enhanced verification with documents
- `LOA3` - High assurance with in-person verification

## Backup and Export

### Export Current Database

To export your current database state:

```bash
sqlite3 trqp.db .dump > my_backup.sql
```

### Restore from Backup

To restore from a backup:

```bash
# Remove existing database
rm trqp.db

# Import backup
sqlite3 trqp.db < my_backup.sql
```

### Export Only Data (No Schema)

```bash
sqlite3 trqp.db .dump | grep "^INSERT" > data_only.sql
```

## Customizing Seed Data

To customize the seed data for your environment:

1. Edit `seed_data.sql`
2. Modify the INSERT statements to match your:
   - Entity hierarchy
   - Authorization types
   - DID methods
   - Assurance levels

3. Run the loader:
   ```bash
   python load_seed_data.py
   ```

## Database Schema

The database includes these main tables:

### Core Tables

- **entities** - Registered entities (ecosystems, organizations, people)
- **authorizations** - Action+Resource pairs that define permissions
- **entity_authorizations** - Many-to-many mapping between entities and authorizations

### Lookup Tables

- **did_methods** - Supported DID methods
- **assurance_levels** - Identity verification levels

### Configuration Tables

- **registry_config** - Registry configuration (authority_id, egf_id, etc.)
- **trust_registry_config** - Trust registry metadata

### Recognition (Future)

- **ecosystem_recognitions** - Cross-ecosystem recognition records

## Important Notes on Root Ecosystems

As of the recent updates, the system supports **root ecosystems** - ecosystems that don't have an authority:

- Root ecosystems have `authority_id = NULL`
- Non-ecosystem entities **must** have an `authority_id`
- Root ecosystems can serve as authorities for other ecosystems or organizations

### Example Hierarchy

```
Root Ecosystem (authority_id = NULL)
  ├─ Child Ecosystem (authority_id = Root Ecosystem DID)
  │   └─ Organization (authority_id = Child Ecosystem DID)
  └─ Organization (authority_id = Root Ecosystem DID)
```

## Troubleshooting

### Database is Locked

If you get "database is locked" errors:

1. Stop the FastAPI server
2. Wait a few seconds for connections to close
3. Try the operation again

### Foreign Key Errors

If you get foreign key constraint errors:

1. Check that parent entities exist before creating child entities
2. Ensure authority_id references an existing ecosystem entity
3. For root ecosystems, use `NULL` for authority_id

### Duplicate Key Errors

If you get unique constraint errors:

- Check that entity DIDs are unique
- Check that DID method identifiers are unique
- Check that assurance level identifiers are unique

## Migration from Old Schema

If you have an old database without the root ecosystem support:

1. Backup your current database:
   ```bash
   sqlite3 trqp.db .dump > backup_before_migration.sql
   ```

2. The schema change was applied automatically via SQLite ALTER TABLE
3. Existing ecosystems with authority_id will continue to work
4. You can now create root ecosystems by setting authority_id to NULL

## Using PostgreSQL

To switch from SQLite to PostgreSQL:

1. Set `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/trqp_db"
   ```

2. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

3. Run initialization:
   ```bash
   python init_db.py
   ```

**Note:** The `load_seed_data.py` script currently only supports SQLite. For PostgreSQL, use `psql` to import the SQL file:

```bash
psql -d trqp_db -f seed_data.sql
```

## Development Tips

### View Database in Terminal

```bash
sqlite3 trqp.db
sqlite> .tables
sqlite> .schema entities
sqlite> SELECT * FROM entities;
sqlite> .quit
```

### Quick Entity Lookup

```bash
sqlite3 trqp.db "SELECT entity_did, name, entity_type, authority_id FROM entities;"
```

### Check Authorization Mappings

```bash
sqlite3 trqp.db "
SELECT
  e.name as entity,
  a.action,
  a.resource
FROM entities e
JOIN entity_authorizations ea ON e.id = ea.entity_id
JOIN authorizations a ON ea.authorization_id = a.id
ORDER BY e.name;
"
```

### Find Root Ecosystems

```bash
sqlite3 trqp.db "SELECT name, entity_did FROM entities WHERE authority_id IS NULL AND entity_type = 'ecosystem';"
```

## Support

For issues related to database management:

1. Check the [README.md](README.md) for general setup
2. Review [GETTING_STARTED.md](GETTING_STARTED.md) for tutorials
3. See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for admin operations
4. Open an issue on GitHub for bugs or questions
