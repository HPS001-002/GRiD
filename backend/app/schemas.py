from pydantic import BaseModel, Field

class ServerBase(BaseModel):
    server_type: str = Field(..., max_length=128)
    os: str = Field(..., max_length=64)
    hostname: str = Field(..., max_length=255)
    tailscale_ip: str = Field("", max_length=64)
    local_ip: str = Field("", max_length=64)

class ServerCreate(ServerBase):
    id: str = Field(..., max_length=64)

class ServerUpdate(ServerBase):
    pass

class ServerOut(ServerCreate):
    created_at: str | None = None

class LoginIn(BaseModel):
    username: str
    password: str

class SetupIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    is_admin: bool
    created_at: str | None = None
