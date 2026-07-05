"""
Creates all tables. Run this once before seed_data.py, or simply
run app.py, which calls this automatically on first launch.
"""

from database.connection import engine, Base
import models  # noqa: F401  (import registers all model classes with Base)


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
