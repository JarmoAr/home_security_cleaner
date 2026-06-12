# 🛡️ Älykäs Valvontakamerajärjestelmä & AI-Pururi (Batch Processing)

Tämä sovellus automatisoi valvontakameroiden lähettämien videomeilien hallinnan, analysoinnin ja siivouksen. Järjestelmä vapauttaa dynaamisesti Gmail-tallennustilaa ja suodattaa konenäön (YOLOv8 & Histogrammit & Kasvojentunnistus) avulla pois videot, joissa esiintyy vain asukkaita tai omia ajoneuvoja/eläimiä.

---

## 📋 1. Tavoite ja Logiikka
*   Gmail-tilan vapautus: Sähköpostit ladataan eräajona ja siirretään lennosta Gmailin roskakoriin (Trash), jolloin pilvikapasiteetti vapautuu välittömästi.
*   Dynaaminen kansiohallinta: Videot kulkevat prosessilinjan läpi D-asemalla: Gmail -> temp -> arkisto (jos kriittinen hälytys) tai delete_temp (30 päivän paikallinen roskakori).
*   Monikerroksinen AI-suodatus: Luokitellaan kohteet älykkäästi. Vain vieraat tai tunnistamattomat kohteet aiheuttavat kriittisen hälytyksen ja videon pysyvän arkistoinnin.

---

## 🏗️ 2. Järjestelmän rakenne

### Kansiot ja Sijainnit (D-asema)
*   D:\valvontakamera\temp\ - Paikka, jonne uudet videot ladataan analyysiä varten.
*   D:\valvontakamera\arkisto\ - Pysyvä paikka videoille, joissa on kriittinen hälytys (vieras auto/ihminen).
*   D:\valvontakamera\delete_temp\ - Paikallinen roskakori turhille videoille (automaattinen 30 päivän säilytys).
*   D:\valvontakamera\sample\ - Manuaalinen tai puoliautomaattinen kansio ongelmavideoiden dynaamiseen opettamiseen.

### Tekoälyn mallikuvapankki (Projektikansio)
*   ./images/auto/ - Oman auton referenssikuvakaappaukset dynaamista histogrammianalyysiä varten.
*   ./images/ihmiset/ - Asukkaiden kasvokuvat (face_recognition).
*   ./images/koira/ - Oman koiran (kiinanharjakoira) dynaaminen turkki- ja haalariväripankki.

### Moduulit
1. main.py: Ohjaa prosessia tehokkaana eräajona (Batch processing loop), hallitsee vikasietoisuutta (try-except-suojat) ja suorittaa dynaamisen reitityksen.

2. gmail_service.py: Hallitsee Google API -tunnistautumista, token-virheiden käsittelyä, sähköpostien hakua, videoiden latausta ja viestien poistoa.

3. vision_service.py: Suorittaa monikerroksisen konenäköanalyysin: YOLOv8-kohdetunnistus, 2D-värihistogrammivertailu (BGR2HSV) ja dynaaminen infrapuna-yömooditunnistus (Saturation-keskiarvon seuranta).

4. cleaner_service.py: Suorittaa edellisen ajokerran virhelokin (error_log.txt) dynaamisen alustuksen aikaleimalla ja siivoaa yli 30 päivää vanhat videot paikallisesta roskakorista.

5. name_service.py: Muuntaa sähköpostin sisäiset aikaleimat standardeiksi suomalaisiksi tiedostonimiksi.

6. save_service.py: Dekoodaa Base64-videodatan ja tallentaa sen kiintolevylle varmistaen, etteivät olemassa olevat tiedostot ylikirjoitu (automaattinen numerointi).

7. sample_service.py: Erillinen puoliautomaattinen työkalu, joka etsii dynaamisesti sample-kansion videoista halutut kohteet (car/person/dog) ja leikkaa ne Tensor-muunnoksilla suoraan mallikuvapankkiin.

8. log_service.py: Kirjoittaa keskitetyt virheet lokitiedostoihin.


---

## ⚙️ 3. Työnkulku (Detailed Workflow)

1. Järjestelmän alustus: Ohjelma tyhjentää edellisen ajokerran virhelokin ja leimaa uuden alun aikaleimalla. Paikallinen roskakori siivotaan vanhoista tiedostoista.

2. Yhteys & Token-suoja: Ohjelma tarkistaa Google API -yhteyden. Jos token.json on vanhentunut tai viallinen, se heittää hallitun poikkeuksen ja antaa suomenkieliset korjausohjeet.

3. Eräajon haku: Ohjelma lataa viestit muistiin dynaamisella otsikkohaulla ja prosessoi ne halutussa eräkoossa (esim. 10 viestiä kerralla) säästääkseen API-kyselyrajoja (Rate Limiting).

4. Lataus & Vapautus: Video ladataan temp-kansioon ja sähköposti siirretään heti Gmailin roskakoriin tilan vapauttamiseksi.

5. Dynaaminen AI-Analyysi:
    1. YOLOv8 tunnistaa objektit (auto, ihminen, eläin).
    
    2. Päivämoodi: Jos kuvassa on värejä, auton ja koiran tunnistus käyttää normalisoitua 2D-korrelaatiohistogrammia (värisävy + kylläisyys). Ihmiset tunnistetaan kasvojen piirteistä.
    
    3. Yömoodi (Infrapuna): Jos tekoäly laskee kuvan värikylläisyyden keskiarvoksi lähellä nollaa, järjestelmä vaihtaa lennosta taktiikkaa ja hyväksyy oman auton puhtaasti farmari-suhdeluvun (leveys/korkeus) perusteella.

6. Tiedostoreititys: Jos videolta löytyy "vieras_ihminen" tai "vieras_auto", video lukitaan arkistoon. Jos kohteet ovat tuttuja, video lentää delete_temp-kansioon odottamaan automaattista tuhoa.

---

## 🛠️ 4. Tekniset vaatimukset
*   **Kirjastot:** `google-api-python-client`, `google-auth-oauthlib`, `opencv-python`, `face_recognition`, `ultralytics` (YOLOv8), `numpy`, `shutil`.
*   **Yhteensopivuus:** Kehitetty ja testattu tuotantovalmiiksi Windows-ympäristössä (D-aseman kansiorakenne). Automaattinen testausympäristö (CI) on yhteensopiva Linux-pohjaisen GitHub Actions -pilviajon kanssa.

---

## 🧪 5. Testaus ja Laadunvarmistus (CI/CD)
1. Järjestelmälle on rakennettu kattava automaattinen regressiontestaus Robot Framework -työkalulla.

2. Testit ajetaan eristetyssä GitHub Actions -pilviympäristössä (CI) aina, kun koodia pusketaan Gittiin.

3. Pilviajoa ja OpenCV/YOLO-riippuvuuksia varten järjestelmä käyttää älykästä suojamuuria (testiapuri.py), joka eristää Tensor- ja histogrammilaskennat testiajon ajaksi ilman, että aitoa tuotantokoodia tarvitsee muuttaa.

## Testausmoduulit (30 testitapausta):
1.  `save_service_tests.robot`: Varmistaa Base64-dekoodauksen ja automaattisen tiedostojen numeroinnin.
2.  `gmail_service_test.robot`: Testaa API-rajapinnat ja suojatut viestien haut.
3.  `vision_service_test.robot`: Testaa kasvojentunnistuksen ja kohteiden tunnistamisen suojatut rajapinnat (Run Keyword And Ignore Error).
4.  `name_service_test.robot`: Testaa nimen koostamista tallennettavalle tiedostolle.
5.  `cleaner_service_test.robot`: Testaa dynaamisten lokitiedostojen luonnin, alustuksen sekä vanhojen videoiden automaattisen poiston aikaleimapakotuksilla (Set Modified Time).
6.  `log_service_test.robot`: Testaa tarvittavan logituksen(log_service.py).

---
*Dokumentti päivitetty: 12.6.2026 - Päivitetty eräajot, YOLOv8-logiikka, infrapuna-yömoodi, sample_service-oppimispalvelu sekä dynaamiset virheloki-alustukset.*



