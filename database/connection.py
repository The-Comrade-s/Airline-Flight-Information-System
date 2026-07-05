"""
Database connection and session management for SkyWings.

Uses SQLite for local/demo deployment, but every column type and
constraint here is written in a MySQL-compatible way, so migrating
later only requires changing DATABASE_URL and re-running init_db().
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "skywings.db")

# To migrate to MySQL later, replace this with something like:
# DATABASE_URL = "mysql+pymysql://user:password@host:3306/skywings"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

Base = declarative_base()


def get_session():
    """Return a new SQLAlchemy session. Caller is responsible for closing it."""
    return SessionLocal()
