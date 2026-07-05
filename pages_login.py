"""
Login screen. Not placed in pages/ because Streamlit's multipage
auto-discovery would list it in the sidebar — it's rendered manually
from app.py before authentication succeeds.
"""

import streamlit as st
from authentication.auth import authenticate, login_user

AVIATION_BG_URL = "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2069&auto=format&fit=crop"


def render_login():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(10,31,68,0.55), rgba(10,31,68,0.75)),
                        url('{AVIATION_BG_URL}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sw-login-panel">', unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; font-size:44px;'>&#9992;&#65039;</div>",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sw-login-title" style="text-align:center;">SkyWings</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sw-login-subtitle" style="text-align:center;">'
            'Airline Flight Information System</div>',
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="e.g. admin")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user_info = authenticate(username, password)
                    if user_info:
                        login_user(user_info)
                        st.success(f"Welcome back, {user_info['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")

        st.markdown(
            "<div style='text-align:center; color:rgba(255,255,255,0.6); font-size:13px; margin-top:10px;'>"
            "Demo accounts — Admin: admin / Admin@123 &nbsp;|&nbsp; Staff: staff / Staff@123"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
