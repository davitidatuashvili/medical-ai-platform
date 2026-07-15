import json
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from sqlalchemy import select, func
from .. import db
from ..models import Analysis
from ..services.registry import PredictorRegistry

main_bp = Blueprint("main", __name__)
_registry = None

def registry():
    global _registry
    if _registry is None:
        _registry = PredictorRegistry(current_app.root_path)
    return _registry

@main_bp.route("/")
def landing():
    if current_user.is_authenticated:
        return dashboard()
    return render_template("landing.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    departments = registry().public_departments()
    total = db.session.scalar(select(func.count(Analysis.id)).where(Analysis.user_id == current_user.id)) or 0
    recent = db.session.scalars(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
    ).all()
    return render_template("dashboard.html", departments=departments, total=total, recent=recent)

@main_bp.route("/history")
@login_required
def history():
    analyses = db.session.scalars(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
    ).all()
    return render_template("history.html", analyses=analyses)
