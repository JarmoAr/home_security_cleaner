import os
import json
import shutil
import gmail_service 
import save_service
import name_service
import vision_service
import cleaner_service

# Paths
temp_path = r"d:\valvontakamera\temp"
arkisto_path = r"d:\valvontakamera\arkisto"
delete_path = r"d:\valvontakamera\delete_temp"

# 0. Automaattinen vanhojen videoiden siivous roskakorista
print("Suoritetaan roskakorin ylläpitovoitelu...")
cleaner_service.siivoa_roskakori(delete_path, paivia_sailytetään=30)

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

# Tekoälyanalyysi ja automaattinen päätöksenteko
if tallenna_polku and os.path.exists(tallenna_polku):
    print(f"Video tallennettu polkuun: {tallenna_polku}. Aloitetaan tekoälyajo...")
    
    # 11. Otetaan videosta kuvakaappaukset muistiin
    kuvat = vision_service.ota_kuvakaappaukset(tallenna_polku)
    
    # 12. Ajetaan tekoälytunnistus (YOLO + Mallikuvakansiot)
    tunnistukset = vision_service.tunnista_kohteet(kuvat)
    print(f"Tekoälyn havainnot videolta: {tunnistukset}")
    
    # 13. PÄÄTÖKSENTEKO: Mitä videolle tehdään?
    # Jos tekoäly huomasi jotain vierasta tai mahdollisesti vaarallista:
    if "vieras_ihminen" in tunnistukset or "vieras_auto" in tunnistukset or "vieras_elain" in tunnistukset:
        print("KRIITTINEN HÄLYTYS: Vieras kohde havaittu pihassa! Video jätetään arkistoon.")
        # Tähän voidaan tulevaisuudessa liittää esim. kännykkäilmoituksen lähetys
        shutil.move(tallenna_polku, os.path.join(arkisto_path, os.path.basename(tallenna_polku)))

    # Jos videolla näkyi VAIN jotain tuttua (kuten oma auto) eikä mitään vaarallista:
    else:
        print("Video todettu turhaksi (vain tuttua dataa). Siirretään roskakoriin 30 päiväksi.")
        # Varmistetaan, että delete_temp kansio on olemassa lennossa
        os.makedirs(delete_path, exist_ok=True)
        # Siirretään video temp-kansiosta roskakoriin
        shutil.move(tallenna_polku, os.path.join(delete_path, os.path.basename(tallenna_polku)))

print("Pääohjelman suoritus päättynyt onnistuneesti!")



