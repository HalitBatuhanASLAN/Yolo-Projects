import cv2

from ultralytics import YOLO

model = YOLO('best.pt')

cam = cv2.VideoCapture(0)

print("Cam is opening... Press 'q' to exit.")

while True:
    ret, frame = cam.read()

    if not ret:
        print("Failed to grab frame. Exitting...")
        break

    result = model.predict(frame, conf = 0.40)
    for res in result:
        new_frame = res.plot()

        cv2.imshow("Yolo Deskptop Detection", new_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()