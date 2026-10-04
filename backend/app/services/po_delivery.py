import os
import uuid
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.extensions import db
from app.models import PurchaseOrder
import logging

logger = logging.getLogger(__name__)

PDF_DIR = os.path.join(os.path.dirname(__file__), '../../data/po_pdfs')
os.makedirs(PDF_DIR, exist_ok=True)

def generate_po_pdf(po_id):
    po = PurchaseOrder.query.get(po_id)
    if not po:
        raise ValueError(f"PurchaseOrder {po_id} not found")
        
    pdf_path = os.path.join(PDF_DIR, f"PO_{po.id}_{int(time.time())}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    elements.append(Paragraph(f"<b>PURCHASE ORDER #{po.id}</b>", styles['Title']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Paragraph(f"Supplier: {po.supplier.name}", styles['Normal']))
    elements.append(Paragraph(f"Email: {po.supplier.email}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table Data
    data = [["SKU", "Product", "Qty", "Unit Price", "Total"]]
    for item in po.items:
        data.append([
            item.product.sku,
            item.product.name,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.quantity * item.unit_price:.2f}"
        ])
        
    data.append(["", "", "", "Total:", f"${po.total_amount:.2f}"])
    
    t = Table(data, colWidths=[80, 200, 60, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F7B5F')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    return pdf_path

def send_po_email(po_id):
    """
    Mock sending email with PDF attachment.
    Implements idempotency.
    """
    po = PurchaseOrder.query.get(po_id)
    if not po:
         return False
         
    if po.status in ['sent', 'partial', 'fulfilled']:
        logger.warning(f"PO {po_id} is already in state {po.status}. Skipping send to prevent duplicates.")
        return True
        
    if not po.idempotency_key:
        po.idempotency_key = str(uuid.uuid4())
        db.session.commit()
        
    logger.info(f"Generating PDF for PO {po_id}...")
    pdf_path = generate_po_pdf(po_id)
    
    logger.info(f"Mocking email dispatch to {po.supplier.email} with attachment {pdf_path} (Key: {po.idempotency_key})")
    
    # Simulate API call delay
    time.sleep(1)
    
    # Update state
    po.status = 'sent'
    po.sent_at = datetime.utcnow()
    db.session.commit()
    logger.info(f"PO {po_id} successfully marked as sent.")
    
    return True
