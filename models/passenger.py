from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database.connection import Base


class Passenger(Base):
    """A registered passenger/traveller."""

    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    gender = Column(String(20))
    date_of_birth = Column(Date)
    nationality = Column(String(80))
    passport_number = Column(String(30), unique=True, nullable=False, index=True)
    phone_number = Column(String(30))
    email = Column(String(150))

    bookings = relationship("Booking", back_populates="passenger", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Passenger {self.full_name}>"
