import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials   
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Tämä funktio hakee Gmail API:n käyttöoikeudet ja palauttaa palveluobjektin, jota voidaan käyttää API-kutsuihin
def get_service():
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

# Tämä funktio hakee Gmail-viestit, jotka sisältävät "Motion Detection for" otsikon, ja tulostaa niiden ID:n, aiheen, lähettäjän ja päivämäärän.
def hae_kaikki_kameran_viestit(service):
    kaikki_viestit = []
    seuraava_sivu = None
    try:
         # Hae viestit, jotka sisältävät "Motion Detection for" otsikon
        while True:

            results = service.users().messages().list(
                userId='me',
                q='subject:"Motion Detection for"',
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

    except HttpError as error:
        print(f"Tapahtui virhe: {error}")
        return []

def seuraava_viesti_id(kaikki_viestit):
    try:
        # tarlostetaam onko viestilista tyhjä, jos on, palautetaan None
        if not kaikki_viestit:
            return None
        # Haetaan ensimmäisen mailin id
        haettava_maili_id = kaikki_viestit[0]['id']

        return haettava_maili_id
    except Exception as e:
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
            seuraava_viesti_id = seuraava_viesti_id(viestilista)
            print(f"Seuraava haettava viestin ID: {seuraava_viesti_id}")
