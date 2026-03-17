import cv2
from ultralytics import YOLO

model = YOLO('best.pt')

cam = cv2.VideoCapture(0)

print("Cashier System Active! Show the products to the camera... (Press 'q' to exit)")

while True:
    ret, frame = cam.read()
    
    if not ret:
        print("Failed to grab frame")
        break

    results = model.predict(source = frame, conf=0.5,verbose=False)

    selected_frame = results[0].plot()
    cv2.imshow("Cashier System", selected_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
