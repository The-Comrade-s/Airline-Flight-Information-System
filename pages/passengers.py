import streamlit as st
from datetime import date

from database.queries import (
    search_passengers, create_passenger, update_passenger, delete_passenger,
    get_passenger_by_id
)
from utils.helpers import format_date, paginate
from authentication.auth import is_admin, require_login


def render():
    require_login()
    st.markdown("### Passenger Management")
    st.caption("Register, search, and manage passenger records.")

    tabs = st.tabs(["View & Search", "Register New Passenger"]) if is_admin() else [st.container()]
    tab_list = tabs[0]
    tab_add = tabs[1] if is_admin() else None

    with tab_list:
        search_term = st.text_input("Search by name, passport number, email, or phone")
        passengers = search_passengers(search_term)
        st.write(f"**{len(passengers)} passenger(s) found**")

        if "passenger_page" not in st.session_state:
            st.session_state["passenger_page"] = 1

        page_items, total_pages = paginate(passengers, st.session_state["passenger_page"], page_size=12)

        for p in page_items:
            cols = st.columns([2, 1, 1.3, 1.3, 2, 1.6, 1] if is_admin() else [2, 1, 1.3, 1.3, 2, 1.6])
            cols[0].write(f"**{p.full_name}**")
            cols[1].write(p.gender or "-")
            cols[2].write(format_date(p.date_of_birth))
            cols[3].write(p.nationality or "-")
            cols[4].write(p.passport_number)
            cols[5].write(p.email or "-")
            if is_admin():
                if cols[6].button("Edit", key=f"edit_pax_{p.id}"):
                    st.session_state["editing_passenger_id"] = p.id
            st.divider()

        pc1, pc2, pc3 = st.columns([1, 2, 1])
        if pc1.button("\u2190 Previous", disabled=st.session_state["passenger_page"] <= 1, key="pax_prev"):
            st.session_state["passenger_page"] -= 1
            st.rerun()
        pc2.markdown(f"<div style='text-align:center;'>Page {st.session_state['passenger_page']} of {total_pages}</div>", unsafe_allow_html=True)
        if pc3.button("Next \u2192", disabled=st.session_state["passenger_page"] >= total_pages, key="pax_next"):
            st.session_state["passenger_page"] += 1
            st.rerun()

        if is_admin() and st.session_state.get("editing_passenger_id"):
            _render_edit_panel(st.session_state["editing_passenger_id"])

    if is_admin() and tab_add is not None:
        with tab_add:
            _render_add_form()


def _render_add_form():
    st.markdown("#### Register New Passenger")
    with st.form("add_passenger_form"):
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

        submitted = st.form_submit_button("Register Passenger", type="primary")
        if submitted:
            if not full_name or not passport_number:
                st.error("Full name and passport number are required.")
            else:
                create_passenger({
                    "full_name": full_name,
                    "gender": gender,
                    "date_of_birth": dob,
                    "nationality": nationality,
                    "passport_number": passport_number,
                    "phone_number": phone,
                    "email": email,
                })
                st.success(f"Passenger '{full_name}' registered successfully.")
                st.rerun()


def _render_edit_panel(passenger_id):
    passenger = get_passenger_by_id(passenger_id)
    if not passenger:
        st.session_state["editing_passenger_id"] = None
        return

    st.markdown("---")
    st.markdown(f"#### Edit Passenger — {passenger.full_name}")
    with st.form(f"edit_passenger_{passenger_id}"):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("Full Name", value=passenger.full_name)
        gender = c2.selectbox("Gender", ["Male", "Female", "Other"],
                               index=["Male", "Female", "Other"].index(passenger.gender) if passenger.gender in ["Male", "Female", "Other"] else 0)

        c3, c4 = st.columns(2)
        dob = c3.date_input("Date of Birth", value=passenger.date_of_birth or date(1990, 1, 1))
        nationality = c4.text_input("Nationality", value=passenger.nationality or "")

        c5, c6 = st.columns(2)
        passport_number = c5.text_input("Passport Number", value=passenger.passport_number)
        phone = c6.text_input("Phone Number", value=passenger.phone_number or "")

        email = st.text_input("Email Address", value=passenger.email or "")

        col_save, col_delete, col_cancel = st.columns(3)
        save = col_save.form_submit_button("Save Changes", type="primary")
        delete = col_delete.form_submit_button("Delete Passenger")
        cancel = col_cancel.form_submit_button("Cancel")

        if save:
            update_passenger(passenger_id, {
                "full_name": full_name, "gender": gender, "date_of_birth": dob,
                "nationality": nationality, "passport_number": passport_number,
                "phone_number": phone, "email": email,
            })
            st.success("Passenger updated successfully.")
            st.session_state["editing_passenger_id"] = None
            st.rerun()

        if delete:
            delete_passenger(passenger_id)
            st.success("Passenger deleted.")
            st.session_state["editing_passenger_id"] = None
            st.rerun()

        if cancel:
            st.session_state["editing_passenger_id"] = None
            st.rerun()
