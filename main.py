import os
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Imported services 
import save_service
import name_service
import vision_service
import cleaner_service
import log_service

# Configuration imports
from config import WATCH_PATH, TEMP_PATH, ARCHIVE_PATH, DELETE_PATH, AI_RESULTS_PATH, create_directories

# Core parameters
WATCH_DIRECTORY = WATCH_PATH  # The directory where the camera drops new files
CHECK_INTERVAL_SECONDS = 2  # How often to scan the folder

def process_video(file_path: Path, temp_path: str, archive_path: str, delete_path: str):
    """
    Processes a single video file detected in the watch directory.
    Safely handles corrupted frames by routing bad files directly to trash.
    """
    print("\n" + "="*50)
    print(f"[PROCESS] Starting processing for: {file_path.name}")
    print("="*50)

    # Initialize path placeholder so except block can clean it up if AI crashes
    temp_target_path = None

    try:
        # 1. Get creation timestamp from file modification time
        file_timestamp = str(int(file_path.stat().st_mtime * 1000))
        formatted_timestamp = name_service.format_timestamp(file_timestamp)
        
        # 2. Define target path in temp folder
        temp_target_path = os.path.join(temp_path, f"{formatted_timestamp}.mp4")
        
        # 3. Move the file from incoming to temp directory to start processing safely
        print(f"[INFO] Moving file to temp directory...")
        shutil.move(str(file_path), temp_target_path)

        # 4. AI Vision Processing Baseline
        if os.path.exists(temp_target_path):
            print("[AI] Capturing screenshots for analysis...")
            screenshots = vision_service.capture_screenshots(temp_target_path)
            
            print("[AI] Analyzing objects in screenshots...")
            detections = vision_service.detect_objects(screenshots)
            print(f"[AI] Results: {detections}")
            
            # 5. Route the file based on AI results
            critical_targets = ["unknown_person", "unknown_car", "unknown_animal"]
            if any(target in detections for target in critical_targets):
                print("[CRITICAL] Unrecognized object detected! Moving video to ARCHIVE.")
                shutil.move(temp_target_path, os.path.join(archive_path, os.path.basename(temp_target_path)))
            else:
                print("[INFO] No threats detected. Moving video to TRASH.")
                shutil.move(temp_target_path, os.path.join(delete_path, os.path.basename(temp_target_path)))

    except Exception as e:
        log_service.log_error(f"Failed to process video {file_path.name}: {e}")
        
        # Write to local textual error log file
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error processing {file_path.name}: {e}\n")
            
        # CRITICAL RECOVERY: If the AI failed because the video file was corrupted (e.g. array stack crash),
        # move the bad file out of the temp folder into trash so the pipeline never deadlocks.
        if temp_target_path and os.path.exists(temp_target_path):
            try:
                corrupted_trash_target = os.path.join(delete_path, os.path.basename(temp_target_path))
                shutil.move(temp_target_path, corrupted_trash_target)
                log_service.log_info(f"[CLEANER] Successfully purged corrupted/unreadable frame stack video to trash: {file_path.name}")
            except Exception as backup_error:
                log_service.log_error(f"Failed to clear corrupted file from temp workspace: {backup_error}")

def main():
    # Ensure all required folders are created at startup
    create_directories() 
    
    # Initialize the daily rolling logging service (keeps last 7 days of logs)
    log_service.initialize_logger(days_to_keep=7)
    log_service.log_info("Application started and directory watcher is spinning up...")
    
    # Setup paths from config variables
    temp_path = str(TEMP_PATH)
    archive_path = str(ARCHIVE_PATH)
    delete_path = str(DELETE_PATH)
    ai_results_path = str(AI_RESULTS_PATH)  # Added for visual AI debugging logs/images
    
    # Automatic error log baseline cleanup
    cleaner_service.initialize_error_log("error_log.txt")

    # Force direct path architecture mapping from configuration settings
    watch_path = WATCH_PATH
    watch_path.mkdir(exist_ok=True)
    
    log_service.log_info(f"[START] Directory watcher active on: '{watch_path.resolve()}'")
    log_service.log_info(f"[START] Scanning every {CHECK_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.")

    # Initialize the date tracking variable for scheduled daily folder cleanups
    last_cleanup_date = None

    try:
        while True:
            current_time = datetime.now()
            current_date = current_time.date()
            
            # --- SCHEDULED DAILY STORAGE MAINTENANCE ---
            # If the maintenance has not been executed today, run it now at midnight rollover
            if last_cleanup_date != current_date:
                log_service.log_info("[MAINTENANCE] Running scheduled daily storage cleanup...")
                
                # OPTIMIZATION: Reduced retention from 30 days to 7 days to guarantee the 110 GB disk limit never overflows
                cleaner_service.cleanup_folder(delete_path, days_to_keep=7)
                
                # Clean the AI results visual debugging folder (7 days retention policy)
                cleaner_service.cleanup_folder(ai_results_path, days_to_keep=7)
                
                # Lock the current date to prevent re-running until the next midnight rollover
                last_cleanup_date = current_date

            
            # --- CONTINUOUS DIRECTORY WATCHER ---
            # Fetch a fresh list of all .mp4 and .MP4 files
            video_files = list(watch_path.glob("*.mp4")) + list(watch_path.glob("*.MP4"))
            
            if video_files:
                # Log the dynamic state of the processing queue length
                log_service.log_info(f"[QUEUE] Found {len(video_files)} video file(s) in queue. Starting processing loop...")
                
                # Sort files by modification time (oldest first for power outage recovery)
                video_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Select the first (oldest) video file from the queue safely using brackets
                file_path = video_files[0]
                
                try:
                    if file_path.exists():
                        initial_size = file_path.stat().st_size
                        
                        # If the file is completely empty (0 bytes), it's corrupted. Move it to trash to unblock the queue.
                        if initial_size == 0:
                            trash_target = Path(delete_path) / file_path.name
                            shutil.move(str(file_path), str(trash_target))
                            log_service.log_info(f"[CLEANER] Moved corrupted 0-byte file to trash: {file_path.name}")
                            continue  # Jump instantly back to fetch a fresh list!

                        # File is valid, proceed with stability check
                        time.sleep(0.5)
                        
                        if file_path.exists() and file_path.stat().st_size == initial_size:
                            # File is ready! Process it and route it dynamically based on AI analytics
                            process_video(file_path, temp_path, archive_path, delete_path)
                            continue
                except Exception as file_error:
                    pass
            
            # Wait 2 seconds before the next check (only if directory was empty or file was busy)
            time.sleep(CHECK_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n[STOP] Directory watcher stopped by user.")

if __name__ == "__main__":
    main()
