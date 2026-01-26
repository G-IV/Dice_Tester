import cv2
from ultralytics import YOLO

# Load your custom YOLO model
# model = YOLO('./1 - Images/runs/detect/training4/weights/best.pt')  # Update the path to your model weights
model = YOLO('./4 - Single Side/runs/training/weights/best.pt')  # Update the path to your model weights

# Open the default camera (0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

def count_pips(frame, results):
    """
    Count the number of pips (dots) on detected dice.
    Uses contour detection to find circular pips within bounding boxes.
    """
    pip_count = 0
    
    # Get the first result
    result = results[0]
    
    # Iterate through detected objects
    for box in result.boxes:
        # Get bounding box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # Crop the region of interest (the die)
        roi = frame[y1:y2, x1:x2]
        
        if roi.size == 0:
            continue
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding to detect dark pips
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours (pips)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and circularity to count pips
        die_pips = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200 and area < 50:  # Adjust these thresholds based on your die size
                # Check circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * 3.14159 * area / (perimeter * perimeter)
                    if circularity > 0.5:  # Circular enough to be a pip
                        die_pips += 1
        
        pip_count += die_pips
        
        # Display pip count on the frame
        cv2.putText(frame, f"Pips: {die_pips}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return pip_count

while True:
    # Read frame from camera
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame")
        break
    
    # Run YOLO prediction
    results = model(frame)
    
    # Draw bounding boxes on frame
    annotated_frame = results[0].plot()

    # # Count pips and display the count
    # total_pips = count_pips(frame, results)
    # cv2.putText(annotated_frame, f"Total Pips: {total_pips}", (10, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    
    
    # Display the frame
    cv2.imshow('YOLO Object Detection', annotated_frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()