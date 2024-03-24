from ultralytics import YOLO
from PIL import Image
import cv2

def pred_image(file):
    model = YOLO(r"Model\best.pt")
    im1 = Image.open(file)
    print(im1)
    results = model.predict(source=im1, save=True,save_txt=True)
