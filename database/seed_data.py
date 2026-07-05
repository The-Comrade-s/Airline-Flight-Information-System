"""
Populates the database with realistic sample data:
- Airports, aircraft, airlines
- 40+ flights
- 120+ passengers
- Random bookings
- One default administrator and one staff user

Safe to re-run: it checks whether data already exists and skips
if the database has already been seeded.
"""

import random
import string
from datetime import date, time, timedelta, datetime

from database.connection import get_session
from database.init_db import init_db
from models import User, Airport, Aircraft, Flight, Passenger, Booking
from authentication.auth import hash_password

random.seed(42)

AIRPORTS = [
    ("JFK", "John F. Kennedy International Airport", "New York", "USA"),
    ("LHR", "Heathrow Airport", "London", "United Kingdom"),
    ("DXB", "Dubai International Airport", "Dubai", "UAE"),
    ("CDG", "Charles de Gaulle Airport", "Paris", "France"),
    ("HND", "Haneda Airport", "Tokyo", "Japan"),
    ("SIN", "Changi Airport", "Singapore", "Singapore"),
    ("LOS", "Murtala Muhammed International Airport", "Lagos", "Nigeria"),
    ("ABV", "Nnamdi Azikiwe International Airport", "Abuja", "Nigeria"),
    ("JNB", "O.R. Tambo International Airport", "Johannesburg", "South Africa"),
    ("CPT", "Cape Town International Airport", "Cape Town", "South Africa"),
    ("DOH", "Hamad International Airport", "Doha", "Qatar"),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
    ("SYD", "Sydney Kingsford Smith Airport", "Sydney", "Australia"),
    ("YYZ", "Toronto Pearson International Airport", "Toronto", "Canada"),
    ("GRU", "São Paulo–Guarulhos International Airport", "São Paulo", "Brazil"),
    ("AMS", "Amsterdam Airport Schiphol", "Amsterdam", "Netherlands"),
    ("IST", "Istanbul Airport", "Istanbul", "Turkey"),
    ("HKG", "Hong Kong International Airport", "Hong Kong", "Hong Kong"),
    ("NBO", "Jomo Kenyatta International Airport", "Nairobi", "Kenya"),
    ("ACC", "Kotoka International Airport", "Accra", "Ghana"),
]

AIRCRAFT = [
    ("Boeing 777-300ER", "Boeing", 396, "3-4-3"),
    ("Boeing 787-9 Dreamliner", "Boeing", 290, "3-3-3"),
    ("Boeing 737-800", "Boeing", 189, "3-3"),
    ("Airbus A380-800", "Airbus", 555, "3-4-3"),
    ("Airbus A350-900", "Airbus", 325, "3-3-3"),
    ("Airbus A320neo", "Airbus", 180, "3-3"),
    ("Airbus A330-300", "Airbus", 277, "2-4-2"),
    ("Embraer E190", "Embraer", 100, "2-2"),
]

AIRLINES = [
    "SkyWings Airlines",
    "Emirates",
    "Qatar Airways",
    "British Airways",
    "Air France",
    "Lufthansa",
    "Singapore Airlines",
    "Delta Air Lines",
    "Turkish Airlines",
    "Ethiopian Airlines",
]

FLIGHT_STATUS_WEIGHTS = [
    ("Scheduled", 45),
    ("Boarding", 15),
    ("Delayed", 15),
    ("Landed", 20),
    ("Cancelled", 5),
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Chinedu", "Amaka", "Oluwaseun", "Ngozi",
    "Kwame", "Aisha", "Fatima", "Yusuf", "Ahmed", "Aaliyah", "Wei", "Mei", "Hiroshi",
    "Yuki", "Arjun", "Priya", "Carlos", "Sofia", "Lucas", "Isabella", "Mohammed",
    "Layla", "Ivan", "Olga", "Liam", "Emma", "Noah", "Olivia", "Ethan", "Ava",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Okafor", "Adeyemi", "Balogun", "Mensah", "Osei", "Diallo",
    "Kimura", "Tanaka", "Sato", "Patel", "Sharma", "Khan", "Ali", "Ibrahim", "Hassan",
    "Silva", "Santos", "Pereira", "Rossi", "Moreau", "Bernard", "Schmidt", "Müller",
    "Ivanov", "Petrov", "Nguyen", "Tran", "Lee", "Kim", "Park", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lewis", "Clark", "Walker",
]
NATIONALITIES = [
    "American", "British", "Nigerian", "French", "German", "Japanese", "Emirati",
    "Qatari", "South African", "Canadian", "Brazilian", "Turkish", "Kenyan", "Ghanaian",
    "Indian", "Chinese", "Australian", "Dutch", "Singaporean", "Egyptian",
]


def _random_flight_number(airline_index):
    prefix = "".join(c for c in AIRLINES[airline_index] if c.isupper())[:2] or "SW"
    return f"{prefix}{random.randint(100, 999)}"


def _weighted_status():
    statuses, weights = zip(*FLIGHT_STATUS_WEIGHTS)
    return random.choices(statuses, weights=weights, k=1)[0]


def _random_passport():
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    digits = "".join(random.choices(string.digits, k=7))
    return f"{letters}{digits}"


def seed_airports(session):
    if session.query(Airport).count() > 0:
        return
    for code, name, city, country in AIRPORTS:
        session.add(Airport(code=code, name=name, city=city, country=country))
    session.commit()


def seed_aircraft(session):
    if session.query(Aircraft).count() > 0:
        return
    for model, manufacturer, seats, layout in AIRCRAFT:
        session.add(Aircraft(model=model, manufacturer=manufacturer,
                              total_seats=seats, seat_layout=layout))
    session.commit()


def seed_users(session):
    if session.query(User).count() > 0:
        return
    session.add(User(
        full_name="Admin User",
        username="admin",
        email="admin@skywings.com",
        password_hash=hash_password("Admin@123"),
        role="Administrator",
    ))
    session.add(User(
        full_name="Staff Member",
        username="staff",
        email="staff@skywings.com",
        password_hash=hash_password("Staff@123"),
        role="Staff",
    ))
    session.commit()


def seed_flights(session, count=48):
    if session.query(Flight).count() > 0:
        return
    airports = session.query(Airport).all()
    aircraft_list = session.query(Aircraft).all()
    today = date.today()
    used_numbers = set()

    for _ in range(count):
        dep_airport, dest_airport = random.sample(airports, 2)
        aircraft = random.choice(aircraft_list)
        airline_index = random.randrange(len(AIRLINES))
        airline = AIRLINES[airline_index]

        flight_number = _random_flight_number(airline_index)
        while flight_number in used_numbers:
            flight_number = _random_flight_number(airline_index)
        used_numbers.add(flight_number)

        dep_offset_days = random.randint(-5, 21)
        departure_date = today + timedelta(days=dep_offset_days)
        dep_hour = random.randint(0, 23)
        dep_minute = random.choice([0, 15, 30, 45])
        departure_time = time(dep_hour, dep_minute)

        duration_minutes = random.randint(90, 780)
        dep_dt = datetime.combine(departure_date, departure_time)
        arrival_dt = dep_dt + timedelta(minutes=duration_minutes)
        arrival_time = arrival_dt.time()

        total_seats = aircraft.total_seats
        booked_ratio = random.uniform(0.1, 0.95)
        available_seats = max(0, int(total_seats * (1 - booked_ratio)))

        base_price = random.uniform(120, 2400)
        status = _weighted_status()
        if departure_date < today:
            status = random.choice(["Landed", "Cancelled"])

        flight = Flight(
            flight_number=flight_number,
            airline=airline,
            aircraft_id=aircraft.id,
            departure_airport_id=dep_airport.id,
            destination_airport_id=dest_airport.id,
            departure_date=departure_date,
            departure_time=departure_time,
            arrival_time=arrival_time,
            gate=f"{random.choice('ABCDEF')}{random.randint(1, 32)}",
            terminal=str(random.randint(1, 5)),
            ticket_price=round(base_price, 2),
            total_seats=total_seats,
            available_seats=available_seats,
            status=status,
        )
        session.add(flight)

    session.commit()


def seed_passengers(session, count=130):
    if session.query(Passenger).count() > 0:
        return
    used_passports = set()
    today = date.today()

    for _ in range(count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"

        passport = _random_passport()
        while passport in used_passports:
            passport = _random_passport()
        used_passports.add(passport)

        age_years = random.randint(4, 82)
        dob = today - timedelta(days=age_years * 365 + random.randint(0, 364))

        passenger = Passenger(
            full_name=full_name,
            gender=random.choice(["Male", "Female"]),
            date_of_birth=dob,
            nationality=random.choice(NATIONALITIES),
            passport_number=passport,
            phone_number=f"+{random.randint(1, 999)}{random.randint(1000000, 9999999)}",
            email=f"{first.lower()}.{last.lower()}{random.randint(1,99)}@example.com",
        )
        session.add(passenger)

    session.commit()


def _random_booking_reference(used):
    ref = "SW" + "".join(random.choices(string.digits, k=7))
    while ref in used:
        ref = "SW" + "".join(random.choices(string.digits, k=7))
    used.add(ref)
    return ref


def _random_seat(aircraft_layout):
    row_size = sum(int(x) for x in aircraft_layout.split("-"))
    letters = string.ascii_uppercase[:row_size]
    row = random.randint(1, 45)
    return f"{row}{random.choice(letters)}"


def seed_bookings(session, count=160):
    if session.query(Booking).count() > 0:
        return
    passengers = session.query(Passenger).all()
    flights = session.query(Flight).filter(Flight.status != "Cancelled").all()
    used_refs = set()
    used_seats_per_flight = {}

    if not passengers or not flights:
        return

    for _ in range(count):
        flight = random.choice(flights)
        passenger = random.choice(passengers)

        seats_taken = used_seats_per_flight.setdefault(flight.id, set())
        seat = _random_seat(flight.aircraft.seat_layout if flight.aircraft else "3-3")
        attempts = 0
        while seat in seats_taken and attempts < 10:
            seat = _random_seat(flight.aircraft.seat_layout if flight.aircraft else "3-3")
            attempts += 1
        seats_taken.add(seat)

        status = random.choices(
            ["Confirmed", "Checked-in", "Boarded", "Completed", "Cancelled"],
            weights=[40, 20, 10, 25, 5], k=1
        )[0]

        booking = Booking(
            booking_reference=_random_booking_reference(used_refs),
            passenger_id=passenger.id,
            flight_id=flight.id,
            seat_number=seat,
            fare_paid=round(flight.ticket_price * random.uniform(0.9, 1.15), 2),
            status=status,
        )
        session.add(booking)

    session.commit()


def seed_all():
    init_db()
    session = get_session()
    try:
        seed_airports(session)
        seed_aircraft(session)
        seed_users(session)
        seed_flights(session, count=48)
        seed_passengers(session, count=130)
        seed_bookings(session, count=170)
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()
    print("Database seeded successfully.")
