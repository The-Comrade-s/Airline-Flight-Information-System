"""
Central visual design system for SkyWings.

Palette:
  Navy (primary dark)     #0A1F44
  Royal blue (action)     #1E4FD9
  Sky blue (accent)       #3B82F6
  Off-white (background)  #F7F9FC
  Surface (cards)         #FFFFFF
  Success                 #10B981
  Warning                 #F59E0B
  Danger                  #EF4444

Type:
  Display / headings : Poppins
  Body / data         : Inter
"""

import streamlit as st

PALETTE = {
    "navy": "#0A1F44",
    "royal": "#1E4FD9",
    "sky": "#3B82F6",
    "bg": "#F7F9FC",
    "surface": "#FFFFFF",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "muted": "#64748B",
    "border": "#E2E8F0",
}

STATUS_COLORS = {
    "Scheduled": "#3B82F6",
    "Boarding": "#10B981",
    "Delayed": "#F59E0B",
    "Cancelled": "#EF4444",
    "Landed": "#64748B",
    "Confirmed": "#10B981",
    "Checked-in": "#3B82F6",
    "Boarded": "#1E4FD9",
    "Completed": "#64748B",
}


def inject_global_css(dark_mode: bool = False):
    bg = "#0F172A" if dark_mode else PALETTE["bg"]
    surface = "#1E293B" if dark_mode else PALETTE["surface"]
    text = "#F1F5F9" if dark_mode else PALETTE["navy"]
    border = "#334155" if dark_mode else PALETTE["border"]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 17px;
            color: {text};
        }}

        h1, h2, h3, h4, .sw-display {{
            font-family: 'Poppins', 'Segoe UI', sans-serif;
            letter-spacing: -0.01em;
            color: {text};
        }}

        .stApp {{
            background-color: {bg};
        }}

        .sw-card {{ background: {surface}; border-color: {border}; }}
        .sw-stat-value, .sw-section-title {{ color: {text}; }}

        section[data-testid="stSidebar"] {{
            background-color: {PALETTE['navy']};
        }}
        section[data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stButton>button {{
            background-color: transparent;
            color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.15);
            text-align: left;
            font-size: 16px;
            font-weight: 500;
            padding: 0.6rem 1rem;
            border-radius: 10px;
            width: 100%;
            margin-bottom: 4px;
            transition: background-color 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton>button:hover {{
            background-color: {PALETTE['royal']};
            border-color: {PALETTE['royal']};
        }}

        /* Primary buttons */
        .stButton>button[kind="primary"], button[kind="primary"] {{
            background-color: {PALETTE['royal']};
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 600;
            font-size: 16px;
            padding: 0.6rem 1.4rem;
        }}
        .stButton>button[kind="primary"]:hover {{
            background-color: {PALETTE['navy']};
        }}

        /* Stat / info cards */
        .sw-card {{
            background: {PALETTE['surface']};
            border-radius: 14px;
            padding: 1.4rem 1.5rem;
            border: 1px solid {PALETTE['border']};
            box-shadow: 0 2px 10px rgba(10, 31, 68, 0.05);
        }}
        .sw-stat-label {{
            font-size: 15px;
            color: {PALETTE['muted']};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 6px;
        }}
        .sw-stat-value {{
            font-family: 'Poppins', sans-serif;
            font-size: 32px;
            font-weight: 700;
            color: {PALETTE['navy']};
        }}
        .sw-stat-delta-up {{
            color: {PALETTE['success']};
            font-weight: 600;
            font-size: 14px;
        }}
        .sw-stat-delta-down {{
            color: {PALETTE['danger']};
            font-weight: 600;
            font-size: 14px;
        }}

        /* Status badges */
        .sw-badge {{
            display: inline-block;
            padding: 4px 14px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 600;
            color: white;
        }}

        /* Boarding pass */
        .sw-pass {{
            background: linear-gradient(135deg, {PALETTE['navy']} 0%, {PALETTE['royal']} 100%);
            border-radius: 18px;
            padding: 2rem;
            color: white;
            position: relative;
        }}
        .sw-pass-stub {{
            border-top: 2px dashed rgba(255,255,255,0.4);
            margin-top: 1.2rem;
            padding-top: 1.2rem;
        }}
        .sw-pass-label {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(255,255,255,0.7);
            margin-bottom: 2px;
        }}
        .sw-pass-value {{
            font-family: 'Poppins', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: white;
        }}

        /* Login page */
        .sw-login-panel {{
            background: rgba(10, 31, 68, 0.72);
            border-radius: 20px;
            padding: 2.6rem 2.4rem;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255,255,255,0.15);
        }}
        .sw-login-title {{
            color: white;
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 30px;
        }}
        .sw-login-subtitle {{
            color: rgba(255,255,255,0.75);
            font-size: 16px;
            margin-bottom: 1.4rem;
        }}

        /* Seat map */
        .seat-available {{
            background-color: #E8F0FE; border: 2px solid {PALETTE['sky']};
            border-radius: 8px; text-align: center; padding: 10px 0;
            font-weight: 600; color: {PALETTE['navy']};
        }}
        .seat-selected {{
            background-color: {PALETTE['royal']}; border: 2px solid {PALETTE['navy']};
            border-radius: 8px; text-align: center; padding: 10px 0;
            font-weight: 700; color: white;
        }}
        .seat-occupied {{
            background-color: #E2E8F0; border: 2px solid #CBD5E1;
            border-radius: 8px; text-align: center; padding: 10px 0;
            font-weight: 600; color: #94A3B8;
        }}
        .seat-premium {{
            background-color: #FFF7E6; border: 2px solid {PALETTE['warning']};
            border-radius: 8px; text-align: center; padding: 10px 0;
            font-weight: 600; color: #92400E;
        }}

        /* Section dividers */
        .sw-section-title {{
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 22px;
            color: {PALETTE['navy']};
            margin-top: 0.5rem;
            margin-bottom: 0.8rem;
            border-left: 5px solid {PALETTE['royal']};
            padding-left: 12px;
        }}

        /* Tables */
        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
        }}

        /* Larger, high-contrast form labels for accessibility */
        label, .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {{
            font-size: 16px !important;
            font-weight: 600 !important;
            color: {PALETTE['navy']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_badge_html(status: str) -> str:
    color = STATUS_COLORS.get(status, "#64748B")
    return f'<span class="sw-badge" style="background-color:{color};">{status}</span>'


def stat_card(label: str, value: str, delta: str = None, delta_positive: bool = True) -> str:
    delta_html = ""
    if delta:
        cls = "sw-stat-delta-up" if delta_positive else "sw-stat-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    return f"""
    <div class="sw-card">
        <div class="sw-stat-label">{label}</div>
        <div class="sw-stat-value">{value}</div>
        {delta_html}
    </div>
    """
