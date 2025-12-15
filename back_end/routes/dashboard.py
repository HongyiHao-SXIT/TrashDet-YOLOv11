from flask import Blueprint, render_template, current_app, request, url_for, redirect
from flask_login import login_required
from app import db
from models.detection import Detection
from collections import Counter
from sqlalchemy import func
import json

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    recent = Detection.query.order_by(Detection.timestamp.desc()).limit(30).all()

    daily = db.session.query(func.date(Detection.timestamp).label("day"), func.count(Detection.id)).group_by(func.date(Detection.timestamp)).order_by(func.date(Detection.timestamp)).all()
    daily_counts = [[str(d[0]), d[1]] for d in daily]

    all_records = Detection.query.all()
    c = Counter()
    for r in all_records:
        try:
            classes = json.loads(r.classes or "[]")
            for cls in classes:
                c[cls] += 1
        except:
            pass

    class_data = dict(c)

    return render_template("dashboard.html", recent=recent, daily_counts=daily_counts, class_data=class_data)

@dashboard_bp.route("/list")
@login_required
def list_detections():
    q = Detection.query.order_by(Detection.timestamp.desc())
    page = int(request.args.get("page", 1))
    per_page = 20
    paged = q.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("detection_list.html", page_data=paged)

@dashboard_bp.route("/view/<int:detect_id>")
@login_required
def view_detection(detect_id):
    d = Detection.query.get_or_404(detect_id)
    return render_template("detection_detail.html", detect=d)
