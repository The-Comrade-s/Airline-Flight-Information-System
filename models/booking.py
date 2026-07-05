from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

BOOKING_STATUSES = ["Confirmed", "Checked-in", "Boarded", "Cancelled", "Completed"]


class Booking(Base):
    """A passenger's reservation on a specific flight."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_reference = Column(String(20), unique=True, nullable=False, index=True)

    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)

    passenger = relationship("Passenger", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")

    seat_number = Column(String(6), nullable=False)
    fare_paid = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="Confirmed")
    booked_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Booking {self.booking_reference}>"
