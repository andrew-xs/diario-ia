import logging

from app.core.config import settings

_CONFIGURED = False


def _resolve_level() -> int:
    env = settings.app_env.lower()

    if env == "development":
        return logging.DEBUG
    if env == "production":
        return logging.WARNING

    return logging.INFO


def configure_logging() -> None:
    global _CONFIGURED

    if _CONFIGURED:
        return

    logging.basicConfig(
        level=_resolve_level(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)