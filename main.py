import os
import json
import gmail_service # Olettaen että get_service on täällä

# Paths
temp_path = r"d:\valvontakamera\temp"
arkisto_path = r"d:\valvontakamera\arkisto"
image_path = r".\image"

# 1. Muodosta yhteys
palvelu = gmail_service.get_service()

# 2. Hae viestit
viestit = gmail_service.hae_kaikki_kameran_viestit(palvelu)

# 3. Tallenna kaikki_viestit json tekstitiedostoon
with open("viestit.json", "w") as f:
    json.dump(viestit, f)

# testing
print("Temp kansio olemassa:", os.path.exists(temp_path))
print("Arkisto kansio olemassa:", os.path.exists(arkisto_path))
print("Image kansio olemassa:", os.path.exists(image_path))