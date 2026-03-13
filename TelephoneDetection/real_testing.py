import cv2
from ultralytics import YOLO

model = YOLO('best.pt')

# 0 coreespındings to default webcam, 1 for external webcam, and so on
cam = cv2.VideoCapture(0)

print("Cam is opening... Press 'q' to exit.")

while True:
    ret, frame = cam.read() # capture the current frame

    # if grebbing frame couldnot heppen
    if not ret:
        print("Failed to grab frame. Exitting...")
        break

    # stream = true is optimazing the mem usge for taking frames
    results = model.predict(frame, stream = True, conf = 0.40)

    for res in results:
        new_frame = res.plot() # plot the results on the frame

        # show new_frame into a window
        cv2.imshow("Yolo Telephone Detection", new_frame)

    # wait for 1ms and check if 'q' is pressed to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exitting...")
        break

cam.release()
cv2.destroyAllWindows()
