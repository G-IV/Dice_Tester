import cv2
import numpy as np

# 1. Initialize Camera
cap = cv2.VideoCapture(0) # 0 is usually the default camera

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# 2. Define callback function for trackbars (required by cv2.createTrackbar)
def nothing(x):
    pass

# 3. Create a Window for the controls
cv2.namedWindow('Control Panel')
cv2.resizeWindow('Control Panel', 400, 300)

# 4. Create Trackbars (Name, Window Name, Min, Max, Callback)
# Note: Not all cameras support all properties.
cv2.createTrackbar('Brightness', 'Control Panel', 100, 200, nothing)
# cv2.createTrackbar('Contrast', 'Control Panel', 100, 200, nothing)
# cv2.createTrackbar('Exposure', 'Control Panel', -6, 0, nothing)

print("Press 'q' to exit.")

while True:
    # 5. Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # 6. Get current positions of trackbars
    brightness = cv2.getTrackbarPos('Brightness', 'Control Panel')
    contrast = cv2.getTrackbarPos('Contrast', 'Control Panel')
    exposure = cv2.getTrackbarPos('Exposure', 'Control Panel')

    # 7. Apply settings to the camera
    # Convert slider values to usable camera properties
    cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness / 100.0) # 0.0 to 2.0
    cap.set(cv2.CAP_PROP_CONTRAST, contrast / 100.0)    # 0.0 to 2.0
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure)            # Varies by camera

    # Optional: Display settings on the image
    cv2.putText(frame, f'B: {brightness} C: {contrast} E: {exposure}', 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 8. Display the resulting frame
    cv2.imshow('Camera Feed', frame)

    # 9. Break loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 10. Clean up
cap.release()
cv2.destroyAllWindows()