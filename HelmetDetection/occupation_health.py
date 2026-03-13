import cv2
from ultralytics import YOLO

model = YOLO('best.pt')

video_path = "exampleVideo.mp4"
cam = cv2.VideoCapture(video_path)

while True:
    ret, frame = cam.read()
    if not ret:
        break
    # by using track method, we can track the objects in the video and persist the results for each frame
    results = model.track(frame, persist = True, conf= 0.5)

    selected_frame = results[0].plot()
    cv2.imshow("Occupational Health and Safety", selected_frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()