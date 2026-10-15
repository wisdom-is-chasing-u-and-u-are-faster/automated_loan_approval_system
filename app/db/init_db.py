import os
import sys

# Ensure project root is in sys.path for direct script execution
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import sqlite3
from app.db.session import get_db

def init_database(schema_path: str = "db/schema.sql", seed_path: str = "db/seed.sql"):
    """Initializes the database schema and seeds default records."""
    schema_full_path = os.path.join(base_dir, schema_path) if not os.path.isabs(schema_path) else schema_path
    seed_full_path = os.path.join(base_dir, seed_path) if not os.path.isabs(seed_path) else seed_path

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Execute schema
        if os.path.exists(schema_full_path):
            with open(schema_full_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            cursor.executescript(schema_sql)
        
        # Execute seeds
        if os.path.exists(seed_full_path):
            with open(seed_full_path, "r", encoding="utf-8") as f:
                seed_sql = f.read()
            cursor.executescript(seed_sql)

if __name__ == "__main__":
    init_database()
    print("Database schema and seeds initialized successfully.")
