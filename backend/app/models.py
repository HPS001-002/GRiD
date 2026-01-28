from sqlalchemy import String, DateTime, Boolean, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())

    access: Mapped[list["UserServerAccess"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Server(Base):
    __tablename__ = "servers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    server_type: Mapped[str] = mapped_column(String(128))
    os: Mapped[str] = mapped_column(String(64))
    hostname: Mapped[str] = mapped_column(String(255))
    tailscale_ip: Mapped[str] = mapped_column(String(64), default="")
    local_ip: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())

    access: Mapped[list["UserServerAccess"]] = relationship(back_populates="server", cascade="all, delete-orphan")

class UserServerAccess(Base):
    __tablename__ = "user_server_access"
    __table_args__ = (UniqueConstraint("user_id", "server_id", name="uq_user_server"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    server_id: Mapped[str] = mapped_column(String(64), ForeignKey("servers.id", ondelete="CASCADE"), index=True)

    user: Mapped["User"] = relationship(back_populates="access")
    server: Mapped["Server"] = relationship(back_populates="access")
