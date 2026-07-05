from sqlalchemy import Column, Integer, String
from database.connection import Base


class Airport(Base):
    """Airport reference table (IATA codes)."""

    __tablename__ = "airports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(3), unique=True, nullable=False, index=True)  # e.g. JFK
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Airport {self.code}>"

    @property
    def label(self):
        return f"{self.city} ({self.code})"
