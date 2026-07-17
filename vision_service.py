import os
import cv2
import face_recognition
from ultralytics import YOLO
import log_service

def capture_screenshots(video_path):
    """
    Captures video frames every 2 seconds and returns them in a list.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps 
        else:
            video_length = 0
        
        screenshots = []
        second = 0
        while second < video_length:
            cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
            success, frame = cap.read()
            if success:
                screenshots.append(frame)
            second += 2
        cap.release()
        return screenshots
    except Exception as e:
        log_service.log_error(f"Error capturing screenshots: {e}")
        return []        

def detect_objects(screenshots):
    """
    Analyzes screenshots using YOLOv8 and categorizes detected objects.
    """
    try:
        model = YOLO("yolov8n.pt")
        detected_labels = [] 

        results = model.predict(source=screenshots, verbose=False, conf=0.60)

        for i, result in enumerate(results):
            for box in result.boxes:
                class_id = int(box.cls) if hasattr(box.cls, '__getitem__') else int(box.cls.item() if hasattr(box.cls, 'item') else box.cls)
                name = model.names[class_id]
                
                final_label = None

                if name == 'dog':
                    if is_own_dog(screenshots, results):
                        final_label = "own_dog"
                    else:
                        final_label = "unknown_animal"
                
                elif name in ['cat', 'bird', 'horse', 'sheep']:
                    final_label = "unknown_animal"

                elif name == 'person':
                    if is_known_person(screenshots):
                        final_label = "known_person"
                    else:
                        final_label = "unknown_person"

                elif name in ['car', 'truck']:
                    if is_own_car(screenshots, results):
                        final_label = "own_car"
                    else:
                        final_label = "unknown_car"

                if final_label and final_label not in detected_labels:
                    detected_labels.append(final_label)
        
        return detected_labels
    except Exception as e:
        log_service.log_error(f"Error detecting objects: {e}")
        return []

def is_own_dog(screenshots, yolo_results):
    """
    Compares the detected dog's color histogram with template images of the own dog.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(script_dir, "images", "koira")
        
        model_histograms = []
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(folder_path, file)
                    img = cv2.imread(path)
                    
                    if img is not None:
                        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                        # Lasketaan 2D-histogrammi kanaville 0 (Sävy) ja 1 (Kylläisyys)
                        hist = cv2.calcHist([hsv_img], [0, 1], None, [50, 60], [0, 180, 0, 256])
                        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                        model_histograms.append(hist)

        if len(model_histograms) == 0:
            return False

        for i, result in enumerate(yolo_results):
            frame = screenshots[i]
            
            for box in result.boxes:
                if hasattr(box.cls, 'tolist'):
                    classes = box.cls.tolist()
                    class_id = int(classes[0]) if classes else -1
                elif hasattr(box.cls, 'item'):
                    class_id = int(box.cls.item())
                else:
                    class_id = int(box.cls)
                
                # 16 = dog in COCO dataset
                if class_id == 16:
                    if hasattr(box.xyxy, 'tolist'):
                        coords = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist()[0], list) else box.xyxy.tolist()
                    else:
                        coords = box.xyxy
                    
                    x1, y1, x2, y2 = map(int, coords)
                    animal_roi = frame[y1:y2, x1:x2]
                    if animal_roi.size == 0:
                        continue
                        
                    video_hsv = cv2.cvtColor(animal_roi, cv2.COLOR_BGR2HSV)
                    video_hist = cv2.calcHist([video_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                    cv2.normalize(video_hist, video_hist, 0, 1, cv2.NORM_MINMAX)
                    
                    for m_hist in model_histograms:
                        match_score = cv2.compareHist(m_hist, video_hist, cv2.HISTCMP_CORREL)
                        if match_score > 0.25:
                            return True
        return False
    except Exception as e:
        log_service.log_error(f"Error checking own dog: {e}")
        return None

def is_own_car(screenshots, yolo_results):
    """
    Compares the detected vehicle's color histogram with template images of the own car.
    Supports Infrared (Night) mode using aspect ratio.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(script_dir, "images", "auto")
        
        model_histograms = []
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith(('.jpg', '.jpeg', '.png')):
                    path = os.path.join(folder_path, file)
                    img = cv2.imread(path)
                    
                    if img is not None:
                        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                        hist = cv2.calcHist([hsv_img], [0, 1], None, [50, 60], [0, 180, 0, 256])
                        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                        model_histograms.append(hist)

        if len(model_histograms) == 0:
            return False

        for i, result in enumerate(yolo_results):
            frame = screenshots[i]
            
            for box in result.boxes:
                if hasattr(box.cls, 'tolist'):
                    classes = box.cls.tolist()
                    class_id = int(classes[0]) if classes else -1
                elif hasattr(box.cls, 'item'):
                    class_id = int(box.cls.item())
                else:
                    class_id = int(box.cls)
                
                # 2 = car, 7 = truck
                if class_id in [2, 7]:
                    if hasattr(box.xyxy, 'tolist'):
                        coords = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist()[0], list) else box.xyxy.tolist()
                    else:
                        coords = box.xyxy
                    
                    x1, y1, x2, y2 = map(int, coords)
                    width = x2 - x1
                    height = y2 - y1
                    
                    aspect_ratio = width / height if height > 0 else 0

                    car_roi = frame[y1:y2, x1:x2]
                    if car_roi.size == 0:
                        continue
                        
                    video_hsv = cv2.cvtColor(car_roi, cv2.COLOR_BGR2HSV)
                    
                    # NIGHT MODE DETECTION (Infrared)
                    s_channel = video_hsv[:, :, 1]
                    saturation_mean = cv2.mean(s_channel)[0]
                    
                    is_night_mode = saturation_mean < 8.0
                    
                    if is_night_mode:
                        if aspect_ratio > 1.2:
                            return True
                    else:
                        # DAY MODE: Run normal color histogram matching
                        video_hist = cv2.calcHist([video_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                        cv2.normalize(video_hist, video_hist, 0, 1, cv2.NORM_MINMAX)
                        
                        for m_hist in model_histograms:
                            match_score = cv2.compareHist(m_hist, video_hist, cv2.HISTCMP_CORREL)
                            if aspect_ratio > 1.2 and match_score > 0.45:
                                return True 
                            
        return False
    except Exception as e:
        log_service.log_error(f"Error checking own car: {e}")
        return None

def is_known_person(screenshots):
    """
    Uses face_recognition to verify if a person matches known face images.
    """
    try:
        folder_path = "images/ihmiset"
        template_images = []
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith((".jpg", ".JPEG", ".png")):
                    template_images.append(os.path.join(folder_path, file))

        known_encodings = []
        for template in template_images:
            img = face_recognition.load_image_file(template)
            img_encodings = face_recognition.face_encodings(img)
            if len(img_encodings) > 0:
                known_encodings.append(img_encodings[0])

        for frame in screenshots:
            frame_encodings = face_recognition.face_encodings(frame)
            for encoding in frame_encodings:
                matches = face_recognition.compare_faces(known_encodings, encoding)
                if True in matches:
                    return True
        return False
    except Exception as e:
        log_service.log_error(f"Error recognizing person: {e}")
        return None
