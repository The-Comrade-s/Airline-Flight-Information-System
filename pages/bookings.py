import streamlit as st

from database.queries import get_all_bookings, update_booking_status
from models.booking import BOOKING_STATUSES
from utils.styling import status_badge_html
from utils.helpers import format_currency, format_date, paginate
from utils.pdf_utils import generate_ticket_pdf
from authentication.auth import require_login, is_admin


def render():
    require_login()
    st.markdown("### Bookings")
    st.caption("View and manage all passenger bookings.")

    bookings = get_all_bookings()

    c1, c2 = st.columns(2)
    status_filter = c1.selectbox("Filter by status", ["All"] + BOOKING_STATUSES)
    search_term = c2.text_input("Search by reference, passenger name, or flight number")

    filtered = bookings
    if status_filter != "All":
        filtered = [b for b in filtered if b.status == status_filter]
    if search_term:
        term = search_term.lower()
        filtered = [
            b for b in filtered
            if term in b.booking_reference.lower()
            or term in b.passenger.full_name.lower()
            or term in b.flight.flight_number.lower()
        ]

    st.write(f"**{len(filtered)} booking(s) found**")

    if "booking_page" not in st.session_state:
        st.session_state["booking_page"] = 1

    page_items, total_pages = paginate(filtered, st.session_state["booking_page"], page_size=10)

    for b in page_items:
        with st.container():
            cols = st.columns([1.3, 2, 1.3, 1, 1.2, 1.3, 1.2])
            cols[0].markdown(f"**{b.booking_reference}**")
            cols[1].write(b.passenger.full_name)
            cols[2].write(b.flight.flight_number)
            cols[3].write(b.seat_number)
            cols[4].write(format_currency(b.fare_paid))
            cols[5].markdown(status_badge_html(b.status), unsafe_allow_html=True)

            with cols[6]:
                pdf_bytes = generate_ticket_pdf(b)
                st.download_button(
                    "Ticket", data=pdf_bytes,
                    file_name=f"{b.booking_reference}.pdf",
                    mime="application/pdf",
                    key=f"dl_{b.id}",
                )
            if is_admin() and b.status != "Cancelled":
                if st.button(f"Manage {b.booking_reference}", key=f"manage_booking_{b.id}"):
                    st.session_state["managing_booking_id"] = b.id
            st.divider()

    pc1, pc2, pc3 = st.columns([1, 2, 1])
    if pc1.button("\u2190 Previous", disabled=st.session_state["booking_page"] <= 1, key="bk_prev"):
        st.session_state["booking_page"] -= 1
        st.rerun()
    pc2.markdown(f"<div style='text-align:center;'>Page {st.session_state['booking_page']} of {total_pages}</div>", unsafe_allow_html=True)
    if pc3.button("Next \u2192", disabled=st.session_state["booking_page"] >= total_pages, key="bk_next"):
        st.session_state["booking_page"] += 1
        st.rerun()

    if is_admin() and st.session_state.get("managing_booking_id"):
        _render_status_panel(st.session_state["managing_booking_id"])


def _render_status_panel(booking_id):
    from database.queries import get_booking_by_id
    booking = get_booking_by_id(booking_id)
    if not booking:
        st.session_state["managing_booking_id"] = None
        return

    st.markdown("---")
    st.markdown(f"#### Update Booking — {booking.booking_reference}")
    with st.form(f"update_booking_{booking_id}"):
        new_status = st.selectbox("Status", BOOKING_STATUSES, index=BOOKING_STATUSES.index(booking.status))
        col_save, col_cancel = st.columns(2)
        save = col_save.form_submit_button("Update Status", type="primary")
        cancel = col_cancel.form_submit_button("Close")

        if save:
            update_booking_status(booking_id, new_status)
            st.success("Booking status updated.")
            st.session_state["managing_booking_id"] = None
            st.rerun()
        if cancel:
            st.session_state["managing_booking_id"] = None
            st.rerun()
