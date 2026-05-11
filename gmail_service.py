import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials   
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
def hae_kameran_viestit(service):
        try:
            # Hae viestit, jotka sisältävät "Motion Detection for" otsikon
            results = service.users().messages().list(userId='me', q='subject:"Motion Detection for"').execute()
            messages = results.get('messages', [])

            if not messages:
                print("Ei löytynyt viestejä.")
                return

            print(f"Löytyi {len(messages)} viestit.")
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(f"Viestin ID: {msg['id']}")
                print(f"Viestin aihe: {msg['payload']['headers'][0]['value']}")
                print(f"Viestin lähettäjä: {msg['payload']['headers'][1]['value']}")
                print(f"Viestin päivämäärä: {msg['payload']['headers'][2]['value']}")
                print("----")
        except HttpError as error:
            print(f"Tapahtui virhe: {error}")

# Tämä on pääohjelma, joka suoritetaan, kun skripti ajetaan. Se kutsuu get_service-funktiota ja tarkistaa, onnistuiko yhteyden muodostaminen Gmail API:iin.
if __name__ == "__main__":
    # Kutsutaan tekemääsi funktiota
    print("testataan yhteyttä...")
    yhteys = get_service()
    
    if yhteys:
        print("Onnistui! Yhteys muodostettu.")
        # Kutsutaan funktiota, joka hakee kameran viestit
        hae_kameran_viestit(yhteys)