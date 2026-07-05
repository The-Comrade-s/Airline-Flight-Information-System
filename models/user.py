from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    """System user account (Administrator or Staff)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(120), nullable=False)
    username = Column(String(60), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="Staff")  # Administrator | Staff
    is_active = Column(Integer, default=1)  # 1 = active, 0 = disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
