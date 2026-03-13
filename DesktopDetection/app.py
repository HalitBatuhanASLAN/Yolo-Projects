import gradio as gr
import cv2
from ultralytics import YOLO

model = YOLO('best.pt')

# defining a function to detect objects which loaded into web app
def detect_obj(img):
    results = model.predict(img, conf=0.40)

    # keep results into a numpy array
    boxed_photo = results[0].plot()

    # YOLO gives colors as in BGR format, web is in RGB format, so we need to convert it
    boxed_photo_rgb = cv2.cvtColor(boxed_photo, cv2.COLOR_BGR2RGB)

    return boxed_photo_rgb

interface = gr.Interface(
    fn = detect_obj,
    inputs = gr.Image(type="numpy",label = "Upload image"),
    outputs = gr.Image(type="numpy", label = "Detected image result"),
    title = "YOLO Desktop Object Detection Web App",
    description = "Upload an image to detect objects like person, computer, tv, chair(related to office) using YOLOv8 model. The detected objects will be highlighted in the output image."
)

if __name__ == "__main__":
    interface.launch()