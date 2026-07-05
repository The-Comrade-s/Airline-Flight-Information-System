"""PDF generation for boarding passes/tickets and reports, using ReportLab."""

import io
from reportlab.lib.pagesizes import A5, A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from utils.qr_utils import generate_qr_bytes, boarding_pass_qr_payload
from utils.helpers import format_date, format_time, format_currency

NAVY = colors.HexColor("#0A1F44")
ROYAL = colors.HexColor("#1E4FD9")
LIGHT_BG = colors.HexColor("#F7F9FC")
WHITE = colors.white


def generate_ticket_pdf(booking) -> bytes:
    """Generate a printable PDF boarding pass / ticket for a booking."""
    flight = booking.flight
    passenger = booking.passenger

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A5,
        topMargin=14 * mm, bottomMargin=14 * mm,
        leftMargin=12 * mm, rightMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TicketTitle", parent=styles["Title"], textColor=NAVY, fontSize=20, spaceAfter=2
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"], textColor=colors.HexColor("#64748B"), fontSize=8
    )
    value_style = ParagraphStyle(
        "Value", parent=styles["Normal"], textColor=NAVY, fontSize=13, fontName="Helvetica-Bold"
    )

    elements = []
    elements.append(Paragraph("SkyWings", title_style))
    elements.append(Paragraph("Electronic Boarding Pass", styles["Normal"]))
    elements.append(Spacer(1, 10))

    qr_bytes = generate_qr_bytes(boarding_pass_qr_payload(booking))
    qr_img = Image(io.BytesIO(qr_bytes), width=28 * mm, height=28 * mm)

    info_table_data = [
        [Paragraph("PASSENGER", label_style), Paragraph("FLIGHT", label_style)],
        [Paragraph(passenger.full_name, value_style), Paragraph(flight.flight_number, value_style)],
        [Paragraph("FROM", label_style), Paragraph("TO", label_style)],
        [Paragraph(flight.departure_airport.label, value_style),
         Paragraph(flight.destination_airport.label, value_style)],
        [Paragraph("DATE", label_style), Paragraph("BOARDING TIME", label_style)],
        [Paragraph(format_date(flight.departure_date), value_style),
         Paragraph(format_time(flight.departure_time), value_style)],
        [Paragraph("SEAT", label_style), Paragraph("GATE / TERMINAL", label_style)],
        [Paragraph(booking.seat_number, value_style),
         Paragraph(f"{flight.gate or '-'} / T{flight.terminal or '-'}", value_style)],
    ]
    info_table = Table(info_table_data, colWidths=[55 * mm, 55 * mm])
    info_table.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))

    header_table = Table([[info_table, qr_img]], colWidths=[112 * mm, 30 * mm])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    footer_data = [
        ["Booking Reference", booking.booking_reference],
        ["Airline", flight.airline],
        ["Fare Paid", format_currency(booking.fare_paid)],
        ["Status", booking.status],
    ]
    footer_table = Table(footer_data, colWidths=[70 * mm, 72 * mm])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748B")),
        ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 14))
    elements.append(Paragraph(
        "Please arrive at the gate at least 45 minutes before boarding time. "
        "Have this pass and a valid ID ready for verification.",
        styles["Normal"],
    ))

    doc.build(elements)
    return buffer.getvalue()


def _styled_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def generate_report_pdf(title: str, headers: list, rows: list, subtitle: str = "") -> bytes:
    """Generate a generic tabular report PDF (used for Flights, Passengers, Bookings, Revenue reports)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=16 * mm, bottomMargin=16 * mm, leftMargin=14 * mm, rightMargin=14 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], textColor=NAVY, fontSize=20)
    subtitle_style = ParagraphStyle("ReportSubtitle", parent=styles["Normal"], textColor=colors.HexColor("#64748B"))

    elements = [Paragraph("SkyWings", subtitle_style), Paragraph(title, title_style)]
    if subtitle:
        elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 14))

    table_data = [headers] + rows
    elements.append(_styled_table(table_data))
    doc.build(elements)
    return buffer.getvalue()
