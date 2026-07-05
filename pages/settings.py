import streamlit as st
from authentication.auth import require_login, current_user


def render():
    require_login()
    user = current_user()
    st.markdown("### Settings")
    st.caption("Manage your preferences and account information.")

    st.markdown("#### Appearance")
    dark_mode = st.toggle("Dark Mode", value=st.session_state.get("dark_mode", False))
    if dark_mode != st.session_state.get("dark_mode", False):
        st.session_state["dark_mode"] = dark_mode
        st.rerun()

    st.caption(
        "Dark mode adjusts SkyWings to a low-glare theme for extended dashboard use. "
        "Tip: your operating system or browser's own dark mode also works well with this app."
    )

    st.markdown("---")
    st.markdown("#### Account")
    c1, c2 = st.columns(2)
    c1.text_input("Full Name", value=user.get("full_name", ""), disabled=True)
    c2.text_input("Username", value=user.get("username", ""), disabled=True)
    c1.text_input("Email", value=user.get("email", ""), disabled=True)
    c2.text_input("Role", value=user.get("role", ""), disabled=True)

    st.markdown("---")
    st.markdown("#### Notifications")
    st.checkbox("Email me a daily flight summary", value=True)
    st.checkbox("Notify me when a flight is delayed or cancelled", value=True)
    st.checkbox("Notify me of new bookings", value=False)

    st.markdown("---")
    st.markdown("#### About")
    st.write(
        "**SkyWings Airline Flight Information System** — a professional flight management "
        "platform covering flight scheduling, passenger records, bookings, and reporting."
    )
