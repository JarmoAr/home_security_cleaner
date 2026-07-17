from datetime import datetime
from zoneinfo import ZoneInfo
import log_service  # Keep this import for now if log_service is still used

def format_timestamp(timestamp):
    """
    Converts a millisecond timestamp into a readable string format (YYYYMMDD_HHMMSS).
    """
    try:
        # Convert milliseconds to seconds
        timestamp_seconds = int(timestamp) / 1000
        
        # Format the timestamp into a readable date-time string
        formatted_date = datetime.fromtimestamp(timestamp_seconds).strftime('%Y%m%d_%H%M%S')
        return formatted_date
    
    except Exception as e:
        # If you still use the old log_service:
        log_service.virhe_logi(f"Error converting timestamp: {e}", "error_log.txt")
        return None
