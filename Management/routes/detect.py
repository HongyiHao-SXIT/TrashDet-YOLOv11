import os
import uuid
import json
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory, flash
from flask_login import login_required, current_user
from app import db
from models.detection import Detection
from models.yolo_model import detect_image, get_model
from werkzeug.utils import secure_filename

ALLOWED_EXT = {"png","jpg","jpeg","bmp"}

detect_bp = Blueprint("detect", __name__, url_prefix="/detect")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

@detect_bp.route("/upload", methods=["GET","POST"])
@login_required
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("未找到上传文件", "warning")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == "":
            flash("未选择文件", "warning")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename_orig = secure_filename(file.filename)
            unique = f"{uuid.uuid4().hex}_{filename_orig}"
            input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique)
            file.save(input_path)

            try:
                results = get_model()(input_path)
            except Exception as e:
                flash(f"模型推理失败: {e}", "danger")
                return redirect(request.url)
            try:
                results[0].save(save_dir=current_app.config['RESULT_FOLDER'])
                result_image_name = os.path.basename(results[0].path) if hasattr(results[0], "path") else unique
                result_image_name = unique if result_image_name is None else result_image_name
            except Exception:
                result_image_name = unique
            boxes = []
            classes = []
            confs = []
            try:
                boxes_attr = getattr(results[0], "boxes", None)
                if boxes_attr is not None:
                    for b in boxes_attr:
                        xyxy = b.xyxy.tolist() if hasattr(b, "xyxy") else None
                        conf = float(b.conf) if hasattr(b, "conf") else None
                        cls = int(b.cls) if hasattr(b, "cls") else None
                        boxes.append(xyxy)
                        confs.append(conf)
                        try:
                            name = get_model().names[cls]
                        except Exception:
                            name = str(cls)
                        classes.append(name)
                else:
                    pass
            except Exception as e:
                print("解析 boxes 出错:", e)

            try:
                if len(classes) == 0 and hasattr(results[0], "boxes") and hasattr(results[0].boxes, "cls"):
                    for cls in results[0].boxes.cls:
                        idx = int(cls)
                        classes.append(get_model().names[idx])
            except Exception:
                pass

            conf_vals = [c for c in confs if c is not None]
            conf_avg = float(sum(conf_vals)/len(conf_vals)) if conf_vals else 0.0

            record = Detection(
                filename=unique,
                result_image=result_image_name,
                classes=json.dumps(classes, ensure_ascii=False),
                confidences=json.dumps(confs),
                boxes=json.dumps(boxes),
                confidence_avg=conf_avg,
                count=len(classes),
                user_id=current_user.id
            )
            db.session.add(record)
            db.session.commit()

            flash("上传并检测完成", "success")
            return redirect(url_for("dashboard.view_detection", detect_id=record.id))
        else:
            flash("仅支持图片格式：png/jpg/jpeg/bmp", "warning")
    return render_template("index.html")
