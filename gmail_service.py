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
        # KORJAUS: Ei palauteta None, vaan heitetään virhe eteenpäin perusteluineen!
        raise RuntimeError(f"Gmail-yhteys poikki (Tarkista token.json / oikeudet). Alkuperäinen virhe: {e}")


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

def poista_viesti_gmailista(service, maili_id):
    try:
        print(f"[GMAIL] Siirretään viesti {maili_id} roskakoriin tilan vapauttamiseksi...")
        # trash() siirtää viestin Gmailin roskakoriin, josta se tuhoutuu automaattisesti 30 päivän kuluttua
        service.users().messages().trash(userId='me', id=maili_id).execute()
        print(f"[GMAIL] Viesti {maili_id} siirretty onnistuneesti roskakoriin.")
        return True
    except Exception as e:
        log_service.virhe_logi(f"Virhe viestin poistamisessa: {e}", "error_log.txt")
        print(f"[GMAIL] !!! Virhe viestin poistamisessa: {e}")
        return None