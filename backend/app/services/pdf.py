from io import BytesIO

from ..config import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_invoice_pdf(data: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(settings.company_name, styles["Heading2"]))
    story.append(Paragraph(f"Invoice {data.get('number', '')}", styles["Title"]))
    story.append(Spacer(1, 12))

    client = data.get("client", {})
    story.append(Paragraph(f"Client: {client.get('name', '')}", styles["Normal"]))
    story.append(Paragraph(f"Email: {client.get('email', '')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    rows = [["Description", "Qty", "Unit Price", "Amount"]]
    for item in data.get("items", []):
        rows.append(
            [
                item.get("description", ""),
                str(item.get("quantity", 0)),
                f"{item.get('unit_price', 0):.2f}",
                f"{item.get('amount', 0):.2f}",
            ]
        )
    rows.append(["", "", "Subtotal", f"{data.get('subtotal', 0):.2f}"])
    rows.append(["", "", "Tax", f"{data.get('tax', 0):.2f}"])
    rows.append(["", "", "Total", f"{data.get('total', 0):.2f}"])

    table = Table(rows, colWidths=[260, 60, 100, 100])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    story.append(table)

    story.append(Spacer(1, 12))
    story.append(Paragraph(settings.invoice_terms, styles["Italic"]))

    if data.get("payment_link"):
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Pay here: {data['payment_link']}", styles["Normal"]))
        try:
            import qrcode

            qr = qrcode.make(data["payment_link"])
            buf_qr = BytesIO()
            qr.save(buf_qr, format="PNG")
            buf_qr.seek(0)
            story.append(Spacer(1, 6))
            story.append(Image(ImageReader(buf_qr), width=120, height=120))
        except Exception:
            pass

    doc.build(story)
    return buf.getvalue()