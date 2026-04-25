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


def run_seed():
    db = SessionLocal()
    try:
        for item in DEFAULT_SOURCES:
            exists = db.query(Source).filter(Source.name == item["name"]).first()
            if not exists:
                db.add(Source(**item))
        db.commit()
        print("Seed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()