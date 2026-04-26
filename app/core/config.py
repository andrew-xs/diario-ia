import os
from dataclasses import dataclass


def parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def load_env():
    if not os.path.exists(".env"):
        return

    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, _, value = line.strip().partition("=")
                os.environ.setdefault(key, value)


load_env()


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./diario_ia.db")
    wordpress_enabled: bool = parse_bool(os.getenv("WORDPRESS_ENABLED"), False)
    social_enabled: bool = parse_bool(os.getenv("SOCIAL_ENABLED"), False)


settings = Settings()