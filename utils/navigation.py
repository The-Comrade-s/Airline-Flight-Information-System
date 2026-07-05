"""Sidebar navigation, shared across all authenticated pages."""

import streamlit as st
from authentication.auth import current_user, logout_user, is_admin

NAV_ITEMS = [
    ("Dashboard", "\U0001F4CA"),
    ("Flights", "\u2708\uFE0F"),
    ("Book Flight", "\U0001F4DD"),
    ("Passengers", "\U0001F465"),
    ("Bookings", "\U0001F3AB"),
    ("Reports", "\U0001F4C8"),
    ("Aircraft", "\U0001F6E9\uFE0F"),
    ("Airports", "\U0001F3E2"),
    ("Staff", "\U0001F464"),
    ("Settings", "\u2699\uFE0F"),
]


def render_sidebar():
    user = current_user()

    with st.sidebar:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:10px;padding:6px 0 18px 0;'>"
            "<span style='font-size:28px;'>&#9992;&#65039;</span>"
            "<span style='font-size:22px;font-weight:700;font-family:Poppins,sans-serif;'>SkyWings</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        current_page = st.session_state.get("current_page", "Dashboard")

        for label, icon in NAV_ITEMS:
            if label in ("Staff",) and not is_admin():
                continue
            if label == current_page:
                st.markdown(
                    f"<div style='background-color:#1E4FD9; color:white; border-radius:10px; "
                    f"padding:0.6rem 1rem; font-weight:600; font-size:16px; margin-bottom:4px;'>"
                    f"{icon}&nbsp;&nbsp;{label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                    st.session_state["current_page"] = label
                    st.rerun()

        st.markdown("<div style='margin-top:20px; border-top:1px solid rgba(255,255,255,0.15); padding-top:14px;'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:15px; font-weight:600;'>{user.get('full_name', '')}</div>"
            f"<div style='font-size:13px; color:rgba(255,255,255,0.6);'>{user.get('role', '')}</div>",
            unsafe_allow_html=True,
        )
        if st.button("Log Out", use_container_width=True):
            logout_user()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state.get("current_page", "Dashboard")
