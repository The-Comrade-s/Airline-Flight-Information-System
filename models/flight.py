from sqlalchemy import (
    Column, Integer, String, Float, Date, Time, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from database.connection import Base

FLIGHT_STATUSES = ["Scheduled", "Boarding", "Delayed", "Cancelled", "Landed"]


class Flight(Base):
    """A scheduled flight between two airports."""

    __tablename__ = "flights"
    __table_args__ = (
        CheckConstraint("ticket_price >= 0", name="ck_flight_price_nonneg"),
        CheckConstraint("available_seats >= 0", name="ck_flight_seats_nonneg"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_number = Column(String(10), unique=True, nullable=False, index=True)
    airline = Column(String(80), nullable=False)

    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    aircraft = relationship("Aircraft")

    departure_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    destination_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    departure_airport = relationship("Airport", foreign_keys=[departure_airport_id])
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_id])

    departure_date = Column(Date, nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)

    gate = Column(String(10))
    terminal = Column(String(10))

    ticket_price = Column(Float, nullable=False, default=0.0)
    total_seats = Column(Integer, nullable=False, default=180)
    available_seats = Column(Integer, nullable=False, default=180)

    status = Column(String(20), nullable=False, default="Scheduled")

    bookings = relationship("Booking", back_populates="flight", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Flight {self.flight_number}>"
