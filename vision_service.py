import os
import math
from types import SimpleNamespace
import cv2
import face_recognition
from ultralytics import YOLO
import log_service

class CorruptVideoError(ValueError):
    """The video cannot provide valid sampled frames."""


def capture_screenshots(video_path):
    """Capture frames every two seconds; propagate non-decoding errors."""
    # Missing/inaccessible files are filesystem errors, not corrupt videos.
    with open(video_path, "rb"):
        pass
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise CorruptVideoError(f"Decoder cannot open video: {video_path}")
        fps = cap.get(cv2.CAP_PROP_FPS)
        total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if not math.isfinite(fps) or fps <= 0 or not math.isfinite(total) or total <= 0:
            raise CorruptVideoError(f"Invalid video metadata: {video_path}")
        screenshots = []
        second = 0
        while second < total / fps:
            if not cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000):
                raise RuntimeError(f"Decoder cannot seek to {second}s")
            success, frame = cap.read()
            if not success or frame is None:
                raise CorruptVideoError(f"Unreadable video frame at {second}s")
            screenshots.append(frame)
            second += 2
        return screenshots
    finally:
        cap.release()


def load_known_faces():
    encodings = []
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "ihmiset")
    if os.path.isdir(folder):
        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                image = face_recognition.load_image_file(os.path.join(folder, filename))
                faces = face_recognition.face_encodings(image)
                if faces:
                    encodings.append(faces[0])
    return encodings


def detect_objects(screenshots):
    """Analyze each object locally, without rescanning the entire video."""
    try:
        if not screenshots:
            raise RuntimeError("No frames supplied to object detection")
        model = YOLO("yolov8n.pt")
        labels = set()
        known_encodings = None
        for i, frame in enumerate(screenshots, 1):
            print(f"[AI] Frame {i}/{len(screenshots)}: detecting objects", flush=True)
            result = model.predict(source=frame, verbose=False, conf=0.60)[0]
            for box in result.boxes:
                name = model.names[int(box.cls.item())]
                single_result = SimpleNamespace(boxes=[box])
                label = None
                if name == "dog":
                    own = is_own_dog([frame], [single_result])
                    label = "own_dog" if own else "unknown_animal"
                elif name in ("cat", "bird", "horse", "sheep"):
                    label = "unknown_animal"
                elif name in ("car", "truck"):
                    own = is_own_car([frame], [single_result])
                    label = "own_car" if own else "unknown_car"
                elif name == "person":
                    if known_encodings is None:
                        known_encodings = load_known_faces()
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    height, width = frame.shape[:2]
                    crop = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
                    print(f"[AI] Frame {i}: checking person crop", flush=True)
                    known = crop.size > 0 and is_known_person([crop], known_encodings)
                    label = "known_person" if known else "unknown_person"
                if label:
                    labels.add(label)
            print(f"[AI] Frame {i} complete: {sorted(labels)}", flush=True)
        return sorted(labels)
    except Exception as error:
        log_service.log_error(f"Error detecting objects: {error}")
        raise


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
        raise

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
        raise

def is_known_person(screenshots, known_encodings=None):
    """Check cropped people using RGB frames and reusable face templates."""
    try:
        if known_encodings is None:
            known_encodings = load_known_faces()
        if not known_encodings:
            return False
        for frame in screenshots:
            height, width = frame.shape[:2]
            if not height or not width:
                continue
            scale = min(1.0, 640 / max(height, width))
            small = cv2.resize(frame, (max(1, round(width * scale)), max(1, round(height * scale))))
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_encodings(rgb)
            # A known face must not hide an unknown face inside the same crop.
            if faces and all(any(face_recognition.compare_faces(known_encodings, face)) for face in faces):
                return True
        return False
    except Exception as error:
        log_service.log_error(f"Error recognizing person: {error}")
        raise
