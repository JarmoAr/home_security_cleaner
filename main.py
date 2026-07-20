import os
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Imported services (Muutetaan nämäkin englanniksi myöhemmin jos haluat)
import save_service
import name_service
import vision_service
import cleaner_service
import log_service

# main.py tiedoston yläreunaan:
from config import WATCH_PATH, TEMP_PATH, ARCHIVE_PATH, DELETE_PATH, AI_RESULTS_PATH, create_directories

# Configuration
WATCH_DIRECTORY = WATCH_PATH  # The directory where the camera drops new files
CHECK_INTERVAL_SECONDS = 2  # How often to scan the folder

def main():
    # Ensure all required folders are created at startup
    create_directories()  
    
    # Initialize the automatic daily rolling log (keeps last 7 days)
    log_service.initialize_logger(days_to_keep=7)
    log_service.log_info("Application started and directory watcher is spinning up...")
    
    # SETUP PATHS
    temp_path = str(TEMP_PATH)
    archive_path = str(ARCHIVE_PATH)
    delete_path = str(DELETE_PATH)
    ai_results_path = str(AI_RESULTS_PATH) # Uusi muuttuja
    
    # AUTOMATIC MAINTENANCE (Runs once at startup)
    print("[STARTUP] Running automatic storage maintenance...")
    
    # 1. Siivotaan normaali roskakori (säilytys 30 päivää)
    cleaner_service.cleanup_folder(delete_path, days_to_keep=30)
    
    # 2. Siivotaan AI-tarkistuskansio (säilytys esim. 7 päivää, jottei täyty turhaan!)
    cleaner_service.cleanup_folder(ai_results_path, days_to_keep=7)
    
    cleaner_service.initialize_error_log("error_log.txt")

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
            screenshots = vision_service.capture_screenshots(temp_target_path)
            
            print("[AI] Analyzing objects in screenshots...")
            detections = vision_service.detect_objects(screenshots)
            print(f"[AI] Results: {detections}")
            
            # 5. Route the file based on AI results
            # Check if any unknown objects were detected
            critical_targets = ["unknown_person", "unknown_car", "unknown_animal"]
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

    # KORJAUS: Ohitetaan WATCH_DIRECTORY ja käytetään suoraan pomminvarmaa config-polkua
    watch_path = WATCH_PATH
    watch_path.mkdir(exist_ok=True)
    
    print(f"[START] Directory watcher active on: '{watch_path.resolve()}'")
    print(f"[START] Scanning every {CHECK_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.")

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
                
                # Clean the local trash folder (30 days retention policy)
                cleaner_service.cleanup_folder(delete_path, days_to_keep=30)
                
                # Clean the AI results visual debugging folder (7 days retention policy)
                cleaner_service.cleanup_folder(ai_results_path, days_to_keep=7)
                
                # Lock the current date to prevent re-running until the next midnight
                last_cleanup_date = current_date
            
            # --- CONTINUOUS DIRECTORY WATCHER ---
            # Fetch a fresh list of all .mp4 and .MP4 files
            video_files = list(watch_path.glob("*.mp4")) + list(watch_path.glob("*.MP4"))
            
            if video_files:
                # DEBUG PRINT: Tulostetaan heti löydettyjen tiedostojen määrä
                print(f"[DEBUG] Found {len(video_files)} video file(s) in queue. Starting processing loop...")
                
                # Sort files by modification time (oldest first for power outage recovery)
                video_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Select the first (oldest) video file from the queue safely using brackets
                file_path = video_files[0]
                
                try:
                    if file_path.exists():
                        initial_size = file_path.stat().st_size
                        
                        # DEBUG PRINT: Katsotaan tiedoston perustiedot livenä
                        print(f"[DEBUG-QUEUE] Checking file: {file_path.name} | Size: {initial_size} bytes")
                        
                        time.sleep(0.5)
                        
                        if file_path.exists() and file_path.stat().st_size == initial_size and initial_size > 0:
                            # File is ready! Process it and route it dynamically based on AI analytics
                            print(f"[DEBUG-QUEUE] File is stable. Sending to process_video...")
                            process_video(file_path, temp_path, archive_path, delete_path)
                            continue
                        else:
                            print(f"[DEBUG-QUEUE] File skipped! Reason -> Stable size: {file_path.stat().st_size == initial_size}, Size > 0: {initial_size > 0}")
                except Exception as file_error:
                    # TÄRKEÄÄ: Tulostetaan aito virhe ruudulle hiljaisen pass-ohituksen sijaan!
                    print(f"[DEBUG-ERROR] Failed to handle queue file: {file_error}")

            
            # Wait 2 seconds before the next check (only if directory was empty or file was busy)
            time.sleep(CHECK_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n[STOP] Directory watcher stopped by user.")

if __name__ == "__main__":
    main()
