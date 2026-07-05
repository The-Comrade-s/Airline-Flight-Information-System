"""Reusable Plotly chart builders, styled consistently to the SkyWings palette."""

import plotly.graph_objects as go
from utils.styling import PALETTE, STATUS_COLORS

CHART_FONT = dict(family="Inter, Segoe UI, sans-serif", size=14, color=PALETTE["navy"])


def bookings_line_chart(dates, counts, title="Bookings Trend"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=counts, mode="lines+markers",
        line=dict(color=PALETTE["royal"], width=3, shape="spline"),
        marker=dict(size=7, color=PALETTE["royal"]),
        fill="tozeroy", fillcolor="rgba(30, 79, 217, 0.08)",
        name="Bookings",
    ))
    fig.update_layout(
        title=title, font=CHART_FONT, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=PALETTE["border"]),
        height=340,
    )
    return fig


def flight_status_pie(status_counts: dict, title="Flight Status Overview"):
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = [STATUS_COLORS.get(s, "#94A3B8") for s in labels]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="label+percent",
    )])
    total = sum(values)
    fig.update_layout(
        title=title, font=CHART_FONT, showlegend=True,
        margin=dict(l=10, r=10, t=50, b=10), height=340,
        annotations=[dict(text=f"{total}<br>Total", x=0.5, y=0.5, font_size=18, showarrow=False)],
    )
    return fig


def airline_performance_bar(airlines, values, title="Airline Performance"):
    fig = go.Figure(data=[go.Bar(
        x=airlines, y=values,
        marker=dict(color=PALETTE["sky"], line=dict(color=PALETTE["royal"], width=1)),
        text=values, textposition="outside",
    )])
    fig.update_layout(
        title=title, font=CHART_FONT, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=PALETTE["border"]),
        height=340,
    )
    return fig


def revenue_bar_chart(labels, values, title="Revenue Summary"):
    fig = go.Figure(data=[go.Bar(
        x=labels, y=values,
        marker=dict(color=PALETTE["navy"]),
        text=[f"${v:,.0f}" for v in values], textposition="outside",
    )])
    fig.update_layout(
        title=title, font=CHART_FONT, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=PALETTE["border"]),
        height=340,
    )
    return fig


def passenger_demographics_bar(labels, values, title="Passengers by Nationality"):
    fig = go.Figure(data=[go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=PALETTE["royal"]),
    )])
    fig.update_layout(
        title=title, font=CHART_FONT, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=True, gridcolor=PALETTE["border"]),
        yaxis=dict(showgrid=False),
        height=400,
    )
    return fig
