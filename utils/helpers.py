"""General-purpose formatting and helper functions used across pages."""

import random
import string
from datetime import datetime


def format_currency(value: float) -> str:
    try:
        return f"${value:,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def format_date(d) -> str:
    if not d:
        return "-"
    return d.strftime("%d %b %Y")


def format_time(t) -> str:
    if not t:
        return "-"
    return t.strftime("%I:%M %p")


def generate_booking_reference() -> str:
    return "SW" + "".join(random.choices(string.digits, k=7))


def duration_between(dep_date, dep_time, arr_time) -> str:
    """Return a human-readable flight duration string (handles overnight flights)."""
    dep_dt = datetime.combine(dep_date, dep_time)
    arr_dt = datetime.combine(dep_date, arr_time)
    if arr_dt <= dep_dt:
        arr_dt = arr_dt.replace(day=arr_dt.day)
        from datetime import timedelta
        arr_dt += timedelta(days=1)
    delta = arr_dt - dep_dt
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{hours}h {minutes:02d}m"


def paginate(items: list, page: int, page_size: int = 10):
    """Return (page_items, total_pages) for a given list, 1-indexed page."""
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total_pages
