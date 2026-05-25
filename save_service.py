import os
import base64
import log_service

# Videon dekoodaus
def decode_video(video_data):
    try:
        decoded_video = base64.urlsafe_b64decode(video_data['data'])
        return decoded_video
    except Exception as e:
        log_service.virhe_logi(f"Virhe videon dekoodauksessa: {e}", "error_log.txt")
        return None

# tarkistetaan löytyykö saman nimienen tiedosto
def tarkista_nimi(tiedostonnimi, temp_path, arkisto_path):
    try:
        polku_temp = os.path.join(temp_path, tiedostonnimi + ".mp4")
        polku_arkisto = os.path.join(arkisto_path, tiedostonnimi + ".mp4")
        niminumero = 1
        lopullinen_nimi = tiedostonnimi + ".mp4"

        while True:
            if os.path.exists(polku_temp) or os.path.exists(polku_arkisto):
                lopullinen_nimi = tiedostonnimi + "(" + str(niminumero) + ").mp4"
                niminumero += 1
                polku_temp = os.path.join(temp_path, lopullinen_nimi)
                polku_arkisto = os.path.join(arkisto_path, lopullinen_nimi)
            else:
                break
        
        return lopullinen_nimi

    except Exception as e:
        log_service.virhe_logi(f"Virhe tiedoston nimen tarkistuksessa: {e}", "error_log.txt")
        return None

# Tallenna video temp-kansioon , nimen tarkistamiseen tarvitaan temp ja arkisto kansioiden polut
def tallenna_video(decoded_video, tiedostonnimi, temp_path, arkisto_path):
    try:
        lopullinen_nimi = tarkista_nimi(tiedostonnimi, temp_path, arkisto_path)
        polku_temp = os.path.join(temp_path, lopullinen_nimi)
        with open(polku_temp, "wb") as f:
            f.write(decoded_video)
        return polku_temp
    
    except Exception as e:
        return None

# testi osio
if __name__ == "__main__":
    # 1. Luodaan testidataa (feikkibitit)
    testi_bitit = b"Videodataa 123"
    testi_nimi = "20260428_101425"  # Pelkkä aikaleima ilman päätettä
    
    # 2. Määritellään testipolut (voit käyttää r-kirjainta polun edessä)
    t_path = r"d:\valvontakamera\temp"
    a_path = r"d:\valvontakamera\arkisto"
    
    print("Testataan videon tallennusta...")
    # 3. Kutsutaan funktiota
    tulos_polku = tallenna_video(testi_bitit, testi_nimi, t_path, a_path)
    
    if tulos_polku:
        print(f"Onnistui! Tiedosto tallennettu polkuun: {tulos_polku}")
    else:
        print("Tallennus epäonnistui.")