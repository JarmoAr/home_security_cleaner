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
    # tedään oletuspolut, joissa videotiedostot sijaitsevat.
    ${temp_path}    Set Variable    ${CURDIR}/test_temp
    ${arkisto_path}    Set Variable     ${CURDIR}/arkisto_temp
    # tehdään video.mp4-tiedosto temp_path-kansioon, jotta tarkistusfunktio havaitsee sen olemassaolon.
    Create File     ${temp_path}/video.mp4       testidataa
    # määritellään tarkistettava nimi, joka on sama kuin olemassa olevan tiedoston nimi.
    ${nimi}    Set Variable    video    
    # Kutsutaan tarkistusfunktiota, joka tarkistaa, onko nimi jo käytössä temp_path- ja arkisto_path-kansioissa.
    ${tarkistettu_nimi}    Tarkista Nimi    ${nimi}    ${temp_path}    ${arkisto_path}
    # Varmistetaan, että tarkistettu nimi on "video(1).mp4", koska "video.mp4" on jo olemassa.
    Should Be Equal As Strings    ${tarkistettu_nimi}    video(1).mp4
    # Siivotaan testissä luotu tiedosto.
    Remove File    ${temp_path}/video.mp4
    # Varmistetaan, että testissä luotu tiedosto on poistettu.
    File Should Not Exist    ${temp_path}/video.mp4
    # siivotaan testissä luotu arkisto kansio.
    Remove Directory    ${arkisto_path}
    # Varmistetaan, että testissä luotu arkisto kansio on poistettu.
    Directory Should Not Exist    ${arkisto_path}    
    # Siivotaan testissä luotu temp kansio.
    Remove Directory    ${temp_path}    
    # Varmistetaan, että testissä luotu temp kansio on poistettu.
    Directory Should Not Exist    ${temp_path}    



     