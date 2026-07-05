import streamlit as st
import pandas as pd
from datetime import date, time

from database.queries import (
    search_flights, get_all_airports, get_all_aircraft, create_flight,
    update_flight, delete_flight, get_flight_by_id
)
from models.flight import FLIGHT_STATUSES
from utils.styling import status_badge_html
from utils.helpers import format_currency, format_date, format_time, paginate
from authentication.auth import is_admin, require_login


def _airport_options():
    airports = get_all_airports()
    return {f"{a.city} ({a.code})": a.id for a in airports}


def _aircraft_options():
    aircraft = get_all_aircraft()
    return {f"{a.model}": a.id for a in aircraft}


def render():
    require_login()
    st.markdown("### Flight Management")
    st.caption("Search, filter, and manage all scheduled flights.")

    if is_admin():
        tab_list, tab_add = st.tabs(["View & Search Flights", "Add New Flight"])
    else:
        tab_list = st.container()
        tab_add = None

    with tab_list:
        with st.expander("Search & Filter", expanded=True):
            c1, c2, c3 = st.columns(3)
            flight_number = c1.text_input("Flight Number", key="f_search_num")
            airline = c2.text_input("Airline", key="f_search_airline")
            status = c3.selectbox("Status", ["All"] + FLIGHT_STATUSES, key="f_search_status")

            c4, c5, c6 = st.columns(3)
            departure_city = c4.text_input("Departure (city or code)", key="f_search_dep")
            destination_city = c5.text_input("Destination (city or code)", key="f_search_dest")
            use_date = c6.checkbox("Filter by date")
            dep_date = c6.date_input("Departure date", value=date.today()) if use_date else None

        flights = search_flights(
            flight_number=flight_number or None,
            airline=airline or None,
            departure_city=departure_city or None,
            destination_city=destination_city or None,
            dep_date=dep_date,
            status=status,
        )

        st.write(f"**{len(flights)} flight(s) found**")

        if "flight_page" not in st.session_state:
            st.session_state["flight_page"] = 1

        page_items, total_pages = paginate(flights, st.session_state["flight_page"], page_size=10)

        for f in page_items:
            with st.container():
                cols = st.columns([1, 1.6, 2.4, 2.4, 1.3, 1, 1, 1.2])
                cols[0].markdown(f"**{f.flight_number}**")
                cols[1].write(f.airline)
                cols[2].write(f"{f.departure_airport.label} \u2192 {f.destination_airport.label}"
                               if f.departure_airport and f.destination_airport else "-")
                cols[3].write(f"{format_date(f.departure_date)} \u00B7 {format_time(f.departure_time)}")
                cols[4].markdown(status_badge_html(f.status), unsafe_allow_html=True)
                cols[5].write(format_currency(f.ticket_price))
                cols[6].write(f"{f.available_seats}/{f.total_seats} seats")
                if is_admin():
                    if cols[7].button("Manage", key=f"manage_{f.id}"):
                        st.session_state["editing_flight_id"] = f.id
                st.divider()

        pc1, pc2, pc3 = st.columns([1, 2, 1])
        if pc1.button("\u2190 Previous", disabled=st.session_state["flight_page"] <= 1):
            st.session_state["flight_page"] -= 1
            st.rerun()
        pc2.markdown(f"<div style='text-align:center;'>Page {st.session_state['flight_page']} of {total_pages}</div>", unsafe_allow_html=True)
        if pc3.button("Next \u2192", disabled=st.session_state["flight_page"] >= total_pages):
            st.session_state["flight_page"] += 1
            st.rerun()

        if is_admin() and st.session_state.get("editing_flight_id"):
            _render_edit_panel(st.session_state["editing_flight_id"])

    if is_admin() and tab_add is not None:
        with tab_add:
            _render_add_form()


def _render_add_form():
    st.markdown("#### Add New Flight")
    airport_opts = _airport_options()
    aircraft_opts = _aircraft_options()

    if not airport_opts or not aircraft_opts:
        st.warning("Please add airports and aircraft before creating flights.")
        return

    with st.form("add_flight_form"):
        c1, c2 = st.columns(2)
        flight_number = c1.text_input("Flight Number*", placeholder="e.g. SW450")
        airline = c2.text_input("Airline*", placeholder="e.g. SkyWings Airlines")

        c3, c4 = st.columns(2)
        dep_airport_label = c3.selectbox("Departure Airport*", list(airport_opts.keys()))
        dest_airport_label = c4.selectbox("Destination Airport*", list(airport_opts.keys()))

        c5, c6, c7 = st.columns(3)
        dep_date = c5.date_input("Departure Date*", value=date.today())
        dep_time = c6.time_input("Departure Time*", value=time(9, 0))
        arr_time = c7.time_input("Arrival Time*", value=time(12, 0))

        c8, c9, c10 = st.columns(3)
        aircraft_label = c8.selectbox("Aircraft*", list(aircraft_opts.keys()))
        gate = c9.text_input("Gate", placeholder="e.g. A12")
        terminal = c10.text_input("Terminal", placeholder="e.g. 2")

        c11, c12, c13 = st.columns(3)
        price = c11.number_input("Ticket Price ($)*", min_value=0.0, value=250.0, step=10.0)
        total_seats = c12.number_input("Total Seats*", min_value=1, value=180, step=1)
        status = c13.selectbox("Status", FLIGHT_STATUSES)

        submitted = st.form_submit_button("Add Flight", type="primary")

        if submitted:
            if dep_airport_label == dest_airport_label:
                st.error("Departure and destination airports must be different.")
            elif not flight_number or not airline:
                st.error("Flight number and airline are required.")
            else:
                create_flight({
                    "flight_number": flight_number.upper().strip(),
                    "airline": airline.strip(),
                    "aircraft_id": aircraft_opts[aircraft_label],
                    "departure_airport_id": airport_opts[dep_airport_label],
                    "destination_airport_id": airport_opts[dest_airport_label],
                    "departure_date": dep_date,
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "gate": gate,
                    "terminal": terminal,
                    "ticket_price": price,
                    "total_seats": int(total_seats),
                    "available_seats": int(total_seats),
                    "status": status,
                })
                st.success(f"Flight {flight_number.upper()} added successfully!")
                st.rerun()


def _render_edit_panel(flight_id):
    flight = get_flight_by_id(flight_id)
    if not flight:
        st.session_state["editing_flight_id"] = None
        return

    st.markdown("---")
    st.markdown(f"#### Manage Flight — {flight.flight_number}")
    airport_opts = _airport_options()
    aircraft_opts = _aircraft_options()

    airport_labels = list(airport_opts.keys())
    aircraft_labels = list(aircraft_opts.keys())

    dep_label_current = next((k for k, v in airport_opts.items() if v == flight.departure_airport_id), airport_labels[0])
    dest_label_current = next((k for k, v in airport_opts.items() if v == flight.destination_airport_id), airport_labels[0])
    aircraft_label_current = next((k for k, v in aircraft_opts.items() if v == flight.aircraft_id), aircraft_labels[0])

    with st.form(f"edit_flight_{flight_id}"):
        c1, c2 = st.columns(2)
        airline = c1.text_input("Airline", value=flight.airline)
        status = c2.selectbox("Status", FLIGHT_STATUSES, index=FLIGHT_STATUSES.index(flight.status))

        c3, c4 = st.columns(2)
        dep_airport_label = c3.selectbox("Departure Airport", airport_labels, index=airport_labels.index(dep_label_current))
        dest_airport_label = c4.selectbox("Destination Airport", airport_labels, index=airport_labels.index(dest_label_current))

        c5, c6, c7 = st.columns(3)
        dep_date = c5.date_input("Departure Date", value=flight.departure_date)
        dep_time = c6.time_input("Departure Time", value=flight.departure_time)
        arr_time = c7.time_input("Arrival Time", value=flight.arrival_time)

        c8, c9, c10 = st.columns(3)
        gate = c8.text_input("Gate", value=flight.gate or "")
        terminal = c9.text_input("Terminal", value=flight.terminal or "")
        price = c10.number_input("Ticket Price ($)", min_value=0.0, value=float(flight.ticket_price), step=10.0)

        available_seats = st.number_input("Available Seats", min_value=0, max_value=flight.total_seats,
                                           value=flight.available_seats, step=1)

        col_save, col_delete, col_cancel = st.columns(3)
        save = col_save.form_submit_button("Save Changes", type="primary")
        delete = col_delete.form_submit_button("Delete Flight")
        cancel = col_cancel.form_submit_button("Cancel")

        if save:
            update_flight(flight_id, {
                "airline": airline,
                "status": status,
                "departure_airport_id": airport_opts[dep_airport_label],
                "destination_airport_id": airport_opts[dest_airport_label],
                "departure_date": dep_date,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "gate": gate,
                "terminal": terminal,
                "ticket_price": price,
                "available_seats": int(available_seats),
            })
            st.success("Flight updated successfully.")
            st.session_state["editing_flight_id"] = None
            st.rerun()

        if delete:
            delete_flight(flight_id)
            st.success("Flight deleted.")
            st.session_state["editing_flight_id"] = None
            st.rerun()

        if cancel:
            st.session_state["editing_flight_id"] = None
            st.rerun()
