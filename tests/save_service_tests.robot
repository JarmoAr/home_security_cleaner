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

Testaa Videon Decoodaus tyhjä data
    # Tässä testissä luodaan feikkidata, joka on tyhjä data.
    # Sitten käytetään Decode Video -funktiota dekoodaamaan se
    # ja tarkistetaan, että saatu tulos on odotettu None kun virhee käskittely laukeaa.
    &{feikkidata}    Create Dictionary
    # Tämä on base64-koodattua dataa, joka vastaa "Koevideo" tekstiä.
    ${tulos}    Decode Video    ${feikkidata}
    # Varmistetaan, että dekoodattu tulos on "Koevideo".
    Should Be Equal As Strings    ${tulos}    None

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


Testaa tallenna video
    # def tallenna_video(decoded_video, tiedostonnimi, temp_path, arkisto_path):
    # tedään oletuspolut, johon videotiedostot tallennetaan.
    ${temp_path}    Set Variable    ${CURDIR}/test_temp
    ${arkisto_path}    Set Variable     ${CURDIR}/arkisto_temp
    # luodaan temp_path ja arkisto_path-kansio, jos se ei vielä ole olemassa.
    Create Directory    ${temp_path}
    Create Directory    ${arkisto_path}
    # tehdään tiedostomuuttuja tallentamista varten
    ${nimi}    Set Variable    video
    # tehdään data joka tallennetaaan,
    ${data}    Set Variable    testidataa§    
    # kutsutaan tallenna_video-funktio, joka tallentaa datan temp_path-kansioon
    ${tulos}    Tallenna Video    ${data}    ${nimi}    ${temp_path}    ${arkisto_path}
    # Varmistetaan, että tallennettu tiedosto on olemassa temp_path-kansiossa.
    File Should Exist    ${temp_path}/video.mp4
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