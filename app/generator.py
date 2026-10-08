from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    certificate_date: str
) -> str:
    """
    Generate one certificate PDF and return its file path.
    """

    file_path = OUTPUT_DIR / f"certificate_{certificate_id}.pdf"

    width, height = landscape(A4)

    pdf = canvas.Canvas(str(file_path), pagesize=(width, height))

    # Border
    pdf.setLineWidth(3)
    pdf.rect(
        30,
        30,
        width - 60,
        height - 60
    )

    # Title
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        width / 2,
        height - 120,
        "CERTIFICATE OF COMPLETION"
    )

    # Subtitle
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2,
        height - 170,
        "This certificate is proudly presented to"
    )

    # Recipient
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        width / 2,
        height - 230,
        recipient_name
    )

    # Event
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2,
        height - 280,
        "for successfully completing"
    )

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(
        width / 2,
        height - 320,
        event_name
    )

    # Date
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        100,
        f"Date: {certificate_date}"
    )

    # Certificate ID
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        width / 2,
        75,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return str(file_path)