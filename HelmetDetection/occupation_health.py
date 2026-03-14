import cv2 # opencv library, to read and process video frames
from ultralytics import YOLO

model = YOLO('best.pt')
# curently no video is provided, so we will use a sample video for testing
video_path = "exampleVideo.mp4"

# it prepare the video for processing
cam = cv2.VideoCapture(video_path)

while True:
    # read function captures a frame and return a value
    ret, frame = cam.read()
    if not ret:
        break
    # by using track method, we can track the objects in the video and persist the results for each frame
    # persist is for remamaber the objects in the previous frames
    results = model.track(frame, persist = True, conf= 0.5)

    selected_frame = results[0].plot()
    cv2.imshow("Occupational Health and Safety", selected_frame)

    # waits 30 milisecond between frames
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cam.release() # release the video capture object
cv2.destroyAllWindows() # closes all windows