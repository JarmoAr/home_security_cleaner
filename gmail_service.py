import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials   
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import log_service

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Tämä funktio hakee Gmail API:n käyttöoikeudet ja palauttaa palveluobjektin, jota voidaan käyttää API-kutsuihin
def get_service():
    try:
        # alustetaan creds-muuttuja
        creds = None
        # jos token.json-tiedosto löytyy, ladataan siitä credentials
        if  os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # jos credentials ei ole voimassa, päivitetään se tai luodaan uusi
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        # jos token.json-tiedostoa ei löydy, luodaan uusi credentials
            else:
                # Tämä on se automaattinen tapa, joka avaa selaimen itse
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Ja muista tallentaa se token heti sen jälkeen
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        # palautetaan creds-muuttuja, joka sisältää Gmail API:n käyttöoikeudet
        return build('gmail', 'v1', credentials=creds)   
    except Exception as e:
        log_service.virhe_logi(f"Yhteyden muodostaminen epäonnistui: {e}", "error_log.txt")
        return None

# Tämä funktio hakee Gmail-viestit, jotka sisältävät "Motion Detection for" otsikon, ja tulostaa niiden ID:n, aiheen, lähettäjän ja päivämäärän.
def hae_kaikki_kameran_viestit(service):
    kaikki_viestit = []
    seuraava_sivu = None
    try:
         # Hae viestit, jotka sisältävät "Motion Detection for" otsikon
        while True:
            results = service.users().messages().list(
                userId='me',
                q='"subject:Motion Detection for"',
                pageToken=seuraava_sivu).execute()
            
            # Lisää haetut viestit kaikki_viestit-listaan
            kaikki_viestit.extend(results.get('messages', []))
            
            # Hae seuraavan sivun token, jos se on saatavilla
            seuraava_sivu = results.get('nextPageToken')

            if not seuraava_sivu:
                break
        # käännetään viestilista vanhimmasta uusimpaan
        kaikki_viestit.reverse()
        # Palautetaan kaikki haetut viestit
        return kaikki_viestit

    except Exception as e:
        log_service.virhe_logi(f"Virhe tapahtui haettaessa kaikkia kameran viestejä: {e}", "error_log.txt")
        return None

def seuraava_viesti_id(kaikki_viestit):
    try:
        # tarkastetaan onko viestilista tyhjä, jos on, palautetaan None
        if not kaikki_viestit:
            return None
        # Haetaan ensimmäisen mailin id
        haettava_maili_id = kaikki_viestit[0]['id']
        return haettava_maili_id

    except Exception as e:
        log_service.virhe_logi(f"Virhe seuraavan viestin ID:n hakemisessa: {e}", "error_log.txt")
        return None

def haetaan_seuraava_maili(service, maili_id):
    try:
        maili = service.users().messages().get(userId='me', id=maili_id).execute()
        return maili
    except Exception as e:
        log_service.virhe_logi(f"Virhe seuraavan mailin hakemisessa: {e}", "error_log.txt")
        return None

def haetaan_videon_id(maili):
    try:
        video_id = None
        for part in maili['payload']['parts']:
            # jos tiedostonimi päättyy .mp4, katsotaan sen bodyn dataa ja tulostetaan se
            if part['filename'].endswith('.mp4'):
                video_id = part['body']['attachmentId']
        return video_id

    except Exception as e:
        log_service.virhe_logi(f"Virhe videon ID:n hakemisessa: {e}", "error_log.txt")
        return None
        
def haetaan_video(service, maili_id, video_id):
    try:
        # Hae video dataa Gmail API:lla
        video_data = service.users().messages().attachments().get(
            userId='me',
            messageId=maili_id,
            id=video_id
        ).execute()
        return video_data

    except Exception as e:
        log_service.virhe_logi(f"Virhe videon hakemisessa: {e}", "error_log.txt")
        return None

def hae_aikaleima(maili):
    try:
        aikaleima = maili['internalDate']
        return aikaleima

    except Exception as e:
        log_service.virhe_logi(f"Virhe aikaleiman hakemisessa: {e}", "error_log.txt")
        return None


# Tämä on pääohjelma, joka suoritetaan, kun skripti ajetaan. Se kutsuu get_service-funktiota ja tarkistaa, onnistuiko yhteyden muodostaminen Gmail API:iin.
if __name__ == "__main__":
    # Kutsutaan tekemääsi funktiota
    print("testataan yhteyttä...")
    yhteys = get_service()
    
    if yhteys:
        print("Onnistui! Yhteys muodostettu.")
        
        # Kutsutaan funktiota, joka hakee kameran viestit
        viestilista = hae_kaikki_kameran_viestit(yhteys)

        print(f"VALMIS! Löytyi yhteensä {len(viestilista)} viestiä.")
        if viestilista:
            print(f"Vanhin viestin ID : {viestilista[0]['id']}")
            # Haetaan seuraavan viestin ID funktiolla "seuraava_viesti_id" ja tulostetaan se
            seuraava_viesti_id = seuraava_viesti_id(viestilista)
            print(f"Seuraava haettava viestin ID: {seuraava_viesti_id}")
            # Haetaan seuraava maili funktiolla "haetaan_seuraava_maili" ja tulostetaan sen ID
            haettava_maili = haetaan_seuraava_maili(yhteys, seuraava_viesti_id)
            if haettava_maili:
                print(f"Haettu maili ID: {haettava_maili['id']}")
            else:
                print("Seuraavaa mailia ei löytynyt.")
            
            print(haettava_maili.keys())
            print("**********************************************")
            print(haettava_maili['payload'].keys())
            print("**********************************************")
            for part in haettava_maili['payload']['parts']:
                print(part['filename'])
                print(part['mimeType'])
                print("**********************************************")
            
            # jos tiedostonimi päättyy .mp4, katsotaan sen bodyn dataa ja tulostetaan se
                if part['filename'].endswith('.mp4'):
                    video_id = part['body']['attachmentId']
                    print(f"Video attachment ID: {video_id}")
            
            # Hae video dataa Gmail API:lla
                    video_data = haetaan_video(yhteys, haettava_maili['id'], video_id)
                    if video_data:
                        print("Video data haettu onnistuneesti.")
                    else:
                        print("Videon hakeminen epäonnistui.")
                    hae_aikaleima = hae_aikaleima(haettava_maili)
                    if hae_aikaleima:
                        print(f"Mailin aikaleima: {hae_aikaleima}")