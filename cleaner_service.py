import os
from datetime import datetime
import log_service

def cleanup_folder(folder_path: str, days_to_keep: int = 30) -> bool:
    """
    Scans any specified directory and permanently deletes files older than the specified days.
    """
    try:
        # 1. Ensure the directory exists
        if not os.path.exists(folder_path):
            return True
            
        # 2. Get current time
        now = datetime.now()
        deleted_count = 0
        
        # 3. Iterate through all files in the directory
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            
            # Ensure it is a file and not a subdirectory
            if os.path.isfile(full_path):
                # Get the last modification time of the file
                modification_time_ts = os.path.getmtime(full_path)
                modification_time = datetime.fromtimestamp(modification_time_ts)
                
                # Calculate file age
                file_age = now - modification_time
                
                # 4. If the file is older than the allowed days, delete it
                if file_age.days >= days_to_keep:
                    os.remove(full_path)
                    deleted_count += 1
                    
        if deleted_count > 0:
            log_service.log_info(f"[CLEANER] Permanently removed {deleted_count} old file(s) from: {folder_path}")
        return True
    except Exception as e:
        log_service.log_error(f"Error during folder cleanup for {folder_path}: {e}")
        return False

def initialize_error_log(error_log_path: str) -> bool:
    """
    Initializes or clears the error log file at startup.
    """
    try:
        if os.path.exists(error_log_path):
            with open(error_log_path, 'w', encoding='utf-8') as f:
                f.write(f"Error log initialized: {datetime.now()}\n")
        else:
            with open(error_log_path, 'w', encoding='utf-8') as f:
                f.write(f"Error log created: {datetime.now()}\n")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize error log: {e}")
        return False
