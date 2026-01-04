import threading
from ultralytics import YOLO
import os

_model = None
_lock = threading.Lock()

def get_model(model_path=None):
    global _model
    with _lock:
        if _model is None:
            model_name = model_path or "yolov8n.pt"
            _model = YOLO(model_name)
        return _model

def detect_image(input_path, save_path=None, model_path=None):
    model = get_model(model_path)
    results = model(input_path)
    if save_path:
        try:
            results[0].save(save_dir=os.path.dirname(save_path))
        except Exception as e:
            print("Warning saving result:", e)
    return results
