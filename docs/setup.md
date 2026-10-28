> Historical Phase 1 workstation notes. For current portable clone/setup instructions, full cached ACS imports and AI configuration, use the [README](../README.md#local-setup). Keep the historical database-volume cautions below when working in the original checkout.

# Current local setup

The selected project is `/Users/gianvelasco/Desktop/HAIC26`. Its source was recovered from the prior DistrictIQ deliverable into this previously empty Git checkout; the existing `.git` directory was preserved.

Docker Desktop is installed and its engine is running. The existing Compose database configuration uses `postgis/postgis:17-3.5` with `platform: linux/amd64`; Docker Desktop runs that image through Apple Silicon emulation. PostgreSQL is published on loopback port 5432 and persists in `haic26_pgdata`.

The native `.env` uses localhost; container API/migration services use the Compose `db` hostname. Keep the current `.env` because its password matches the initialized database. Never run `docker compose down -v` or delete the volume to perform an ordinary restart.

Start the database and apply migrations:

```bash
cd /Users/gianvelasco/Desktop/HAIC26
docker compose up -d db
make migrate
```

The official files are already imported. To repeat the local import intentionally, `make seed` reads existing GIS/ACS files and upserts their stable identifiers. It does not download additional sources or require API keys. The four unmodified workbooks are in `data/raw/acs` and both existing GeoJSON captures are in `data/raw/geography`.

Start each application in its own terminal:

```bash
make dev-api
```

```bash
make dev-web
```

Open http://localhost:3000 and confirm http://localhost:8000/readyz returns 200. Python 3.12 and Node.js 24 were used. `make install PYTHON=python3.12` recreates dependencies if needed; it does not install Docker.

A Docker credential-helper/keychain error prevented the first anonymous public-image pull inside the sandbox. The public image was pulled using a temporary, project-local Docker config containing an explicit anonymous Docker Hub entry and the existing engine socket. The user's saved Docker credentials and global config were not altered. The image is now cached and ordinary `docker compose up -d db` succeeds. If a future fresh pull from a normal terminal asks for macOS Keychain access, approve Docker's normal trusted prompt or unlock the login keychain; do not replace the database volume.

No OpenAI, Census or ArcGIS key is required for the current imported data and map. Optional discovery and live refresh remain available. See `docs/local-data-methodology.md` and `docs/local-integration-report.md` for source handling and verification.
