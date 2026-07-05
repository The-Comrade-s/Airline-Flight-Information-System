import streamlit as st
import pandas as pd
from datetime import date, timedelta

from database.queries import (
    get_all_flights, get_all_passengers, get_all_bookings, dashboard_stats
)
from utils.charts import revenue_bar_chart, passenger_demographics_bar, flight_status_pie
from utils.helpers import format_currency, format_date, format_time
from utils.export_utils import dataframe_to_csv_bytes
from utils.pdf_utils import generate_report_pdf
from authentication.auth import require_login


def render():
    require_login()
    st.markdown("### Reports & Analytics")
    st.caption("Generate and export professional reports.")

    report_type = st.selectbox(
        "Select Report",
        ["Flight Report", "Passenger Report", "Booking Report", "Revenue Report", "Daily Report", "Monthly Report"],
    )

    if report_type == "Flight Report":
        _flight_report()
    elif report_type == "Passenger Report":
        _passenger_report()
    elif report_type == "Booking Report":
        _booking_report()
    elif report_type == "Revenue Report":
        _revenue_report()
    elif report_type == "Daily Report":
        _daily_report()
    elif report_type == "Monthly Report":
        _monthly_report()


def _export_buttons(df, headers, rows, title, key_prefix):
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "\U0001F4E5 Export CSV", data=dataframe_to_csv_bytes(df),
            file_name=f"{key_prefix}.csv", mime="text/csv", use_container_width=True,
        )
    with c2:
        pdf_bytes = generate_report_pdf(title, headers, rows)
        st.download_button(
            "\U0001F4C4 Export PDF", data=pdf_bytes,
            file_name=f"{key_prefix}.pdf", mime="application/pdf", use_container_width=True,
        )


def _flight_report():
    flights = get_all_flights()
    df = pd.DataFrame([{
        "Flight Number": f.flight_number,
        "Airline": f.airline,
        "From": f.departure_airport.code if f.departure_airport else "-",
        "To": f.destination_airport.code if f.destination_airport else "-",
        "Date": format_date(f.departure_date),
        "Departure": format_time(f.departure_time),
        "Status": f.status,
        "Price": f.ticket_price,
        "Available Seats": f.available_seats,
    } for f in flights])

    st.dataframe(df, use_container_width=True, height=400)
    if not df.empty:
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        _export_buttons(df, headers, rows, "Flight Report", "flight_report")


def _passenger_report():
    passengers = get_all_passengers()
    df = pd.DataFrame([{
        "Full Name": p.full_name,
        "Gender": p.gender,
        "Date of Birth": format_date(p.date_of_birth),
        "Nationality": p.nationality,
        "Passport": p.passport_number,
        "Phone": p.phone_number,
        "Email": p.email,
    } for p in passengers])

    st.dataframe(df, use_container_width=True, height=400)

    stats = dashboard_stats()
    if stats["nationality_counts"]:
        fig = passenger_demographics_bar(
            list(stats["nationality_counts"].keys()),
            list(stats["nationality_counts"].values()),
        )
        st.plotly_chart(fig, use_container_width=True)

    if not df.empty:
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        _export_buttons(df, headers, rows, "Passenger Report", "passenger_report")


def _booking_report():
    bookings = get_all_bookings()
    df = pd.DataFrame([{
        "Reference": b.booking_reference,
        "Passenger": b.passenger.full_name,
        "Flight": b.flight.flight_number,
        "Seat": b.seat_number,
        "Fare Paid": b.fare_paid,
        "Status": b.status,
        "Booked At": b.booked_at.strftime("%d %b %Y %H:%M") if b.booked_at else "-",
    } for b in bookings])

    st.dataframe(df, use_container_width=True, height=400)
    if not df.empty:
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        _export_buttons(df, headers, rows, "Booking Report", "booking_report")


def _revenue_report():
    bookings = get_all_bookings()
    active = [b for b in bookings if b.status != "Cancelled"]

    by_airline = {}
    for b in active:
        airline = b.flight.airline
        by_airline[airline] = by_airline.get(airline, 0) + b.fare_paid

    if by_airline:
        fig = revenue_bar_chart(list(by_airline.keys()), list(by_airline.values()), title="Revenue by Airline")
        st.plotly_chart(fig, use_container_width=True)

    total_revenue = sum(by_airline.values())
    st.metric("Total Revenue", format_currency(total_revenue))

    df = pd.DataFrame([{"Airline": k, "Revenue": round(v, 2)} for k, v in by_airline.items()])
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        _export_buttons(df, headers, rows, "Revenue Report", "revenue_report")


def _daily_report():
    target_date = st.date_input("Select date", value=date.today())
    flights = [f for f in get_all_flights() if f.departure_date == target_date]
    bookings = [b for b in get_all_bookings() if b.flight.departure_date == target_date]

    c1, c2 = st.columns(2)
    c1.metric("Flights on this Date", len(flights))
    c2.metric("Bookings Made / Traveling", len(bookings))

    df = pd.DataFrame([{
        "Flight Number": f.flight_number, "Airline": f.airline,
        "From": f.departure_airport.code, "To": f.destination_airport.code,
        "Departure": format_time(f.departure_time), "Status": f.status,
    } for f in flights])
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        _export_buttons(df, headers, rows, f"Daily Report - {target_date}", f"daily_report_{target_date}")


def _monthly_report():
    today = date.today()
    month_start = today.replace(day=1)
    flights = [f for f in get_all_flights() if f.departure_date >= month_start]
    bookings = [b for b in get_all_bookings() if b.flight.departure_date >= month_start and b.status != "Cancelled"]
    revenue = sum(b.fare_paid for b in bookings)

    c1, c2, c3 = st.columns(3)
    c1.metric("Flights This Month", len(flights))
    c2.metric("Bookings This Month", len(bookings))
    c3.metric("Revenue This Month", format_currency(revenue))

    status_counts = {}
    for f in flights:
        status_counts[f.status] = status_counts.get(f.status, 0) + 1
    if status_counts:
        fig = flight_status_pie(status_counts, title=f"Flight Status — {today.strftime('%B %Y')}")
        st.plotly_chart(fig, use_container_width=True)

    df = pd.DataFrame([{
        "Flight Number": f.flight_number, "Airline": f.airline, "Date": format_date(f.departure_date),
        "Status": f.status, "Price": f.ticket_price,
    } for f in flights])
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        _export_buttons(df, headers, rows, f"Monthly Report - {today.strftime('%B %Y')}", "monthly_report")
