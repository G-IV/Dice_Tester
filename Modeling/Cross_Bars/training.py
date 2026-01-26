from ultralytics import YOLO
import os

# Get absolute path for your data/model
data_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Vision/Modeling/Cross_Bars/data.yaml'
model = YOLO('yolov8n.pt')
results = model.train(
    data=data_path, 
    epochs=100, 
    imgsz=1024, 
    project='/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Vision/Modeling/Cross_Bars/runs/', 
    name='training',
    device="mps", 
    visualize=True,
    show=True,
    exist_ok=True,
    save_txt=True
    )