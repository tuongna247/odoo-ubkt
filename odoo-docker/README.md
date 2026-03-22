# UBKT Odoo 15 - Docker Setup

Runs Odoo 15 in Docker connecting to an existing PostgreSQL 13 on the Windows host.

## Architecture

```
[Docker: odoo:15]  →  host.docker.internal:5432  →  [PostgreSQL 13 on Windows]
                                                          └── db_ubkt_prod_00  (password: B@0Ng0c)
```

## Prerequisites

- Docker Desktop installed and running
- PostgreSQL 13 running at `D:\Program Files\PostgreSQL\13`
- Database `db_ubkt_prod_00` restored

---

## First-Time Setup

### 1. Create the odoo15 database role

Open pgAdmin or psql as the `postgres` superuser and run:

```sql
CREATE ROLE odoo15 WITH LOGIN PASSWORD 'odoo15' CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE db_ubkt_prod_00 TO odoo15;
```

### 2. Allow Docker network in pg_hba.conf

Add the following line to `D:\Program Files\PostgreSQL\13\data\pg_hba.conf`
(already done — verify it exists):

```
host    all             all             172.16.0.0/12           scram-sha-256
```

Then reload PostgreSQL config (run as postgres user):

```sql
SELECT pg_reload_conf();
```

### 3. Start Odoo

```bash
cd D:/Projects/UBKT/odoo-docker
docker compose up -d
```

### 4. Update all installed modules (first run only)

Wait ~30 seconds for Odoo to start, then run:

```bash
docker exec ubkt_odoo15 odoo -d db_ubkt_prod_00 -u all --stop-after-init
```

Then restart:

```bash
docker compose restart odoo
```

### 5. Open in browser

```
http://localhost:8069
```

---

## Daily Usage

| Task | Command |
|---|---|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| View logs | `docker compose logs -f odoo` |
| Restart | `docker compose restart odoo` |

---

## File Structure

```
D:\Projects\UBKT\odoo-docker\
├── docker-compose.yml      — Docker service definition
├── odoo.conf               — Odoo server configuration
├── README.md               — This file
└── data\                   — Odoo filestore (attachments, sessions)

D:\Projects\UBKT\addons_ubkt_prod\opt\odoo\ubkt_addons\
└── (custom modules — mounted read-only into container)
```

---

## Configuration

**odoo.conf key settings:**

| Setting | Value |
|---|---|
| Database host | `host.docker.internal` |
| Database port | `5432` |
| Database name | `db_ubkt_prod_00` |
| Database password | `B@0Ng0c` |
| Filestore | `D:\Projects\UBKT\odoo-docker\data\filestore\` |
| Database user | `odoo15` |
| Addons path | `/mnt/extra-addons` (ubkt_addons) |
| Data directory | `/var/lib/odoo` → `D:\Projects\UBKT\odoo-docker\data\` |

---

## Troubleshooting

**Cannot connect to PostgreSQL:**
- Verify PostgreSQL 13 service is running in Windows Services
- Check `pg_hba.conf` has the `172.16.0.0/12` rule and was reloaded
- Confirm `odoo15` role exists: `SELECT rolname FROM pg_roles WHERE rolname = 'odoo15';`

**Modules not showing / errors on startup:**
```bash
docker compose logs odoo
```

**Force update a specific module (e.g. account_custom):**
```bash
docker exec ubkt_odoo15 odoo -d db_ubkt_prod_00 -u account_custom --stop-after-init
docker compose restart odoo
```

**Reset Odoo container (keeps database and filestore intact):**
```bash
docker compose down
docker compose up -d
```
