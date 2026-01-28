from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os, uuid

from .db import engine, get_db, Base
from . import models, schemas
from .auth import hash_password, verify_password, create_token, get_current_user, require_admin
from .config import BRANDING_DIR, LOGO_PATH

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GRiD API")

# If you use nginx in the frontend container to proxy /api, you won't need CORS.
# But leaving permissive CORS helps for local testing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ensure_branding_dir():
    os.makedirs(BRANDING_DIR, exist_ok=True)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/setup/status")
def setup_status(db: Session = Depends(get_db)):
    exists = db.query(models.User).first() is not None
    return {"initialized": exists}

@app.post("/api/setup", tags=["auth"])
def setup(payload: schemas.SetupIn, db: Session = Depends(get_db)):
    # Only allowed if no users exist
    if db.query(models.User).first() is not None:
        raise HTTPException(status_code=409, detail="Already initialized")
    user = models.User(
        id=str(uuid.uuid4()),
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    return {"ok": True, "token": create_token(user)}

@app.post("/api/auth/login", tags=["auth"])
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": create_token(user), "is_admin": bool(user.is_admin), "username": user.username}

@app.get("/api/servers", response_model=list[schemas.ServerOut], tags=["servers"])
def list_servers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # If not admin, filter to allowed servers
    q = db.query(models.Server)
    if not user.is_admin:
        q = q.join(models.UserServerAccess).filter(models.UserServerAccess.user_id == user.id)
    rows = q.order_by(models.Server.created_at.desc()).all()
    return [schemas.ServerOut(
        id=r.id,
        server_type=r.server_type,
        os=r.os,
        hostname=r.hostname,
        tailscale_ip=r.tailscale_ip,
        local_ip=r.local_ip,
        created_at=str(r.created_at) if r.created_at else None
    ) for r in rows]

@app.post("/api/servers", tags=["servers"])
def create_server(payload: schemas.ServerCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    if db.query(models.Server).filter(models.Server.id == payload.id).first():
        raise HTTPException(status_code=409, detail="Server id already exists")
    s = models.Server(
        id=payload.id,
        server_type=payload.server_type,
        os=payload.os,
        hostname=payload.hostname,
        tailscale_ip=payload.tailscale_ip,
        local_ip=payload.local_ip,
    )
    db.add(s)
    db.commit()
    return {"ok": True}

@app.put("/api/servers/{server_id}", tags=["servers"])
def update_server(server_id: str, payload: schemas.ServerUpdate, db: Session = Depends(get_db), user=Depends(require_admin)):
    s = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    s.server_type = payload.server_type
    s.os = payload.os
    s.hostname = payload.hostname
    s.tailscale_ip = payload.tailscale_ip
    s.local_ip = payload.local_ip
    db.commit()
    return {"ok": True}

@app.delete("/api/servers/{server_id}", tags=["servers"])
def delete_server(server_id: str, db: Session = Depends(get_db), user=Depends(require_admin)):
    s = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(s)
    db.commit()
    return {"ok": True}

@app.get("/api/branding/logo", tags=["branding"])
def get_logo():
    # Return logo if present; otherwise 404
    if os.path.exists(LOGO_PATH):
        return FileResponse(LOGO_PATH)
    raise HTTPException(status_code=404, detail="No logo uploaded")

@app.post("/api/branding/logo", tags=["branding"])
async def upload_logo(file: UploadFile = File(...), user=Depends(require_admin)):
    ensure_branding_dir()
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    with open(LOGO_PATH, "wb") as f:
        f.write(content)
    return {"ok": True}
