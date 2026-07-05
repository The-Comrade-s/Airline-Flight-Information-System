"""
Data access layer: reusable query and mutation functions used by pages.
Keeping this logic here (rather than inline in pages/) keeps the UI
files focused on presentation.
"""

from datetime import date
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from database.connection import get_session
from models import Flight, Passenger, Booking, Airport, Aircraft, User

# Flights are always displayed with their airport/aircraft relationships,
# so every flight query eager-loads them to avoid DetachedInstanceError
# once the session that fetched them has been closed.
_FLIGHT_EAGER = (
    joinedload(Flight.departure_airport),
    joinedload(Flight.destination_airport),
    joinedload(Flight.aircraft),
)

# Bookings are always displayed with their passenger and flight (and the
# flight's own airports/aircraft), so eager-load the full chain.
_BOOKING_EAGER = (
    joinedload(Booking.passenger),
    joinedload(Booking.flight).joinedload(Flight.departure_airport),
    joinedload(Booking.flight).joinedload(Flight.destination_airport),
    joinedload(Booking.flight).joinedload(Flight.aircraft),
)


# ---------- Airports & Aircraft ----------

def get_all_airports():
    session = get_session()
    try:
        return session.query(Airport).order_by(Airport.city).all()
    finally:
        session.close()


def get_all_aircraft():
    session = get_session()
    try:
        return session.query(Aircraft).order_by(Aircraft.model).all()
    finally:
        session.close()


# ---------- Flights ----------

def get_all_flights(session=None):
    own_session = session is None
    session = session or get_session()
    try:
        return session.query(Flight).options(*_FLIGHT_EAGER).order_by(
            Flight.departure_date, Flight.departure_time
        ).all()
    finally:
        if own_session:
            session.close()


def search_flights(flight_number=None, airline=None, departure_city=None,
                    destination_city=None, dep_date=None, status=None):
    session = get_session()
    try:
        query = session.query(Flight).options(*_FLIGHT_EAGER)
        if flight_number:
            query = query.filter(Flight.flight_number.ilike(f"%{flight_number}%"))
        if airline:
            query = query.filter(Flight.airline.ilike(f"%{airline}%"))
        if departure_city:
            query = query.join(Airport, Flight.departure_airport_id == Airport.id).filter(
                or_(Airport.city.ilike(f"%{departure_city}%"), Airport.code.ilike(f"%{departure_city}%"))
            )
        if destination_city:
            dest_airport = Airport.__table__.alias("dest_airport")
            query = query.join(dest_airport, Flight.destination_airport_id == dest_airport.c.id).filter(
                or_(dest_airport.c.city.ilike(f"%{destination_city}%"),
                    dest_airport.c.code.ilike(f"%{destination_city}%"))
            )
        if dep_date:
            query = query.filter(Flight.departure_date == dep_date)
        if status and status != "All":
            query = query.filter(Flight.status == status)
        return query.order_by(Flight.departure_date, Flight.departure_time).all()
    finally:
        session.close()


def get_flight_by_id(flight_id):
    session = get_session()
    try:
        return session.query(Flight).options(*_FLIGHT_EAGER).filter(Flight.id == flight_id).first()
    finally:
        session.close()


def create_flight(data: dict):
    session = get_session()
    try:
        flight = Flight(**data)
        session.add(flight)
        session.commit()
        return flight.id
    finally:
        session.close()


def update_flight(flight_id: int, data: dict):
    session = get_session()
    try:
        flight = session.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            return False
        for key, value in data.items():
            setattr(flight, key, value)
        session.commit()
        return True
    finally:
        session.close()


def delete_flight(flight_id: int):
    session = get_session()
    try:
        flight = session.query(Flight).filter(Flight.id == flight_id).first()
        if flight:
            session.delete(flight)
            session.commit()
            return True
        return False
    finally:
        session.close()


# ---------- Passengers ----------

def get_all_passengers():
    session = get_session()
    try:
        return session.query(Passenger).order_by(Passenger.full_name).all()
    finally:
        session.close()


def search_passengers(term: str):
    session = get_session()
    try:
        if not term:
            return session.query(Passenger).order_by(Passenger.full_name).all()
        like = f"%{term}%"
        return session.query(Passenger).filter(
            or_(Passenger.full_name.ilike(like),
                Passenger.passport_number.ilike(like),
                Passenger.email.ilike(like),
                Passenger.phone_number.ilike(like))
        ).order_by(Passenger.full_name).all()
    finally:
        session.close()


def get_passenger_by_id(passenger_id):
    session = get_session()
    try:
        return session.query(Passenger).filter(Passenger.id == passenger_id).first()
    finally:
        session.close()


def create_passenger(data: dict):
    session = get_session()
    try:
        passenger = Passenger(**data)
        session.add(passenger)
        session.commit()
        return passenger.id
    finally:
        session.close()


def update_passenger(passenger_id: int, data: dict):
    session = get_session()
    try:
        passenger = session.query(Passenger).filter(Passenger.id == passenger_id).first()
        if not passenger:
            return False
        for key, value in data.items():
            setattr(passenger, key, value)
        session.commit()
        return True
    finally:
        session.close()


def delete_passenger(passenger_id: int):
    session = get_session()
    try:
        passenger = session.query(Passenger).filter(Passenger.id == passenger_id).first()
        if passenger:
            session.delete(passenger)
            session.commit()
            return True
        return False
    finally:
        session.close()


# ---------- Bookings ----------

def get_all_bookings():
    session = get_session()
    try:
        return session.query(Booking).options(*_BOOKING_EAGER).order_by(Booking.booked_at.desc()).all()
    finally:
        session.close()


def get_booking_by_id(booking_id):
    session = get_session()
    try:
        return session.query(Booking).options(*_BOOKING_EAGER).filter(Booking.id == booking_id).first()
    finally:
        session.close()


def get_booking_by_reference(reference: str):
    session = get_session()
    try:
        return session.query(Booking).options(*_BOOKING_EAGER).filter(
            Booking.booking_reference == reference
        ).first()
    finally:
        session.close()


def get_taken_seats(flight_id: int):
    session = get_session()
    try:
        rows = session.query(Booking.seat_number).filter(
            Booking.flight_id == flight_id, Booking.status != "Cancelled"
        ).all()
        return {r[0] for r in rows}
    finally:
        session.close()


def create_booking(passenger_id: int, flight_id: int, seat_number: str, fare_paid: float,
                    booking_reference: str):
    session = get_session()
    try:
        flight = session.query(Flight).filter(Flight.id == flight_id).first()
        if not flight or flight.available_seats <= 0:
            return None
        booking = Booking(
            booking_reference=booking_reference,
            passenger_id=passenger_id,
            flight_id=flight_id,
            seat_number=seat_number,
            fare_paid=fare_paid,
            status="Confirmed",
        )
        flight.available_seats -= 1
        session.add(booking)
        session.commit()
        return booking.id
    finally:
        session.close()


def update_booking_status(booking_id: int, status: str):
    session = get_session()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        old_status = booking.status
        booking.status = status
        if status == "Cancelled" and old_status != "Cancelled":
            booking.flight.available_seats += 1
        session.commit()
        return True
    finally:
        session.close()


# ---------- Dashboard aggregates ----------

def dashboard_stats():
    session = get_session()
    try:
        total_flights = session.query(func.count(Flight.id)).scalar() or 0
        active_flights = session.query(func.count(Flight.id)).filter(
            Flight.status.in_(["Scheduled", "Boarding", "Delayed"])
        ).scalar() or 0
        cancelled_flights = session.query(func.count(Flight.id)).filter(
            Flight.status == "Cancelled"
        ).scalar() or 0
        total_passengers = session.query(func.count(Passenger.id)).scalar() or 0
        total_bookings = session.query(func.count(Booking.id)).scalar() or 0
        available_seats = session.query(func.sum(Flight.available_seats)).scalar() or 0
        today_flights = session.query(func.count(Flight.id)).filter(
            Flight.departure_date == date.today()
        ).scalar() or 0
        revenue = session.query(func.sum(Booking.fare_paid)).filter(
            Booking.status != "Cancelled"
        ).scalar() or 0.0

        status_counts = dict(
            session.query(Flight.status, func.count(Flight.id)).group_by(Flight.status).all()
        )

        airline_counts = dict(
            session.query(Flight.airline, func.count(Flight.id)).group_by(Flight.airline)
            .order_by(func.count(Flight.id).desc()).limit(8).all()
        )

        nationality_counts = dict(
            session.query(Passenger.nationality, func.count(Passenger.id))
            .group_by(Passenger.nationality)
            .order_by(func.count(Passenger.id).desc()).limit(10).all()
        )

        return {
            "total_flights": total_flights,
            "active_flights": active_flights,
            "cancelled_flights": cancelled_flights,
            "total_passengers": total_passengers,
            "total_bookings": total_bookings,
            "available_seats": int(available_seats),
            "today_flights": today_flights,
            "revenue": float(revenue),
            "status_counts": status_counts,
            "airline_counts": airline_counts,
            "nationality_counts": nationality_counts,
        }
    finally:
        session.close()


def bookings_trend(days=7):
    """Return (date_list, count_list) for bookings made in the last N days."""
    from datetime import timedelta
    session = get_session()
    try:
        today = date.today()
        results = []
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            count = session.query(func.count(Booking.id)).filter(
                func.date(Booking.booked_at) == day
            ).scalar() or 0
            results.append((day, count))
        return [r[0] for r in results], [r[1] for r in results]
    finally:
        session.close()


# ---------- Users ----------

def get_all_users():
    session = get_session()
    try:
        return session.query(User).order_by(User.full_name).all()
    finally:
        session.close()


def create_user(data: dict):
    session = get_session()
    try:
        user = User(**data)
        session.add(user)
        session.commit()
        return user.id
    finally:
        session.close()


def update_user_status(user_id: int, is_active: int):
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.is_active = is_active
        session.commit()
        return True
    finally:
        session.close()
