import streamlit as st
import pandas as pd

from database.connection import get_session
from models import Airport
from authentication.auth import require_login, is_admin


def render():
    require_login()
    st.markdown("### Airports")
    st.caption("Manage the airport network used for flight routing.")

    session = get_session()
    try:
        airports = session.query(Airport).order_by(Airport.city).all()
        df = pd.DataFrame([{
            "Code": a.code, "Name": a.name, "City": a.city, "Country": a.country,
        } for a in airports])
    finally:
        session.close()

    search_term = st.text_input("Search airports by city, code, or country")
    if search_term:
        term = search_term.lower()
        df = df[df.apply(lambda row: term in str(row).lower(), axis=1)]

    st.dataframe(df, use_container_width=True, height=420)

    if is_admin():
        st.markdown("#### Add Airport")
        with st.form("add_airport_form"):
            c1, c2 = st.columns(2)
            code = c1.text_input("IATA Code* (3 letters)", max_chars=3, placeholder="e.g. JFK")
            name = c2.text_input("Airport Name*", placeholder="e.g. John F. Kennedy International Airport")
            c3, c4 = st.columns(2)
            city = c3.text_input("City*")
            country = c4.text_input("Country*")

            submitted = st.form_submit_button("Add Airport", type="primary")
            if submitted:
                if not code or not name or not city or not country:
                    st.error("All fields are required.")
                elif len(code) != 3:
                    st.error("IATA code must be exactly 3 letters.")
                else:
                    session = get_session()
                    try:
                        session.add(Airport(code=code.upper(), name=name, city=city, country=country))
                        session.commit()
                        st.success(f"Airport '{code.upper()}' added.")
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        st.error(f"Could not add airport (code may already exist): {e}")
                    finally:
                        session.close()
