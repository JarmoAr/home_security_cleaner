# 🛡️ Valvontakameran Videosiivous (Python & AI)

Tämä sovellus automatisoi valvontakameran lähettämien videoiden hallinnan. Se vapauttaa Gmail-tallennustilaa ja suodattaa konenäön avulla pois videot, joissa esiintyy asukkaita tai muita tunnettuja kohteita.

---

## 📋 1. Tavoite ja Logiikka
*   **Gmail-siivous:** Videot ladataan paikallisesti ja poistetaan Gmailista heti, jotta pilvitila ei täyty.
*   **Kansiohallinta:** Videot kulkevat prosessin läpi: `Gmail` -> `temp` -> `arkisto` (tai poisto).
*   **AI-suodatus:** Käytetään useita vertailukuvia (asukkaat/tunnetut henkilöt), joiden perusteella videot luokitellaan turhiksi.

---

## 🏗️ 2. Järjestelmän rakenne

### Kansiot ja Sijainnit
*   **Koodi & Konfiguraatio:** Sijaitsee Git-kloonatussa kansiossa.
    *   `./vertailukuvat/` - Sisältää kuvat (esim. `mina.jpg`, `perhe.jpg`).
    *   `./credentials.json` - Google API-avain.
*   **Videoiden tallennus (D-asema):**
    *   `D:\valvontakamera\temp\` - Paikka, jonne uudet videot ladataan analyysia varten.
    *   `D:\valvontakamera\arkisto\` - Lopullinen paikka videoille, joissa on tuntematon kohde.

### Moduulit
1.  `main.py`: Ohjaa koko prosessia ja hallitsee tiedostojen siirtoja.
2.  `gmail_service.py`: Hoitaa sähköpostien haun (tunnisteella), latauksen ja poiston.
3.  `vision_service.py`: Suorittaa kasvojentunnistuksen ja palauttaa analyysin tuloksen.
4.  `name_service.py`: Hoitaa nimen koostamista tallennettavalle tiedostolle.
5.  `save_service.py`: Hoitaa videon dekoodaamisen ja tallennuksen.
6.  `log_service.py`: Hoitaa tarvittavan logituksen.


---

## ⚙️ 3. Työnkulku (Detailed Workflow)

1.  **Haku ja Työlista:**
    Ohjelma hakee kaikki "kameratunnisteella" löytyvät viestit kerralla hyödyntäen sivutusta (nextPageToken).
    Viestilista käännetään ympäri (reverse), jotta prosessi alkaa vanhimmista viesteistä.
2.  **Lataus:** Video ladataan ja tallennetaan polkuun `D:\valvontakamera\temp\`.
3.  **Vapautus:**  Viesti siirretään Gmailin roskakoriin (Trash) heti onnistuneen latauksen jälkeen pilvitilan vapauttamiseksi.
4.  **AI-Analyysi:** 
    *   Ladataan kaikki kasvot `./vertailukuvat/` -kansioista.
    *   Käydään läpi `temp`-kansion videot.
5.  **Lopullinen sijoitus:**
    *   **Tunnistettu asukas:** Video poistetaan `temp`-kansioista (turha tallenne).
    *   **Tuntematon ihminen:** Video siirretään `D:\valvontakamera\arkisto\` -kansioon.
    *   **Ei ihmistä:** Jos videolla ei ole liikettä tai kasvoja, se poistetaan `temp`-kansiosta.

---

## 🛠️ 4. Tekniset vaatimukset
*   **Kirjastot:** `google-api-python-client`, `opencv-python`, `face_recognition`, `shutil`.
*   **Laitteisto:** Riittävästi tilaa D-asemalla videoiden arkistointiin.
*   **Tunniste:** Käytetään kameran viestien yksilöllistä tunnistetta haun rajaamiseen.

---

## Testaus ja laadunvarmistus
1. Tehdään yksikkötestaus (Unit Testing)
2. Testit ajetaan automaattisena regressiontestauksena (CI) aina, kun koodia pusketaan Gittiin.
3. Testityökaluna Robot Framework ja Github Actions

## Testaus moduulit
1. `save_service_tests.robot`: Hoitaa videon dekoodaamisen ja tallennuksen.

---
*Dokumentti päivitetty: 18.5.2024 - Testau ja laadunvarmistus lisätty.*
