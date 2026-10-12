"""
Database initializer that applies schema.sql and seed.sql on startup.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path for direct execution
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.db.database import execute_script, execute_query


def init_database():
    """Initializes tables and default seed data if not present."""
    schema_path = project_root / "db" / "schema.sql"
    seed_path = project_root / "db" / "seed.sql"

    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            execute_script(schema_sql)

    # Check if users already seeded
    try:
        users = execute_query("SELECT COUNT(*) as count FROM users")
        if not users or users[0]["count"] == 0:
            if seed_path.exists():
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed_sql = f.read()
                    execute_script(seed_sql)
    except Exception as e:
        print(f"Database init warning: {e}")


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
