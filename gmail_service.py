import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials   
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=False)
    # tallennetaan credentials token.json-tiedostoon
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    # palautetaan creds-muuttuja, joka sisältää Gmail API:n käyttöoikeudet
    return creds    

if __name__ == "__main__":
    # Kutsutaan tekemääsi funktiota
    print("testataan yhteyttä...")
yhteys = get_service()
    
if yhteys:
    print("Onnistui! Yhteys muodostettu.")