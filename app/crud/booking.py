import os
from datetime import date
from tempfile import NamedTemporaryFile
from fastapi import BackgroundTasks, HTTPException
from fastapi_mail import FastMail, MessageSchema
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from app.core.config import conf
from sqlalchemy.orm import Session
from app.crud.generic_crud import get_record_by_id
from app.models import Bookings
from app.models.room_type import RoomTypeWithSizes
from app.models.rooms import Rooms 


async def generate_booking_invoice(db: Session, booking_instance):
    
    if not booking_instance:
        raise ValueError("Booking record not found")
    
    folder_path = r"D:\PROJECT\Hotel_Booking_System\app\static\invoices"
    os.makedirs(folder_path, exist_ok=True)

    filename = f"user_{booking_instance.user_id}_booking_{booking_instance.id}_invoice.pdf"
    filepath = os.path.join(folder_path, filename)

    pdf = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"<b><font size=16>Booking Invoice - #{booking_instance.id}</font></b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    details_html = f"""
    <b>User name :</b> {booking_instance.user.first_name}<br/>
    <b>Email :</b> {booking_instance.user.email}<br/>
    <b>Room ID:</b> {booking_instance.room_id}<br/>
    <b>Check-in:</b> {booking_instance.check_in}<br/>
    <b>Check-out:</b> {booking_instance.check_out}<br/>
    <b>Status:</b> {booking_instance.booking_status.value}<br/>
    <b>Payment Status:</b> {booking_instance.payment_status.value}<br/>
    <b>Created:</b> {booking_instance.created_at.strftime('%Y-%m-%d %H:%M')}<br/>
    """
    elements.append(Paragraph(details_html, styles["Normal"]))
    elements.append(Spacer(1, 12))

    days = (booking_instance.check_out - booking_instance.check_in).days
    price_per_night = booking_instance.room.room_type.base_price
    total_amount = booking_instance.total_amount
    
    data = [
        ["Description", "Stay", "Unit Price", "Amount"],
        [f"{booking_instance.room.room_type.room_name}", f"{days} nights", f"Rs.{price_per_night}", f"Rs.{total_amount}"],
        ["Total", "", "", f"Rs.{total_amount}"]
    ]

    table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    footer = Paragraph(
        "<i>Thank you for booking with us!</i><br/>"
        "<i>For any queries, contact: support@hotelbooking.com</i>",
        styles["Normal"]
    )
    elements.append(footer)

    pdf.build(elements)

    return filepath


async def send_email_with_pdf(
    background_tasks: BackgroundTasks,
    to_email: str,
    subject: str,
    message: str,
    pdf_path: str
):
    try:
        email_message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=message or "Please find your booking invoice attached.",
            subtype="plain",
            attachments=[pdf_path],
        )

        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, email_message)

        background_tasks.add_task(os.remove, pdf_path)

        return {"status": "Invoice PDF sent successfully!"}

    except Exception as e:
        print(f"Error sending email with PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

 
        
        