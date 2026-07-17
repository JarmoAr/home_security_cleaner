import cv2
import os
from ultralytics import YOLO
import vision_service
import log_service
from config import SAMPLE_PATH

def extract_new_sample(video_path: str, target_class: str, save_folder: str, file_prefix: str) -> bool:
    """
    Scans a video for a specific target class using YOLOv8.
    Crops the detected object and saves it as a new template image.
    If target is a person, it requires a visible face using face_recognition.
    """
    try:
        # 1. Ensure the destination folder exists
        os.makedirs(save_folder, exist_ok=True)
        
        # 2. Capture screenshots from the video using the updated vision_service
        print(f"[SAMPLE] Opening video for sampling: {video_path}")
        frames = vision_service.capture_screenshots(video_path)
        if not frames:
            print("[SAMPLE] Video could not be opened or is empty.")
            return False

        # 3. Load YOLO model
        model = YOLO("yolov8n.pt")
        
        # 4. Find the next available increment number in the folder
        if os.path.exists(save_folder):
            existing_files = [f for f in os.listdir(save_folder) if f.startswith(file_prefix) and f.endswith('.jpg')]
            next_number = len(existing_files) + 1
        else:
            next_number = 1
        
        print(f"[SAMPLE] Searching for target '{target_class}'. Folder already contains {next_number-1} images. Next free number: {next_number}")
        
        # 5. Search for the object in the captured frames
        for frame in frames:
            results = model.predict(source=frame, verbose=False)
            
            if results:
                result = results[0]  # Take the first result object
                
                for box in result.boxes:
                    # Extract class ID from tensor
                    class_id = int(box.cls[0].item())
                    name = model.names[class_id]
                    
                    if name == target_class:
                        coordinates = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist(), list) else box.xyxy.tolist()
                        x1, y1, x2, y2 = map(int, coordinates)
                        
                        # Crop the object region from the frame
                        cropped_img = frame[y1:y2, x1:x2]
                        
                        if cropped_img.size > 0:
                            # If searching for a person, require face verification
                            if target_class == 'person':
                                import face_recognition
                                # Convert BGR to RGB for face_recognition
                                cropped_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                                faces = face_recognition.face_encodings(cropped_rgb)
                                
                                if len(faces) == 0:
                                    print("[SAMPLE] Person found, but face is not visible. Searching for a better angle...")
                                    continue  # Skip and look for a frame where the face is clear

                            # Save the image if requirements are met
                            new_filename = f"{file_prefix}{next_number}.jpg"
                            final_path = os.path.join(save_folder, new_filename)
                            
                            cv2.imwrite(final_path, cropped_img)
                            print(f"[SAMPLE] SUCCESS! New sample saved to: {final_path}")
                            return True
                        
        print(f"[SAMPLE] Could not find a clear '{target_class}' in this video.")
        return False

    except Exception as e:
        log_service.log_error(f"Error during sampling: {e}")
        print(f"[SAMPLE] !!! Error: {e}")
        return False


# ==============================================================================
# INTERACTIVE CLI TOOL MENU
# ==============================================================================
if __name__ == "__main__":
    sample_folder = str(SAMPLE_PATH)
    os.makedirs(sample_folder, exist_ok=True)
    
    # 1. Fetch all mp4/avi/mkv videos from the sample directory
    videos = [f for f in os.listdir(sample_folder) if f.endswith(('.mp4', '.avi', '.mkv'))]
    
    if not videos:
        print(f"\n[SAMPLE] The folder '{sample_folder}' is empty. Place some security videos there first!")
        exit()
        
    print(f"\n--- AI TEMPLATE SAMPLING TOOL ---")
    print(f"Found {len(videos)} video file(s) in {sample_folder}.\n")
    
    # 2. Iterate through videos one by one
    for i, video_name in enumerate(videos):
        full_video_path = os.path.join(sample_folder, video_name)
        print("="*60)
        print(f"PROCESSING VIDEO {i+1}/{len(videos)}: {video_name}")
        print("="*60)
        
        print("What object would you like to train from this video?")
        print("1 = Your Vehicle (car)")
        print("2 = Yourself / Family member (person)")
        print("3 = Your Dog (dog)")
        print("0 = Skip this video")
        print("x = Exit program")
        
        choice = input("Select an option (1-3, 0, x): ")
        
        if choice.lower() == "x":
            print("Exiting tool.")
            break
        elif choice == "0":
            print(f"Skipping video: {video_name}...\n")
            continue
        elif choice == "1":
            extract_new_sample(full_video_path, "car", "images/auto", "own_car")
        elif choice == "2":
            extract_new_sample(full_video_path, "person", "images/ihmiset", "known_person")
        elif choice == "3":
            extract_new_sample(full_video_path, "dog", "images/koira", "own_dog")
        else:
            print("Invalid selection. Skipping video.\n")
            
    print("\nAll videos processed. Sampling tool closed.")
