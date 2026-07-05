import streamlit as st
import pandas as pd

from database.connection import get_session
from models import Aircraft
from authentication.auth import require_login, is_admin


def render():
    require_login()
    st.markdown("### Aircraft Fleet")
    st.caption("Manage the aircraft types used across your flight schedule.")

    session = get_session()
    try:
        aircraft_list = session.query(Aircraft).order_by(Aircraft.model).all()
        df = pd.DataFrame([{
            "Model": a.model, "Manufacturer": a.manufacturer,
            "Total Seats": a.total_seats, "Seat Layout": a.seat_layout,
        } for a in aircraft_list])
    finally:
        session.close()

    st.dataframe(df, use_container_width=True, height=380)

    if is_admin():
        st.markdown("#### Add Aircraft Type")
        with st.form("add_aircraft_form"):
            c1, c2 = st.columns(2)
            model = c1.text_input("Model*", placeholder="e.g. Boeing 787-9 Dreamliner")
            manufacturer = c2.text_input("Manufacturer*", placeholder="e.g. Boeing")
            c3, c4 = st.columns(2)
            total_seats = c3.number_input("Total Seats*", min_value=1, value=180)
            seat_layout = c4.text_input("Seat Layout", placeholder="e.g. 3-3", value="3-3")

            submitted = st.form_submit_button("Add Aircraft", type="primary")
            if submitted:
                if not model or not manufacturer:
                    st.error("Model and manufacturer are required.")
                else:
                    session = get_session()
                    try:
                        session.add(Aircraft(
                            model=model, manufacturer=manufacturer,
                            total_seats=int(total_seats), seat_layout=seat_layout,
                        ))
                        session.commit()
                        st.success(f"Aircraft '{model}' added.")
                        st.rerun()
                    finally:
                        session.close()
