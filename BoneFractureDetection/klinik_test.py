import cv2

from ultralytics import YOLO

model = YOLO("best.pt")

photo_path = "indir.jpg"

results = model.predict(photo_path, conf=0.10)

selected_result = results[0].plot()
cv2.imshow("Selected Result", selected_result)
cv2.waitKey(0)
cv2.destroyAllWindows()

