from flask import Blueprint, render_template
from flask_login import login_required
from models.detection import Detection
import json

map_bp = Blueprint("map", __name__, url_prefix="/map")

@map_bp.route("/")
@login_required
def index():
    points = []
    recs = Detection.query.filter(Detection.latitude.isnot(None), Detection.longitude.isnot(None)).all()
    for r in recs:
        points.append({
            "id": r.id,
            "lat": r.latitude,
            "lng": r.longitude,
            "img": r.result_image,
            "time": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "classes": json.loads(r.classes or "[]")
        })
    return render_template("map.html", points=points)
