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
cleaner_service.alusta_virheloki("error_log.txt")

# ==============================================================================
# VAIHE 1: Muodosta yhteys (Suojattu token- ja yhteystarkistus)
# ==============================================================================
try:
    palvelu = gmail_service.get_service()
except Exception as virhe:
    print("\n" + "="*80)
    print("[KRIITTINEN YHTEYSVIRHE] Gmail API -tunnistautuminen epäonnistui!")
    print(f"Yksityiskohdat: {virhe}")
    print("-"*80)
    print("Syy on erittäin todennäköisesti vanhentunut tai epäkelpo token.json-tiedosto.")
    print("KORJAUSOHJE: Poista tiedosto 'token.json' projektikansiostasi ja aja ohjelma uudestaan.")
    print("Ohjelma avaa selaimesi automaattisesti uutta tunnistautumista varten.")
    print("="*80 + "\n")
    exit(1) # Suljetaan ohjelma virhekoodilla 1

# 2. Hae viestit
viestit = gmail_service.hae_kaikki_kameran_viestit(palvelu)

# ASETETAAN ERÄKOKO: Kuinka monta viestiä käsitellään tällä yhdellä ajokerralla (esim. 5 viestiä)
era_koko = 300
kasitellyt = 0

# ALOITETAAN SILMUKKA: Käydään viestejä läpi yksitellen muistista
for viesti_info in viestit:
    if kasitellyt >= era_koko:
        print(f"\n[INFO] Eräkoon raja ({era_koko}) saavutettu. Lopetetaan tämän kerran ajo.")
        break
        
    maili_id = viesti_info['id']
    print(f"\n" + "-"*50)
    print(f"[ERÄ] Käsitellään viesti {kasitellyt + 1}/{era_koko} (ID: {maili_id})")
    print("-"*50)

    try:
        # 4. Hae maili ID:llä
        maili = gmail_service.haetaan_seuraava_maili(palvelu, maili_id)
        if not maili:
            continue

        # 5. Hae videon ID mailista
        video_id = gmail_service.haetaan_videon_id(maili)
        if not video_id:
            print("Viestistä puuttui video, siivotaan silti.")
            gmail_service.poista_viesti_gmailista(palvelu, maili_id)
            kasitellyt += 1
            continue

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

        # Tekoäly- ja kansiosiirto-osuus
        if tallenna_polku and os.path.exists(tallenna_polku):
            kuvat = vision_service.ota_kuvakaappaukset(tallenna_polku)
            tunnistukset = vision_service.tunnista_kohteet(kuvat)
            print(f"Tekoälyn havainnot: {tunnistukset}")
            
            if "vieras_ihminen" in tunnistukset or "vieras_auto" in tunnistukset or "vieras_elain" in tunnistukset:
                print("KRIITTINEN HÄLYTYS: Video siirretään arkistoon.")
                shutil.move(tallenna_polku, os.path.join(arkisto_path, os.path.basename(tallenna_polku)))
            else:
                print("Video todettu turhaksi. Siirretään roskakoriin.")
                os.makedirs(delete_path, exist_ok=True)
                shutil.move(tallenna_polku, os.path.join(delete_path, os.path.basename(tallenna_polku)))

        # 14. Sähköpostin lopullinen poisto Gmailista
        gmail_service.poista_viesti_gmailista(palvelu, maili_id)
        kasitellyt += 1

    except Exception as e:
        print(f"Virhe tämän viestin käsittelyssä, hypätään seuraavaan: {e}")
        continue

print(f"\nPääohjelman suoritus päättynyt. Käsiteltiin onnistuneesti {kasitellyt} viestiä!")



