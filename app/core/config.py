from dataclasses import dataclass
from pathlib import Path
import os


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_dotenv(env_path: str = ".env") -> None:
    file_path = Path(env_path)
    if not file_path.exists():
        return

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./diario_ia.db")
    wordpress_enabled: bool = _parse_bool(os.getenv("WORDPRESS_ENABLED"), default=False)
    social_enabled: bool = _parse_bool(os.getenv("SOCIAL_ENABLED"), default=True)


settings = Settings()
