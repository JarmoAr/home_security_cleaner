from pathlib import Path
import log_service

# Base directory (Peruskansio käyttäjän kotihakemistossa)
BASE_DIR = Path.home() / "security_camera_data"

# Core directories (Pääkansiot)
WATCH_PATH = BASE_DIR / "incoming_videos"  # NEW: The folder where the camera drops new files
TEMP_PATH = BASE_DIR / "temp"
ARCHIVE_PATH = BASE_DIR / "archive"        # Matches the updated archive naming
DELETE_PATH = BASE_DIR / "trash"

# Service directories (Muut kansiot)
SAMPLE_PATH = BASE_DIR / "samples"
AI_RESULTS_PATH = BASE_DIR / "ai_results"

# Combined list of all directories to create
ALL_PATHS = [
    WATCH_PATH,
    TEMP_PATH,
    ARCHIVE_PATH,
    DELETE_PATH,
    SAMPLE_PATH,
    AI_RESULTS_PATH,
]

def create_directories() -> bool:
    """
    Ensures all required project directories exist on the system.
    Creates them if they are missing.
    """
    try:
        for path in ALL_PATHS:
            path.mkdir(parents=True, exist_ok=True)
        print("[INFO] All required directories verified/created successfully.")
        return True
    except Exception as e:
        log_service.log_error(f"Error in create_directories(): {e}")
        return False
