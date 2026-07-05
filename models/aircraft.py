from sqlalchemy import Column, Integer, String
from database.connection import Base


class Aircraft(Base):
    """Aircraft type reference table."""

    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(100), nullable=False)          # e.g. Boeing 777-300ER
    manufacturer = Column(String(80), nullable=False)    # e.g. Boeing
    total_seats = Column(Integer, nullable=False, default=180)
    seat_layout = Column(String(20), default="3-3")      # economy row layout, informational

    def __repr__(self):
        return f"<Aircraft {self.model}>"
