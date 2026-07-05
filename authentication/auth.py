"""
Authentication utilities: password hashing/verification, login,
and Streamlit session-state helpers for role-based access control.
"""

import bcrypt
import streamlit as st

from database.connection import get_session
from models import User


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def authenticate(username: str, password: str):
    """
    Attempt to log in. Returns a dict with user info on success, else None.
    """
    session = get_session()
    try:
        user = session.query(User).filter(
            User.username == username.strip().lower(), User.is_active == 1
        ).first()
        if user and verify_password(password, user.password_hash):
            return {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "email": user.email,
            }
        return None
    finally:
        session.close()


def login_user(user_info: dict):
    """Store authenticated user info in session state."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = user_info


def logout_user():
    """Clear session state on logout."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def current_user() -> dict:
    return st.session_state.get("user", {}) or {}


def current_role() -> str:
    return current_user().get("role", "")


def is_admin() -> bool:
    return current_role() == "Administrator"


def require_login():
    """Call at the top of a protected page; halts rendering if not logged in."""
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.stop()


def require_admin():
    """Call at the top of admin-only pages/actions."""
    require_login()
    if not is_admin():
        st.error("This section is restricted to Administrators only.")
        st.stop()
