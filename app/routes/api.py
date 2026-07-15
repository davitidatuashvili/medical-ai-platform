import json
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .. import db
from ..models import Analysis
from .main import registry

api_bp = Blueprint("api", __name__)
ALLOWED = {"png", "jpg", "jpeg", "webp"}

def valid_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED

@api_bp.get("/departments")
def departments():
    return jsonify({"success": True, "departments": registry().public_departments()})

@api_bp.post("/predict/<department>")
@login_required
def predict(department):
    if not registry().has(department):
        return jsonify({"success": False, "error": "უცნობი განყოფილება."}), 404

    image = request.files.get("image")
    if not image or not image.filename:
        return jsonify({"success": False, "error": "სურათი არ არის ატვირთული."}), 400
    if not valid_file(image.filename):
        return jsonify({"success": False, "error": "დაშვებულია JPG, PNG და WEBP."}), 400

    ext = secure_filename(image.filename).rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    image.save(path)

    try:
        result = registry().predict(department, path)
        analysis = Analysis(
            department=department,
            prediction=result["display_prediction"],
            confidence=result["confidence"],
            probabilities_json=json.dumps(result["all_predictions"], ensure_ascii=False),
            image_filename=filename,
            model_name=result["model_name"],
            user_id=current_user.id,
        )
        db.session.add(analysis)
        db.session.commit()

        result.update({
            "success": True,
            "analysis_id": analysis.id,
            "image_url": f"/static/uploads/{filename}",
            "warning": "სასწავლო/კვლევითი შედეგია და არ წარმოადგენს ექიმის დიაგნოზს.",
        })
        return jsonify(result)
    except Exception as exc:
        path.unlink(missing_ok=True)
        return jsonify({"success": False, "error": f"პროგნოზის შეცდომა: {exc}"}), 500
