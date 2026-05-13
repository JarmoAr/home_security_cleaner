import os
from datetime import datetime

def virhe_logi(virheviesti, logitiedosto):
    try:
        with open(logitiedosto, "a") as f:
            aikaleima = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{aikaleima} - {virheviesti}\n")
        return True
    except Exception as e:
        return False