import os
from ultralytics import YOLO

def main():
    print("=== YOLO 垃圾识别程序 ===")
    
    model_path = input("请输入 YOLOv11 模型路径 (例如: best.pt): ").strip()
    if not os.path.exists(model_path):
        print("❌ 模型文件不存在！")
        return

    img_path = input("请输入要识别的图片路径: ").strip()
    if not os.path.exists(img_path):
        print("❌ 图片文件不存在！")
        return

    print("正在加载模型...")
    model = YOLO(model_path)

    print("正在识别，请稍候...")
    results = model(img_path)

    save_dir = os.path.dirname(img_path)
    results[0].save(filename=os.path.join(save_dir, "detected_" + os.path.basename(img_path)))

    print("🎉 识别完成！")
    print(f"已输出标注图片: {os.path.join(save_dir, 'detected_' + os.path.basename(img_path))}")


if __name__ == "__main__":
    main()
