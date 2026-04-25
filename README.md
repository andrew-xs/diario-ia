# Diario IA

Sistema multiagente para generación automática de noticias.

## Flujo

sources → ingestion → stories → reporter → editor → control → publisher → community

## Ejecutar

```bash
uvicorn app.main:app --reload