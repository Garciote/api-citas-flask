#!/usr/bin/env python3
"""
Script de migración inicial para la base de datos Clinica.
Crea colecciones, índices únicos y datos de ejemplo (centros).
Totalmente compatible con MongoDB Atlas y variables de entorno.
"""

import os
from dotenv import load_dotenv
import pymongo

load_dotenv()

# Obligatorio: usar MONGODB_URI desde entorno
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError(
        "Error: Environment variable 'MONGODB_URI' is not set.\n"
        "   - Create a '.env' file with 'MONGODB_URI=...'\n"
        "   - Or configure it in Github Secrets / Server"
    )

DB_NAME = os.getenv("MONGODB_DB", "Clinica")

def ensure_collections(db, names):
    existing = set(db.list_collection_names())
    for name in names:
        if name not in existing:
            db.create_collection(name)
            print(f"  Colección creada: {name}")

def ensure_indexes(db):
    print("  Creando índices únicos...")
    db["usuarios"].create_index("username", unique=True)
    db["citas"].create_index(
        [("day", pymongo.ASCENDING), ("hour", pymongo.ASCENDING), ("center", pymongo.ASCENDING)],
        unique=True,
        name="unique_date_per_center"
    )

def seed_centers(db):
    if db["centros"].count_documents({}) == 0:
        print("  Insertando centros por defecto...")
        db["centros"].insert_many([
            {
                "name": "Centro de Salud Madrid Norte",
                "address": "Calle de la Salud, 123, Madrid"
            },
            {
                "name": "Centro Médico Madrid Sur",
                "address": "Avenida de la Medicina, 456, Madrid"
            }
        ])
    else:
        print("  Los centros ya existen, saltando seed")

def main():
    print(f"Conectando a MongoDB...")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Test conexión
    client.admin.command('ping')
    print(f"Conexión exitosa a la base de datos: {DB_NAME}")

    ensure_collections(db, ["usuarios", "centros", "citas"])
    ensure_indexes(db)
    seed_centers(db)

    print(f"\n¡Migración completada con éxito!")
    print(f"   Base de datos: {DB_NAME}")
    print(f"   URI: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI}")

if __name__ == "__main__":
    main()