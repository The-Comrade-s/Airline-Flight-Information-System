import streamlit as st
from datetime import date

from database.queries import dashboard_stats, bookings_trend, get_all_flights
from utils.styling import stat_card, status_badge_html
from utils.charts import bookings_line_chart, flight_status_pie, airline_performance_bar
from utils.helpers import format_currency, format_date, format_time
from authentication.auth import current_user


def render():
    user = current_user()
    st.markdown(f"### Welcome back, {user.get('full_name', 'there')} \U0001F44B")
    st.caption("Here's what's happening across your network today.")

    stats = dashboard_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Total Flights", f"{stats['total_flights']:,}"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Active Flights", f"{stats['active_flights']:,}"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("Cancelled Flights", f"{stats['cancelled_flights']:,}"), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card("Total Passengers", f"{stats['total_passengers']:,}"), unsafe_allow_html=True)

    st.write("")
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(stat_card("Total Bookings", f"{stats['total_bookings']:,}"), unsafe_allow_html=True)
    with c6:
        st.markdown(stat_card("Available Seats", f"{stats['available_seats']:,}"), unsafe_allow_html=True)
    with c7:
        st.markdown(stat_card("Today's Flights", f"{stats['today_flights']:,}"), unsafe_allow_html=True)
    with c8:
        st.markdown(stat_card("Revenue", format_currency(stats["revenue"])), unsafe_allow_html=True)

    st.write("")
    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        dates, counts = bookings_trend(7)
        labels = [d.strftime("%a %d") for d in dates]
        fig = bookings_line_chart(labels, counts, title="Bookings Overview (Last 7 Days)")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig = flight_status_pie(stats["status_counts"], title="Flight Status Overview")
        st.plotly_chart(fig, use_container_width=True)

    if stats["airline_counts"]:
        fig = airline_performance_bar(
            list(stats["airline_counts"].keys()), list(stats["airline_counts"].values()),
            title="Airline Performance (Flights Operated)"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sw-section-title">Today\'s Flights</div>', unsafe_allow_html=True)
    all_flights = get_all_flights()
    todays = [f for f in all_flights if f.departure_date == date.today()]

    if not todays:
        st.info("No flights are scheduled to depart today.")
    else:
        for f in todays[:8]:
            cols = st.columns([1.2, 2, 2, 1.2, 1.3, 0.8])
            cols[0].write(f"**{f.flight_number}**")
            cols[1].write(f.departure_airport.label if f.departure_airport else "-")
            cols[2].write(f.destination_airport.label if f.destination_airport else "-")
            cols[3].write(format_time(f.departure_time))
            cols[4].markdown(status_badge_html(f.status), unsafe_allow_html=True)
            cols[5].write(f.gate or "-")
