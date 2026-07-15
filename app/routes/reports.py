import io, json
from flask import Blueprint, send_file, abort
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select
from .. import db
from ..models import Analysis

reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/report/<int:analysis_id>.pdf")
@login_required
def report(analysis_id):
    analysis = db.session.scalar(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    if not analysis:
        abort(404)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"Medical AI Report #{analysis.id}")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 60, "Medical AI Analysis Report")

    pdf.setFont("Helvetica", 11)
    lines = [
        f"Report ID: {analysis.id}",
        f"User: {current_user.name}",
        f"Department: {analysis.department}",
        f"Prediction: {analysis.prediction}",
        f"Confidence: {analysis.confidence:.2f}%",
        f"Model: {analysis.model_name}",
        f"Created: {analysis.created_at}",
    ]

    y = height - 100
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y - 10, "Probabilities")
    y -= 35

    pdf.setFont("Helvetica", 10)
    for item in json.loads(analysis.probabilities_json)[:10]:
        pdf.drawString(60, y, f"{item['display_label']}: {item['probability']}%")
        y -= 16
        if y < 80:
            pdf.showPage()
            y = height - 60

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(50, 45, "Educational/research use only. This is not a medical diagnosis.")
    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"medical_ai_report_{analysis.id}.pdf",
    )
