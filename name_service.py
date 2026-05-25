from datetime import datetime
import log_service
from zoneinfo import ZoneInfo

def aikaleiman_muutos(aikaleima):
    try:
       aikaleima = int(aikaleima) / 1000
       uusi_aikaleima = datetime.fromtimestamp(aikaleima).strftime('%Y%m%d_%H%M%S')
       return uusi_aikaleima
    
    except Exception as e:
        log_service.virhe_logi(f"Virhe aikaleiman muunnossa: {e}", "error_log.txt")
        return None

#testi osio
if __name__ == "__main__":
    test_aikaleima = "1777360465000"
    uusi_aikaleima = aikaleiman_muutos(test_aikaleima)
    if uusi_aikaleima:
        print(f"Uusi aikaleima: {uusi_aikaleima}")  
