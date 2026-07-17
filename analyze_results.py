import os
import cv2
from ultralytics import YOLO
import vision_service
from config import AI_RESULTS_PATH

def analyze_video_individually(video_path: str, output_folder: str):
    """
    Analyzes a single video file, runs YOLO object detection, applies deep matching,
    and draws colored bounding boxes around detected objects.
    """
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]
    print("\n" + "="*60)
    print(f"ANALYZING MYSTERY VIDEO: {os.path.basename(video_path)}")
    print("="*60)

    # 1. Capture screenshots exactly like the main pipeline does
    frames = vision_service.capture_screenshots(video_path)
    print(f"Video split into {len(frames)} frames (every 2 seconds).")

    # 2. Load YOLO model
    model = YOLO("yolov8n.pt")
    
    # 3. Run predictions on frames
    results = model.predict(source=frames, verbose=False, conf=0.60)

    any_detections = False

    # 4. Loop through frames and analyze detections with timestamps
    for i, result in enumerate(results):
        timestamp_seconds = i * 2
        # Create a copy of the frame to draw on
        drawn_frame = frames[i].copy()
        has_drawn_objects = False
        
        if len(result.boxes) > 0:
            for box in result.boxes:
                if hasattr(box.cls, 'tolist'):
                    classes = box.cls.tolist()
                    class_id = int(classes[0]) if classes else -1
                elif hasattr(box.cls, 'item'):
                    class_id = int(box.cls.item())
                else:
                    class_id = int(box.cls)
                    
                name = model.names[class_id] if class_id in model.names else f"Unknown ({class_id})"
                confidence = float(box.conf.item() if hasattr(box.conf, 'item') else box.conf)
                
                print(f"  [Timestamp {timestamp_seconds:02d}s] --> Detected: '{name}' ({confidence*100:.1f}%)")
                any_detections = True
                
                # Get bounding box coordinates
                if hasattr(box.xyxy, 'tolist'):
                    coords = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist()[0], list) else box.xyxy.tolist()
                else:
                    coords = box.xyxy
                x1, y1, x2, y2 = map(int, coords)

                # AI deep validation and dynamic box drawing
                if class_id in [2, 7] or name in ['car', 'truck']:
                    if vision_service.is_own_car(frames, [result]):
                        print(f"    └── 🟩 AI DECISION: Target is OWN VEHICLE")
                        cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box for own car
                        cv2.putText(drawn_frame, f"Own Car {confidence*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        print(f"    └── 🟥 AI DECISION: UNKNOWN VEHICLE!")
                        cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red box for stranger
                        cv2.putText(drawn_frame, f"Stranger Car {confidence*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    has_drawn_objects = True

                elif class_id == 0 or name == 'person':
                    if vision_service.is_known_person(frames):
                        print(f"    └── 🟩 AI DECISION: Target is KNOWN PERSON")
                        cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (255, 255, 0), 2)  # Yellow box for family
                        cv2.putText(drawn_frame, f"Known Person {confidence*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                    else:
                        print(f"    └── 🟥 AI DECISION: UNKNOWN PERSON!")
                        cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red box for intruder
                        cv2.putText(drawn_frame, f"INTRUDER {confidence*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    has_drawn_objects = True

                elif class_id == 16 or name == 'dog':
                    if vision_service.is_own_dog(frames, [result]):
                        print(f"    └── 🟩 AI DECISION: Target is OWN DOG")
                        cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box for own dog
                        cv2.putText(drawn_frame, f"Own Dog {confidence*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        print(f"    └── 🟥 AI DECISION: UNKNOWN ANIMAL!")
                        cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red box for unknown animal
                        cv2.putText(drawn_frame, f"Unknown Animal {confidence*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    has_drawn_objects = True

            # Save the frame as an image if an important object was drawn
            if has_drawn_objects:
                image_name = f"{video_base_name}_detection_{timestamp_seconds:02d}s.jpg"
                image_path = os.path.join(output_folder, image_name)
                cv2.imwrite(image_path, drawn_frame)
                print(f"    [INFO] Detection saved as image: {image_name}")
                
    if not any_detections:
        print("\n[INFO] YOLO did not find any targets in this video.")
    print("="*60 + "\n")

if __name__ == "__main__":
    results_folder = str(AI_RESULTS_PATH)
    os.makedirs(results_folder, exist_ok=True)
    
    videos = [f for f in os.listdir(results_folder) if f.endswith(('.mp4', '.avi', '.mkv'))]
    
    if not videos:
        print(f"\n[INFO] Target folder '{results_folder}' is empty. No videos to analyze.")
        exit()
        
    print(f"\n--- SECURITY CAMERA AI ANALYSIS TOOL ---")
    print(f"Found {len(videos)} video file(s) to check.\n")
    
    for video_name in videos:
        full_video_path = os.path.join(results_folder, video_name)
        analyze_video_individually(full_video_path, results_folder)
        
    print("All targeted videos analyzed and detection frames saved successfully!")
