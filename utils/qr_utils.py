"""QR code generation for boarding passes and ticket verification."""

import io
import qrcode
from qrcode.constants import ERROR_CORRECT_M


def generate_qr_bytes(data: str) -> bytes:
    """Generate a QR code PNG (as bytes) encoding the given data string."""
    qr = qrcode.QRCode(
        version=2,
        error_correction=ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A1F44", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def boarding_pass_qr_payload(booking) -> str:
    """Build the text payload encoded into a boarding pass QR code."""
    flight = booking.flight
    passenger = booking.passenger
    return (
        f"SKYWINGS-BOARDING-PASS\n"
        f"Ref:{booking.booking_reference}\n"
        f"Passenger:{passenger.full_name}\n"
        f"Flight:{flight.flight_number}\n"
        f"Seat:{booking.seat_number}\n"
        f"Date:{flight.departure_date}\n"
        f"Status:{booking.status}"
    )
