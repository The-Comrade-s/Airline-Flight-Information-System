import streamlit as st
import pandas as pd

from database.queries import get_all_users, create_user, update_user_status
from authentication.auth import require_admin, hash_password


def render():
    require_admin()
    st.markdown("### Staff Management")
    st.caption("Manage system users and their access roles.")

    users = get_all_users()
    df = pd.DataFrame([{
        "Full Name": u.full_name, "Username": u.username, "Email": u.email,
        "Role": u.role, "Status": "Active" if u.is_active else "Disabled",
    } for u in users])
    st.dataframe(df, use_container_width=True, height=320)

    st.markdown("#### Add Staff Account")
    with st.form("add_staff_form"):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("Full Name*")
        username = c2.text_input("Username*")
        c3, c4 = st.columns(2)
        email = c3.text_input("Email*")
        role = c4.selectbox("Role", ["Staff", "Administrator"])
        password = st.text_input("Temporary Password*", type="password")

        submitted = st.form_submit_button("Create Account", type="primary")
        if submitted:
            if not all([full_name, username, email, password]):
                st.error("All fields are required.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    create_user({
                        "full_name": full_name,
                        "username": username.strip().lower(),
                        "email": email,
                        "password_hash": hash_password(password),
                        "role": role,
                        "is_active": 1,
                    })
                    st.success(f"Account created for {full_name}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not create account (username/email may already exist): {e}")

    st.markdown("#### Enable / Disable Accounts")
    for u in users:
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"**{u.full_name}** ({u.username}) — {u.role}")
        c2.write("Active" if u.is_active else "Disabled")
        label = "Disable" if u.is_active else "Enable"
        if c3.button(label, key=f"toggle_{u.id}"):
            update_user_status(u.id, 0 if u.is_active else 1)
            st.rerun()
