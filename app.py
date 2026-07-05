"""
SkyWings — Airline Flight Information System
Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="SkyWings | Flight Information System",
    page_icon="\u2708\uFE0F",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.seed_data import seed_all
from authentication.auth import is_authenticated
from utils.styling import inject_global_css
from utils.navigation import render_sidebar
from pages_login import render_login

from pages import dashboard, flights, booking, passengers, bookings, reports, aircraft, airports, staff, settings


@st.cache_resource
def _bootstrap_database():
    """Create tables and seed sample data once per server process."""
    seed_all()
    return True


def main():
    _bootstrap_database()

    inject_global_css(dark_mode=st.session_state.get("dark_mode", False))

    if not is_authenticated():
        render_login()
        return

    current_page = render_sidebar()

    page_map = {
        "Dashboard": dashboard.render,
        "Flights": flights.render,
        "Book Flight": booking.render,
        "Passengers": passengers.render,
        "Bookings": bookings.render,
        "Reports": reports.render,
        "Aircraft": aircraft.render,
        "Airports": airports.render,
        "Staff": staff.render,
        "Settings": settings.render,
    }

    render_fn = page_map.get(current_page, dashboard.render)
    render_fn()


if __name__ == "__main__":
    main()
