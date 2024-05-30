import cv2
from paddleocr import PaddleOCR
import re

class Camera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0 (webcam)
        self.video = cv2.VideoCapture(0)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            # Encode the frame into JPEG format
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        else:
            # If the frame is not successfully read, return None
            return None

    def capture_image(self):
        success, image = self.video.read()
        if success:
            return image
        else:
            return None

    def perform_ocr_and_search_text(self, frame):
        # Convert the frame to RGB color space
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Perform OCR on the frame
        ocr_results = self.ocr.ocr(frame_rgb, cls=True)
        
        # Initialize a list to store all detected text
        detected_texts = []
        
        # Iterate through the OCR results and collect all text
        if ocr_results is not None and isinstance(ocr_results, list):
            for line in ocr_results:
                if isinstance(line, list):
                    for info in line:
                        if isinstance(info, list) and len(info) >= 2:
                            text = info[1][0]
                            detected_texts.append(text)
        
        # Return all detected text
        return detected_texts