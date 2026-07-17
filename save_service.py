import os
import log_service  # Keep this import for now if log_service is still used

def check_filename(filename: str, temp_path: str, archive_path: str) -> str:
    """
    Checks if a file with the same name already exists in temp or archive folders.
    If it exists, appends a counter (e.g., filename(1).mp4) to prevent overwriting.
    """
    try:
        temp_file_path = os.path.join(temp_path, filename + ".mp4")
        archive_file_path = os.path.join(archive_path, filename + ".mp4")
        name_counter = 1
        final_name = filename + ".mp4"

        while True:
            if os.path.exists(temp_file_path) or os.path.exists(archive_file_path):
                final_name = f"{filename}({name_counter}).mp4"
                name_counter += 1
                temp_file_path = os.path.join(temp_path, final_name)
                archive_file_path = os.path.join(archive_path, final_name)
            else:
                break
        
        return final_name

    except Exception as e:
        log_service.virhe_logi(f"Error checking filename duplicate: {e}", "error_log.txt")
        return filename + ".mp4"  # Return default as fallback
