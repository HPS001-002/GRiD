import os

def env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if v not in (None, "") else default

MYSQL_HOST = env("MYSQL_HOST", "mysql")
MYSQL_PORT = int(env("MYSQL_PORT", "3306") or "3306")
MYSQL_DATABASE = env("MYSQL_DATABASE", "grid")
MYSQL_USER = env("MYSQL_USER", "grid")
MYSQL_PASSWORD = env("MYSQL_PASSWORD", "gridpassword")

# Secret for JWT. CHANGE IN PROD.
JWT_SECRET = env("JWT_SECRET", "CHANGE_ME") or "CHANGE_ME"
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = int(env("JWT_EXPIRES_MIN", "1440") or "1440")  # 1 day

# Where to store branding/logo inside container
DATA_DIR = env("DATA_DIR", "/data") or "/data"
BRANDING_DIR = os.path.join(DATA_DIR, "branding")
LOGO_PATH = os.path.join(BRANDING_DIR, "logo.png")

# Auth toggle (for quick homelab testing). Set GRID_DISABLE_AUTH=true to disable.
DISABLE_AUTH = (env("GRID_DISABLE_AUTH", "false") or "false").lower() in ("1", "true", "yes")
