from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.source import Source

DEFAULT_SOURCES = [
    {
        "name": "latercera",
        "base_url": "https://www.latercera.com/",
        "category_hint": "nacional",
        "active": True,
    },
    {
        "name": "ciperchile",
        "base_url": "https://www.ciperchile.cl/",
        "category_hint": "actualidad",
        "active": True,
    },
    {
        "name": "emol",
        "base_url": "https://www.emol.com/",
        "category_hint": "nacional",
        "active": True,
    },
    {
        "name": "biobiochile",
        "base_url": "https://www.biobiochile.cl/",
        "category_hint": "nacional",
        "active": True,
    },
    {
        "name": "elmercurio_digital",
        "base_url": "https://digital.elmercurio.com/",
        "category_hint": "actualidad",
        "active": True,
    },
    {
        "name": "lun",
        "base_url": "https://www.lun.com/pages/LUNHomepage.aspx?BodyID=0&dt=",
        "category_hint": "actualidad",
        "active": True,
    },
    {
        "name": "24horas",
        "base_url": "https://www.24horas.cl/",
        "category_hint": "nacional",
        "active": True,
    },
]


def seed_sources(db: Session) -> dict:
    created = 0
    for item in DEFAULT_SOURCES:
        exists = db.query(Source).filter(Source.name == item["name"]).first()
        if exists:
            continue
        db.add(Source(**item))
        created += 1
    db.commit()
    return {"status": "ok", "sources_created": created, "sources_total": len(DEFAULT_SOURCES)}


def run_seed():
    db = SessionLocal()
    try:
        seed_sources(db)
        print("Seed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
