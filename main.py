import os
import time
import shutil
import logging
from pathlib import Path

# Imported services (Muutetaan nämäkin englanniksi myöhemmin jos haluat)
import save_service
import name_service
import vision_service
import cleaner_service
from config import TEMP_PATH, ARKISTO_PATH, DELETE_PATH, luo_kansiot

# Configuration
WATCH_DIRECTORY = "./incoming_videos"  # The directory where the camera drops new files
CHECK_INTERVAL_SECONDS = 2  # How often to scan the folder

def main():
    # Luo tarvittavat kansiot (temp, arkisto jne.)
    luo_kansiot()  
    
    # Käynnistetään uusi automaattisesti rullaava loki (säästetään 7 päivää)
    log_service.initialize_logger(days_to_keep=7)
    log_service.log_info("Application started and folder watcher is active.")

def process_video(file_path: Path, temp_path: str, archive_path: str, delete_path: str):
    """
    Processes a single video file detected in the watch directory.
    """
    print("\n" + "="*50)
    print(f"[PROCESS] Starting processing for: {file_path.name}")
    print("="*50)

    try:
        # 1. Get creation timestamp from the file name or system
        # (Using your name_service to handle the format if needed)
        # Note: If the filename contains the time, you can extract it here.
        # For now, we use file modification time as a backup.
        file_timestamp = str(int(file_path.stat().st_mtime * 1000))
        formatted_timestamp = name_service.format_timestamp(file_timestamp)
        
        # 2. Define target path in temp folder
        temp_target_path = os.path.join(temp_path, f"{formatted_timestamp}.mp4")
        
        # 3. Move the file from incoming to temp directory to start processing safely
        print(f"[INFO] Moving file to temp directory...")
        shutil.move(str(file_path), temp_target_path)

        # 4. AI Vision Processing
        if os.path.exists(temp_target_path):
            print("[AI] Capturing screenshots for analysis...")
            screenshots = vision_service.ota_kuvakaappaukset(temp_target_path)
            
            print("[AI] Analyzing objects in screenshots...")
            detections = vision_service.tunnista_kohteet(screenshots)
            print(f"[AI] Results: {detections}")
            
            # 5. Route the file based on AI results
            # Check if any unknown objects were detected
            critical_targets = ["vieras_ihminen", "vieras_auto", "vieras_elain"]
            if any(target in detections for target in critical_targets):
                print("[CRITICAL] Unrecognized object detected! Moving video to ARCHIVE.")
                shutil.move(temp_target_path, os.path.join(archive_path, os.path.basename(temp_target_path)))
            else:
                print("[INFO] No threats detected. Moving video to TRASH.")
                shutil.move(temp_target_path, os.path.join(delete_path, os.path.basename(temp_target_path)))

    except Exception as e:
        print(f"[ERROR] Failed to process video {file_path.name}: {e}")
        # Assuming you want to keep the error log initialization style
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error processing {file_path.name}: {e}\n")

def main():
    # Ensure all required folders are created at startup
    luo_kansiot()  
    
    # Setup paths
    temp_path = str(TEMP_PATH)
    archive_path = str(ARKISTO_PATH)
    delete_path = str(DELETE_PATH)
    
    # Automatic trash cleanup (runs once at startup)
    print("[STARTUP] Running automatic trash maintenance...")
    cleaner_service.siivoa_roskakori(delete_path, paivia_sailytetään=30)
    cleaner_service.alusta_virheloki("error_log.txt")

    # Ensure the watch directory exists
    watch_path = Path(WATCH_DIRECTORY)
    watch_path.mkdir(exist_ok=True)
    
    print(f"[START] Directory watcher active on: '{watch_path.resolve()}'")
    print(f"[START] Scanning every {CHECK_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.")

    try:
        while True:
            # Scan the folder for any .mp4 files
            video_files = list(watch_path.glob("*.mp4"))
            
            if video_files:
                for file_path in video_files:
                    # Check if the camera has finished writing the file
                    # If the file size is still changing, wait for it to finish
                    initial_size = file_path.stat().st_size
                    time.sleep(0.5)
                    
                    if file_path.stat().st_size == initial_size and initial_size > 0:
                        # File is stable and ready to be processed
                        process_video(file_path, temp_path, archive_path, delete_path)
            
            # Wait before the next folder scan
            time.sleep(CHECK_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n[STOP] Directory watcher stopped by user.")

if __name__ == "__main__":
    main()
