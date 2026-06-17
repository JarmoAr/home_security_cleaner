from pathlib import Path

# Peruskansio
BASE_DIR = Path.home() / "valvontakamera"

# Pääkansiot
TEMP_PATH = BASE_DIR / "temp"
ARKISTO_PATH = BASE_DIR / "arkisto"
DELETE_PATH = BASE_DIR / "delete_temp"

# Sample_service.py:n kansio
SAMPLE_PATH = BASE_DIR / "sample"

# Katso_havainnot.py:n tarkistettavien videoiden kansio
AI_RESULTS_PATH = BASE_DIR / "ai_results"

# Kaikki kansiot yhdessä listana
ALL_PATHS = [
    TEMP_PATH,
    ARKISTO_PATH,
    DELETE_PATH,
    SAMPLE_PATH,
    AI_RESULTS_PATH,
]

# Kansioiden luonti/varmistus
def luo_kansiot():
    try:
        for path in ALL_PATHS:
            path.mkdir(parents=True, exist_ok=True)
        print("[INFO] Kaikki tarvittavat kansiot on luotu tai ne olivat jo olemassa.")
        return True
    except Exception as e:
        log_service.virhe_logi(f"Virhe luo_kansiot() funktiossa: {e}", "error_log.txt")
        return None

