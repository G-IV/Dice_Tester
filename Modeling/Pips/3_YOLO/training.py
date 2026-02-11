from ultralytics import YOLO

# Get absolute path for your data/model
data_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns/data.yaml'

# Loads a model - using the absolute path, I can put the model where I want it.
model = YOLO('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/yolov8n.pt')

results = model.train(
    data=data_path, 
    epochs=100, 
    imgsz=1024, 
    project='/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns', 
    name='runs',
    device="mps", 
    visualize=True,
    show=True,
    exist_ok=True,
    save_txt=True
    )