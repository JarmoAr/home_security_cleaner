*** Settings ***
Library    ../save_service.py
Library    OperatingSystem
Test Setup    Testin aloitus
Test Teardown    Testin lopetus

*** Variables ***
${temp_path}    ${CURDIR}/test_temp
${arkisto_path}    ${CURDIR}/arkisto_temp

*** Test Cases ***
Testaa Videon Decoodaus
    # Tässä testissä luodaan feikkidata, joka on base64-koodattua dataa.
    # Oletpolut on tehty varibles kohdassa ja kansiot luodaan settings kohdassa.
    # Test Setup käskyttää Testin aloitus -funktiota,
    # joka luo temp_path ja arkisto_path-kansiot ennen testin suoritusta ja tarkistaa,
    # että ne on luotu onnistuneesti. 
    # Lopuksi Test Teardown käskyttää Testin lopetus -funktiota,
    # joka poistaa temp_path ja arkisto_path-kansiot testin suorituksen jälkeen
    # ja tarkistaa, että ne on poistettu onnistuneesti.

    # Sitten käytetään Decode Video -funktiota dekoodaamaan se ja tarkistetaan, että saatu tulos on odotettu.
    &{feikkidata}    Create Dictionary    data=S29ldmlkZW8=
    # Tämä on base64-koodattua dataa, joka vastaa "Koevideo" tekstiä.
    ${tulos}    Decode Video    ${feikkidata}
    # Varmistetaan, että dekoodattu tulos on "Koevideo".
    Should Be Equal As Strings    ${tulos}    Koevideo
    

Testaa Videon Decoodaus tyhjä data try except
    # Tässä testissä luodaan feikkidata, joka on tyhjä data.
    # Sitten käytetään Decode Video -funktiota dekoodaamaan se
    # ja tarkistetaan, että saatu tulos on odotettu None kun virhee käskittely laukeaa.

    # Tehdään feikkidata, joka on tyhjä data.
    &{feikkidata}    Create Dictionary
    # Tämä on base64-koodattua dataa, joka vastaa "Koevideo" tekstiä.
    ${tulos}    Decode Video    ${feikkidata}
    # Varmistetaan, että dekoodattu tulos on "None".
    Should Be Equal    ${tulos}    ${None}

Testaa Videon nimen tarkistus
    # Tässä testissä tarkistetaan videon nimen tarkistusfunktio.
    # Testataan, että funktio lisää sulkunumeron jos nimi on jo olemassa.
     # tehdään video.mp4-tiedosto temp_path-kansioon, jotta tarkistusfunktio havaitsee sen olemassaolon.
    Create File     ${temp_path}/video.mp4       testidataa
    # määritellään tarkistettava nimi, joka on sama kuin olemassa olevan tiedoston nimi.
    ${nimi}    Set Variable    video    
    # Kutsutaan tarkistusfunktiota, joka tarkistaa, onko nimi jo käytössä temp_path- ja arkisto_path-kansioissa.
    ${tarkistettu_nimi}    Tarkista Nimi    ${nimi}    ${temp_path}    ${arkisto_path}
    # Varmistetaan, että tarkistettu nimi on "video(1).mp4", koska "video.mp4" on jo olemassa.
    Should Be Equal As Strings    ${tarkistettu_nimi}    video(1).mp4  

Testaa Videon nimen tarkistus tyhjä nimi try except
    # Tässä testissä tarkistetaan videon nimen tarkistusfunktio.
    # Testataan, että funktio lisää sulkunumeron jos nimi on jo olemassa.

    # tehdään video.mp4-tiedosto temp_path-kansioon, jotta tarkistusfunktio havaitsee sen olemassaolon.
    Create File     ${temp_path}/video.mp4       testidataa
    # määritellään tarkistettava nimi, joka on sama kuin olemassa olevan tiedoston nimi.
    ${nimi}    Set Variable    ${None}
    # Kutsutaan tarkistusfunktiota, joka tarkistaa, onko nimi jo käytössä temp_path- ja arkisto_path-kansioissa.
    ${tarkistettu_nimi}    Tarkista Nimi    ${nimi}    ${temp_path}    ${arkisto_path}
    # Varmistetaan, että tarkistettu nimi on "video(1).mp4", koska "video.mp4" on jo olemassa.
    Should Be Equal    ${tarkistettu_nimi}    ${None}

Testaa tallenna video
    # def tallenna_video(decoded_video, tiedostonnimi, temp_path, arkisto_path):
    # tehdään tiedostomuuttuja tallentamista varten
    ${nimi}    Set Variable    video
    # tehdään data joka tallennetaaan,
    ${data}    Set Variable    testidataa    
    # kutsutaan tallenna_video-funktio, joka tallentaa datan temp_path-kansioon
    ${tulos}    Tallenna Video    ${data}    ${nimi}    ${temp_path}    ${arkisto_path}
    # Varmistetaan, että tallennettu tiedosto on olemassa temp_path-kansiossa.
    File Should Exist    ${temp_path}/video.mp4

Testaa tallenna video vihjeellinen syöte try except
    # def tallenna_video(decoded_video, tiedostonnimi, temp_path, arkisto_path):
    # tehdään tiedostomuuttuja tallentamista varten
    ${nimi}    Set Variable    video
    # tehdään data joka tallennetaaan,
    ${data}    Set Variable     ${None}   
    # kutsutaan tallenna_video-funktio, joka tallentaa datan temp_path-kansioon
    ${tulos}    Tallenna Video    ${data}    ${nimi}    ${temp_path}    ${arkisto_path}
    # Varmistetaan, että tallennettu tiedosto on olemassa temp_path-kansiossa.
    Should Be Equal    ${tulos}    ${None}

*** Keywords ***
Luo kansiot
    Create Directory    ${temp_path}
    Create Directory    ${arkisto_path}

Poista kansiot
    Remove Directory    ${temp_path}    RECURSIVE=True   # RECURSIVE=True -parametri varmistaa, että kansio ja sen sisältö poistetaan kokonaan.
    Remove Directory    ${arkisto_path}    RECURSIVE=True  # RECURSIVE=True -parametri varmistaa, että kansio ja sen sisältö poistetaan kokonaan.

Tarkista että kansiot on luotu
    Directory Should Exist    ${temp_path}
    Directory Should Exist    ${arkisto_path}

Tarkista että kansiot on poistettu
    Directory Should Not Exist    ${temp_path}
    Directory Should Not Exist    ${arkisto_path}

Testin aloitus
    # Tehdään oletuspolut, joissa videotiedostot sijaitsevat ja tarkistetaan, että ne on luotu.
    Luo kansiot
    Tarkista että kansiot on luotu

Testin lopetus
    # Siivotaan testissä luodut kansiot ja tarkistetaan, että ne on poistettu.
    Poista kansiot
    Tarkista että kansiot on poistettu

    
