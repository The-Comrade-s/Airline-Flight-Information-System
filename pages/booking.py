import streamlit as st
import string
from datetime import date

from database.queries import (
    search_flights, get_all_passengers, get_taken_seats, create_booking,
    get_booking_by_id, create_passenger
)
from utils.styling import status_badge_html, PALETTE
from utils.helpers import (
    format_currency, format_date, format_time, duration_between,
    generate_booking_reference
)
from utils.pdf_utils import generate_ticket_pdf
from utils.qr_utils import generate_qr_bytes, boarding_pass_qr_payload
from authentication.auth import require_login


def render():
    require_login()
    st.markdown("### Book a Flight")
    st.caption("Search flights, select a passenger, choose a seat, and confirm the booking.")

    step = st.session_state.get("booking_step", 1)

    if step == 1:
        _step_search()
    elif step == 2:
        _step_select_passenger()
    elif step == 3:
        _step_select_seat()
    elif step == 4:
        _step_confirmation()


def _reset_booking():
    for key in ["booking_step", "selected_flight_id", "selected_passenger_id",
                "selected_seat", "selected_seat_row", "completed_booking_id",
                "last_search_results"]:
        st.session_state.pop(key, None)


def _step_search():
    with st.expander("Search Criteria", expanded=True):
        c1, c2, c3 = st.columns(3)
        departure_city = c1.text_input("From (city or code)")
        destination_city = c2.text_input("To (city or code)")
        dep_date = c3.date_input("Departure Date", value=date.today())
        c4, c5 = st.columns(2)
        airline = c4.text_input("Airline (optional)")
        search_clicked = c5.button("Search Flights", type="primary", use_container_width=True)

    if search_clicked or "last_search_results" in st.session_state:
        if search_clicked:
            results = search_flights(
                departure_city=departure_city or None,
                destination_city=destination_city or None,
                dep_date=dep_date,
                airline=airline or None,
                status=None,
            )
            results = [f for f in results if f.status != "Cancelled" and f.available_seats > 0]
            st.session_state["last_search_results"] = [f.id for f in results]

        from database.queries import get_flight_by_id
        flight_ids = st.session_state.get("last_search_results", [])
        flights = [get_flight_by_id(fid) for fid in flight_ids]
        flights = [f for f in flights if f]

        st.write(f"**{len(flights)} flight(s) available**")
        for f in flights:
            with st.container():
                st.markdown('<div class="sw-card">', unsafe_allow_html=True)
                cols = st.columns([1.3, 2.6, 1.3, 1.3, 1.3, 1.2])
                cols[0].markdown(f"**{f.flight_number}**<br>{f.airline}", unsafe_allow_html=True)
                cols[1].markdown(
                    f"{f.departure_airport.label} &#8594; {f.destination_airport.label}<br>"
                    f"<span style='color:{PALETTE['muted']};font-size:14px;'>{format_date(f.departure_date)}</span>",
                    unsafe_allow_html=True,
                )
                cols[2].markdown(f"**{format_time(f.departure_time)}**<br>Departure", unsafe_allow_html=True)
                cols[3].markdown(
                    f"**{duration_between(f.departure_date, f.departure_time, f.arrival_time)}**<br>"
                    f"Lands {format_time(f.arrival_time)}",
                    unsafe_allow_html=True,
                )
                cols[4].markdown(f"**{format_currency(f.ticket_price)}**<br>{f.available_seats} seats left", unsafe_allow_html=True)
                if cols[5].button("Select", key=f"select_flight_{f.id}", type="primary"):
                    st.session_state["selected_flight_id"] = f.id
                    st.session_state["booking_step"] = 2
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.write("")


def _step_select_passenger():
    from database.queries import get_flight_by_id
    flight = get_flight_by_id(st.session_state["selected_flight_id"])
    if not flight:
        st.error("Selected flight no longer exists.")
        _reset_booking()
        st.rerun()
        return

    st.info(f"Flight **{flight.flight_number}** \u00B7 {flight.departure_airport.label} \u2192 "
            f"{flight.destination_airport.label} \u00B7 {format_date(flight.departure_date)}")

    tab_existing, tab_new = st.tabs(["Choose Existing Passenger", "Register New Passenger"])

    with tab_existing:
        passengers = get_all_passengers()
        search_term = st.text_input("Search passenger by name or passport number")
        filtered = [p for p in passengers if not search_term or
                    search_term.lower() in p.full_name.lower() or
                    search_term.lower() in (p.passport_number or "").lower()]
        options = {f"{p.full_name} \u2014 {p.passport_number}": p.id for p in filtered[:50]}

        if options:
            selected_label = st.selectbox("Select Passenger", list(options.keys()))
            if st.button("Continue with this Passenger", type="primary"):
                st.session_state["selected_passenger_id"] = options[selected_label]
                st.session_state["booking_step"] = 3
                st.rerun()
        else:
            st.warning("No matching passengers found. Try the 'Register New Passenger' tab.")

    with tab_new:
        with st.form("new_passenger_booking_form"):
            c1, c2 = st.columns(2)
            full_name = c1.text_input("Full Name*")
            gender = c2.selectbox("Gender", ["Male", "Female", "Other"])
            c3, c4 = st.columns(2)
            dob = c3.date_input("Date of Birth", value=date(1990, 1, 1), min_value=date(1920, 1, 1), max_value=date.today())
            nationality = c4.text_input("Nationality")
            c5, c6 = st.columns(2)
            passport_number = c5.text_input("Passport Number*")
            phone = c6.text_input("Phone Number")
            email = st.text_input("Email Address")

            submitted = st.form_submit_button("Register and Continue", type="primary")
            if submitted:
                if not full_name or not passport_number:
                    st.error("Full name and passport number are required.")
                else:
                    new_id = create_passenger({
                        "full_name": full_name,
                        "gender": gender,
                        "date_of_birth": dob,
                        "nationality": nationality,
                        "passport_number": passport_number,
                        "phone_number": phone,
                        "email": email,
                    })
                    st.session_state["selected_passenger_id"] = new_id
                    st.session_state["booking_step"] = 3
                    st.rerun()

    if st.button("\u2190 Back to Flight Search"):
        st.session_state["booking_step"] = 1
        st.rerun()


def _step_select_seat():
    from database.queries import get_flight_by_id, get_passenger_by_id
    flight = get_flight_by_id(st.session_state["selected_flight_id"])
    passenger = get_passenger_by_id(st.session_state["selected_passenger_id"])

    if not flight or not passenger:
        st.error("Session data missing. Please restart booking.")
        _reset_booking()
        st.rerun()
        return

    st.info(f"Passenger: **{passenger.full_name}** \u00B7 Flight **{flight.flight_number}**")
    st.markdown('<div class="sw-section-title">Select Your Seat</div>', unsafe_allow_html=True)

    legend_cols = st.columns(4)
    legend_cols[0].markdown('<div class="seat-available">Available</div>', unsafe_allow_html=True)
    legend_cols[1].markdown('<div class="seat-premium">Premium</div>', unsafe_allow_html=True)
    legend_cols[2].markdown('<div class="seat-selected">Selected</div>', unsafe_allow_html=True)
    legend_cols[3].markdown('<div class="seat-occupied">Occupied</div>', unsafe_allow_html=True)
    st.write("")

    layout = flight.aircraft.seat_layout if flight.aircraft else "3-3"
    row_groups = [int(x) for x in layout.split("-")]
    row_size = sum(row_groups)
    letters = list(string.ascii_uppercase[:row_size])
    num_rows = 12

    taken_seats = get_taken_seats(flight.id)
    selected_seat = st.session_state.get("selected_seat")

    for row in range(1, num_rows + 1):
        cols = st.columns(row_size + 1)
        cols[0].markdown(f"<div style='text-align:center;font-weight:600;padding-top:10px;'>{row}</div>", unsafe_allow_html=True)
        for i, letter in enumerate(letters):
            seat_id = f"{row}{letter}"
            is_taken = seat_id in taken_seats
            is_premium = row <= 3
            is_selected = seat_id == selected_seat

            with cols[i + 1]:
                if is_taken:
                    st.markdown(f'<div class="seat-occupied">{letter}</div>', unsafe_allow_html=True)
                elif is_selected:
                    st.markdown(f'<div class="seat-selected">{letter}</div>', unsafe_allow_html=True)
                else:
                    button_label = f"{letter} \u2605" if is_premium else letter
                    if st.button(button_label, key=f"seat_{seat_id}",
                                 help="Premium seat (extra legroom)" if is_premium else "Available seat"):
                        st.session_state["selected_seat"] = seat_id
                        st.session_state["selected_seat_row"] = row
                        st.rerun()

    st.write("")
    if selected_seat:
        st.success(f"Seat **{selected_seat}** selected.")
        selected_row = st.session_state.get("selected_seat_row", 4)
        fare = flight.ticket_price * (1.35 if selected_row <= 3 else 1.0)
        st.write(f"Fare for this seat: **{format_currency(fare)}**")

        c1, c2 = st.columns(2)
        if c1.button("\u2190 Back", use_container_width=True):
            st.session_state["booking_step"] = 2
            st.rerun()
        if c2.button("Confirm Booking", type="primary", use_container_width=True):
            reference = generate_booking_reference()
            booking_id = create_booking(
                passenger_id=passenger.id,
                flight_id=flight.id,
                seat_number=selected_seat,
                fare_paid=round(fare, 2),
                booking_reference=reference,
            )
            if booking_id:
                st.session_state["completed_booking_id"] = booking_id
                st.session_state["booking_step"] = 4
                st.rerun()
            else:
                st.error("This flight has no more available seats.")
    else:
        st.warning("Please select a seat to continue.")
        if st.button("\u2190 Back"):
            st.session_state["booking_step"] = 2
            st.rerun()


def _step_confirmation():
    booking = get_booking_by_id(st.session_state["completed_booking_id"])
    if not booking:
        st.error("Booking not found.")
        _reset_booking()
        st.rerun()
        return

    flight = booking.flight
    passenger = booking.passenger

    st.markdown(
        f"<div style='text-align:center;'>"
        f"<div style='font-size:52px;'>&#9989;</div>"
        f"<h2 style='color:{PALETTE['success']};margin-top:0;'>Booking Confirmed!</h2>"
        f"<p style='color:{PALETTE['muted']};'>Your booking reference is <strong>{booking.booking_reference}</strong></p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown('<div class="sw-pass">', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown('<div class="sw-pass-label">Passenger</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value">{passenger.full_name}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="sw-pass-label">Flight</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value">{flight.flight_number}</div>', unsafe_allow_html=True)

        st.write("")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="sw-pass-label">From</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value">{flight.departure_airport.code}</div>', unsafe_allow_html=True)
            st.caption(flight.departure_airport.city)
        with c4:
            st.markdown('<div class="sw-pass-label">To</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value">{flight.destination_airport.code}</div>', unsafe_allow_html=True)
            st.caption(flight.destination_airport.city)

        st.markdown('<div class="sw-pass-stub">', unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.markdown('<div class="sw-pass-label">Date</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value" style="font-size:16px;">{format_date(flight.departure_date)}</div>', unsafe_allow_html=True)
        with c6:
            st.markdown('<div class="sw-pass-label">Boarding</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value" style="font-size:16px;">{format_time(flight.departure_time)}</div>', unsafe_allow_html=True)
        with c7:
            st.markdown('<div class="sw-pass-label">Seat</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value" style="font-size:16px;">{booking.seat_number}</div>', unsafe_allow_html=True)
        with c8:
            st.markdown('<div class="sw-pass-label">Gate</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sw-pass-value" style="font-size:16px;">{flight.gate or "-"}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        qr_bytes = generate_qr_bytes(boarding_pass_qr_payload(booking))
        st.image(qr_bytes, caption="Scan for verification", width=200)
        st.metric("Fare Paid", format_currency(booking.fare_paid))

        pdf_bytes = generate_ticket_pdf(booking)
        st.download_button(
            "\U0001F4C4 Download PDF Ticket",
            data=pdf_bytes,
            file_name=f"{booking.booking_reference}_ticket.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

    st.write("")
    if st.button("Make Another Booking"):
        _reset_booking()
        st.rerun()
