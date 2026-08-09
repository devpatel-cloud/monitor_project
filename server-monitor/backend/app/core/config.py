import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    BaseSettings = object

class Settings(BaseSettings if BaseSettings is not object else object):
    PROJECT_NAME: str = "Linux Server Monitor Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite Database path default
    DB_PATH: str = os.getenv("DB_PATH", "/var/lib/server-monitor/monitor.db")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Use local sqlite file if /var/lib/server-monitor is not writable
        db_dir = os.path.dirname(self.DB_PATH)
        if not os.path.exists(db_dir) and db_dir:
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception:
                return "sqlite:///./monitor.db"
        return f"sqlite:///{self.DB_PATH}"

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "server-monitor-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours

    # DuckDNS Configuration
    DUCKDNS_DOMAIN: str = os.getenv("DUCKDNS_DOMAIN", "sanjaya-server.duckdns.org")
    DUCKDNS_TOKEN: str = os.getenv("DUCKDNS_TOKEN", "") # Kept secret, never returned in API responses

    # Metric Retention Settings
    RETENTION_10S_HOURS: int = 24
    RETENTION_1M_DAYS: int = 7
    RETENTION_5M_DAYS: int = 30
    RETENTION_1H_DAYS: int = 365

settings = Settings()
