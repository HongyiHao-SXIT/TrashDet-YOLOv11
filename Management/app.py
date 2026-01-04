from flask import Flask, render_template, Response, jsonify
import cv2
import torch
import pymysql
from datetime import datetime
from ultralytics import YOLO

app = Flask(__name__)

# 加载 YOLO 模型
model = YOLO("weights/garbage.pt")

# 摄像头
cap = cv2.VideoCapture(0)

# 数据库连接
db = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='garbage_db'
)

def save_to_db(category, lat, lng, conf):
    cursor = db.cursor()
    sql = """INSERT INTO garbage_record
             (category, latitude, longitude, confidence, time)
             VALUES (%s,%s,%s,%s,%s)"""
    cursor.execute(sql, (category, lat, lng, conf, datetime.now()))
    db.commit()

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)
        for *box, conf, cls in results.xyxy[0]:
            label = model.names[int(cls)]
            save_to_db(label, 39.9042, 116.4074, float(conf))  # 示例GPS

        frame = results.render()[0]
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    cursor = db.cursor()
    cursor.execute("SELECT category, COUNT(*) FROM garbage_record GROUP BY category")
    data = cursor.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
