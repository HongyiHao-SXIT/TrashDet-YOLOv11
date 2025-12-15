from app import db
from datetime import datetime
import json

class Detection(db.Model):
    __tablename__ = "detection"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    result_image = db.Column(db.String(300), nullable=True)
    classes = db.Column(db.Text, nullable=True)
    confidences = db.Column(db.Text, nullable=True)
    boxes = db.Column(db.Text, nullable=True)
    confidence_avg = db.Column(db.Float, nullable=True)
    count = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def classes_list(self):
        try:
            return json.loads(self.classes)
        except:
            return []

    def confidences_list(self):
        try:
            return json.loads(self.confidences)
        except:
            return []

    def boxes_list(self):
        try:
            return json.loads(self.boxes)
        except:
            return []
