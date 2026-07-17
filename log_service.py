import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Asetetaan kansio lokeille (luodaan automaattisesti)
LOG_DIR = "./logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def initialize_logger(days_to_keep: int = 7):
    """
    Initializes a rolling logger that creates a new file every midnight
    and automatically deletes files older than days_to_keep.
    """
    try:
        # Varmistetaan, että logs-kansio on olemassa
        os.makedirs(LOG_DIR, exist_ok=True)

        # TimedRotatingFileHandler hoitaa automaattisen rullauksen keskiyöllä ('midnight')
        # backupCount määrittää, kuinka monta vanhaa päivää säästetään (esim. 7)
        handler = TimedRotatingFileHandler(
            LOG_FILE, 
            when="midnight", 
            interval=1, 
            backupCount=days_to_keep,
            encoding="utf-8"
        )
        
        # Määritetään lokiviestin ulkoasu (Aikaleima - [TASO] - Viesti)
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)

        # Otetaan käyttöön globaali Python-logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        logging.info("Logger initialized successfully. Daily rolling active.")
        return True
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Could not initialize logger: {e}")
        return False

def log_error(message: str):
    """
    Call this anywhere in the app to log an error.
    """
    logging.error(message)

def log_info(message: str):
    """
    Call this anywhere in the app to log general information.
    """
    logging.info(message)

# TÄMÄ ON KORVAAVA FUNKTIO VANHALLE 'virhe_logi'-FUNKTIOLLE:
# Jätetään tämä tähän, jotta muiden tiedostojen koodit eivät mene heti rikki!
def virhe_logi(virheviesti, logitiedosto=None):
    """
    Legacy support for the old code structure. Redirects to the new rolling log system.
    """
    log_error(virheviesti)
    return True
