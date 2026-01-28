# GRiD
<<<<<<< HEAD
A Web based server manager, that will allow you to add/remove servers for management purposes. 
=======

GRiD is a self-hosted, web-based server dashboard/manager designed to be easy to deploy on homelabs (TrueNAS SCALE, Docker Compose, etc.).

## What’s included
- **Frontend**: a single-page dashboard (this repo’s `frontend/index.html`) served by Nginx.
- **Backend**: FastAPI + MySQL (CRUD API + optional admin auth).
- **MySQL**: stores server records.

## Quick start (Docker Compose)
```bash
docker compose up -d --build
```

Open:
- UI: `http://localhost:7420`

## First-time admin setup
If auth is enabled (default), initialize the first admin account:
- `POST http://<host>/api/setup` with JSON body:
```json
{"username":"admin","password":"change-me"}
```
Response includes a JWT token.

Login:
- `POST /api/auth/login` with JSON:
```json
{"username":"admin","password":"change-me"}
```

> For quick homelab testing, you can disable auth by setting `GRID_DISABLE_AUTH=true` on the backend.

## TrueNAS SCALE (Install via YAML) – Ombi-style (single port)
In TrueNAS: **Apps → Custom App → Install via YAML**, paste (adjust dataset paths):

```yaml
version: "3.9"
services:
  mysql:
    image: mysql:8.0
    container_name: grid-mysql
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: grid
      MYSQL_USER: grid
      MYSQL_PASSWORD: gridpassword
      MYSQL_ROOT_PASSWORD: rootpassword_change_me
    volumes:
      - /mnt/Main/Apps/grid/mysql:/var/lib/mysql

  backend:
    image: ghcr.io/hps001-002/grid-backend:latest
    container_name: grid-backend
    restart: unless-stopped
    depends_on:
      - mysql
    environment:
      MYSQL_HOST: mysql
      MYSQL_PORT: "3306"
      MYSQL_DATABASE: grid
      MYSQL_USER: grid
      MYSQL_PASSWORD: gridpassword
      JWT_SECRET: change_me_in_prod
      DATA_DIR: /data
    volumes:
      - /mnt/Main/Apps/grid/backend:/data

  grid:
    image: ghcr.io/hps001-002/grid-frontend:latest
    container_name: grid
    restart: unless-stopped
    depends_on:
      - backend
    ports:
      - "7420:80"
```

## Publishing images to GHCR
This repo includes workflows:
- `publish-backend.yml` → `ghcr.io/<owner>/grid-backend:latest`
- `publish-frontend.yml` → `ghcr.io/<owner>/grid-frontend:latest`

Make sure repo Settings → Actions → **Workflow permissions** is set to **Read and write**.
>>>>>>> cce519c (Initial GRiD (MySQL))
