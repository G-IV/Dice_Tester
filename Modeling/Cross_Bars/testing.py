from ultralytics import YOLO
data_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Vision/Modeling/Cross_Bars/data.yaml'
model_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Vision/Modeling/Cross_Bars/runs/training/weights/best.pt'
model = YOLO(model_path)
results = model.val(
    data=data_path, 
    device="mps", 
    imgsz=1024, 
    project='Cross_Bars/runs', 
    name='validation'
    )