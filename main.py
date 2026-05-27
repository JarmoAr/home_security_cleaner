import os
import json
import gmail_service 
import save_service
import name_service


# Paths
temp_path = r"d:\valvontakamera\temp"
arkisto_path = r"d:\valvontakamera\arkisto"
image_path = r".\image"

# 1. Muodosta yhteys
palvelu = gmail_service.get_service()

# 2. Hae viestit
viestit = gmail_service.hae_kaikki_kameran_viestit(palvelu)

# 3. Hae ensimmäisen mailin ID
maili_id = gmail_service.seuraava_viesti_id(viestit)
if maili_id is None:
    print("Ei uusia viestejä.")
    exit()

# 4. Hae maili ID:llä
maili = gmail_service.haetaan_seuraava_maili(palvelu, maili_id)

# 5. Hae videon ID mailista
video_id = gmail_service.haetaan_videon_id(maili)

# 6. Hae video dataa Gmail API:lla
video_data = gmail_service.haetaan_video(palvelu, maili_id, video_id)

# 7. Hae aikaleima mailista
aikaleima = gmail_service.hae_aikaleima(maili)

# 8. Muunna aikaleima luettavaan muotoon
uusi_aikaleima = name_service.aikaleiman_muutos(aikaleima)

# 9. Dekoodaa video data
decoded_video = save_service.decode_video(video_data)

# 10. Tallenna video temp-kansioon
tallenna_polku = save_service.tallenna_video(decoded_video, uusi_aikaleima, temp_path, arkisto_path)




# testing
