import os
import base64

# Videon dekoodaus
def decode_video(video_data):
    try:
        decoded_video = base64.urlsafe_b64decode(video_data['data'])
        return decoded_video
    except Exception as e:
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
                lopullinen_nimi = tiedostonnimi + str(niminumero) + ".mp4"
                niminumero += 1
                polku_temp = os.path.join(temp_path, lopullinen_nimi)
                polku_arkisto = os.path.join(arkisto_path, lopullinen_nimi)
            else:
                break
        
        return lopullinen_nimi
        
    except Exception as e:
        return None

# Tallenna video temp-kansioon
def tallenna_video(decoded_video, tiedostonnimi, temp_path, arkisto_path):
     tarkista_nimi(tiedostonnimi, temp_path, arkisto_path)