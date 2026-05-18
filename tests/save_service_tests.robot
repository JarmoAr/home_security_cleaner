*** Settings ***
Library    ../save_service.py
Library    OperatingSystem

*** Test Cases ***
Testaa Videon Decoodaus
    # Tässä testissä luodaan feikkidata, joka on base64-koodattua dataa.
    # Sitten käytetään Decode Video -funktiota dekoodaamaan se ja tarkistetaan, että saatu tulos on odotettu.
    &{feikkidata}    Create Dictionary    data=S29ldmlkZW8=
    # Tämä on base64-koodattua dataa, joka vastaa "Koevideo" tekstiä.
    ${tulos}    Decode Video    ${feikkidata}
    # Varmistetaan, että dekoodattu tulos on "Koevideo".
    Should Be Equal As Strings    ${tulos}    Koevideo

Testaa Videon nimen tarkistus
    # Tässä testissä tarkistetaan videon nimen tarkistusfunktio.
    # Testataan, että funktio lisää sulkunumeron jos nimi on jo olemassa.
     