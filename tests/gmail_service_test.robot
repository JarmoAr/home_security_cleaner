*** Settings ***
Library    ../gmail_service.py
Library    OperatingSystem
Library    ../testiapuri.py
Test Setup    Testin aloitus
Test Teardown    Testin lopetus

*** Variables ***
${temp_path}    ${CURDIR}/test_temp
${arkisto_path}    ${CURDIR}/arkisto_temp

*** Test Cases ***
Testaa seuraavan viesti id hakemisen
    # Tässä testissä tarkistetaan seuraavan_viesti_id-funktion toimivuus.
    # Testataan, että funktio hakee seuraavan viesti id:n odotetulla tavalla.
    # Luodaan kaikki_viestit-lista,  joka sisältää viestit, jossa o viesti ja sillä id on "12345".
    ${maili}    Create Dictionary    id  12345
    @{kaikki_viestit}    Create List    ${maili}
    # Kutsutaan seuraavan_viesti_id-funktiota, joka hakee seuraavan viesti id:n odotetulla tavalla.
    ${tulos}    Seuraava Viesti Id    ${kaikki_viestit} 
    # Varmistetaan, että haettu viesti id on odotettu "12345", koska funktio hakee ensimmäisen viestin id:n listasta.
    Should Be Equal As Strings    ${tulos}    12345

Testaa seuraavan viesti id hakemisen tyhjä data 
    # Tässä testissä tarkistetaan seuraavan_viesti_id-funktion toimivuus.
    # Testataan, että funktio palauttaa None, jos viestejä ei ole.
    @{kaikki_viestit}    Create List     
    ${tulos}    Seuraava Viesti Id    ${kaikki_viestit}
    Should Be Equal    ${tulos}    ${None}

Testaa seuraavan viesti id hakemisen Try Except
    # Tässä testissä tarkistetaan seuraavan_viesti_id-funktion toimivuus try except tilanteessa
    # Testataan, että funktio palauttaa None virheen sattuessa.
    ${maili}    Create Dictionary    jotain  12345
    @{kaikki_viestit}    Create List    ${maili}
    ${tulos}    Seuraava Viesti Id     ${kaikki_viestit}
    Should Be Equal    ${tulos}    ${None}

Testaa haetaan videon id 
    # Tässä testissä tarkistetaan haetaan_videon_id(maili)-funktion toimivuus.
    # Testataan, että funktio hakee seuraavan videon id:n odotetulla tavalla.
    # Luodaan maili 
    ${maili}    Luo Feikkimaili
    # Kutsutaan haetaan_videon_id-funktiota, joka hakee seuraavan videon id:n odotetulla tavalla.
    ${tulos}    Haetaan Videon Id    ${maili} 
    # Varmistetaan, että haettu viesti id on odotettu "12345", koska funktio hakee ensimmäisen viestin id:n listasta.
    Should Be Equal As Strings    ${tulos}    123456

Testaa haetaan videon id hakemisen Try Except
    # Tässä testissä tarkistetaan haetaan_videon_id-funktion toimivuus try except tilanteessa
    # Testataan, että funktio palauttaa None virheen sattuessa.
    ${jotain}    Create Dictionary    attachmentId  123456
    ${maili}    Create Dictionary    jotain  ${jotain}

    ${tulos}    Haetaan Videon Id     ${maili}
    Should Be Equal    ${tulos}    ${None}

Testaa hae aikaleima
    # Tässä testissä tarkistetaan hae_aikaleima(maili)-funktion toimivuus.
    # Testataan, että funktio hakee aikaleiman odotetulla tavalla.
    # Luodaan maili 
    ${maili}    Luo Feikkimaili
    # Kutsutaan hae_aikaleima-funktiota, joka hakee aikaleiman odotetulla tavalla.
    ${tulos}    Hae Aikaleima     ${maili} 
    # Varmistetaan, että haettu aikaleima on odotettu "1672574400000", koska funktio hakee internalDate-kentän arvon mailista.
    Should Be Equal As Strings    ${tulos}    1672574400000

Testaa hae aikaleima Try Except
    # Tässä testissä tarkistetaan hae_aikaleima-funktion toimivuus try except tilanteessa
    # Testataan, että funktio palauttaa None virheen sattuessa.
    ${jotain}    Create Dictionary    attachmentId  123456
    ${maili}    Create Dictionary    jotain  ${jotain}

    ${tulos}    Hae Aikaleima     ${maili}
    Should Be Equal    ${tulos}    ${None}

Testataan haetaan seuraava maili
    # Tässä testissä tarkistetaan def haetaan_seuraava_maili(service, maili_id)-funktion toimivuus.
    # Testataan, että funktio hakee seuraavan mailin odotetulla tavalla.
    # Luodaan kaikki_viestit-lista,  joka sisältää viestit, jossa o viesti ja sillä id on "12345".
    ${maili}    Luo Feikkimaili
    ${feikki_service}    Luo Feikki Service    ${maili}
    # Kutsutaan haetaan_seuraava_maili-funktiota, joka hakee seuraavan mailin odotetulla tavalla.
    ${tulos}    Haetaan Seuraava Maili     ${feikki_service}  12345
    # Varmistetaan, että haettu maili on odotettu maili, koska funktio hakee ensimmäisen mailin listasta.
    Should Be Equal    ${tulos}    ${maili}

Testataan haetaan seuraava maili Try Except Service
    # Tässä testissä tarkistetaan def haetaan_seuraava_maili(service, maili_id)-funktion toimivuus try except tilanteessa
    # Testataan, että funktio palauttaa None virheen sattuessa.
    ${maili}    Luo Feikkimaili
    ${maili_id}    Create Dictionary    id  12345
    @{kaikki_viestit}    Create List    ${maili}
    ${tulos}    Haetaan Seuraava Maili     ${kaikki_viestit}  ${maili_id}
    Should Be Equal    ${tulos}    ${None}

Testataan haetaan video
    # Tässä testissä tarkistetaan def haetaan_video(service, maili_id, video_id):-funktion toimivuus.
    # Testataan, että funktio hakee videon odotetulla tavalla.
    # Luodaan maili
    ${feikkivideo}    Create Dictionary    data=VideoBittia
    ${feikki_service}    Luo Feikki Service    ${feikkivideo}
    # Kutsutaan haetaan_video-funktiota, joka hakee videon odotetulla tavalla.
    ${tulos}    Haetaan Video     ${feikki_service}  12345  123456
    # Varmistetaan, että haettu video on odotettu video, koska funktio hakee videon mailista.
    Should Be Equal    ${tulos}    ${feikkivideo}

Testataan haetaan video Try Except
    # Tässä testissä tarkistetaan def haetaan_video(service, maili_id, video_id):-funktion Try Except -toimivuus.
    # Testataan, että funktio palauttaa None virheen sattuessa.
    ${tulos}    Haetaan Video     ${None}  12345  123456
    # Varmistetaan, että haettu video on odotettu video, koska funktio hakee videon mailista.
    Should Be Equal    ${tulos}    ${None}

Testataan haetaan kaikki kameran viestit
    # Tässä testissä tarkistetaan def hae_kaikki_kameran_viestit(service):-funktion toimivuus.
    # Testataan, että funktio hakee kaikki kameran viestit odotetulla tavalla.
    # Luodaan maili
    ${maili}    Luo Feikkimaili
    @{viestilista}    Create List    ${maili}
    ${feikki_vastaus}    Create Dictionary    messages  ${viestilista}
    ${haun_tulos}    Luo Feikki Service    ${feikki_vastaus}
    # Kutsutaan hae_kaikki_kameran_viestit-funktiota, joka hakee kaikki kameran viestit odotetulla tavalla.
    ${tulos}    Hae Kaikki Kameran Viestit     ${haun_tulos}
    # Varmistetaan, että haettu viestilista on odotettu viestilista, koska funktio hakee kaikki kameran viestit mailista.
    Should Be Equal    ${tulos}    ${viestilista}
   
Testataan haetaan kaikki kameran viestit Try Except
    # Tässä testissä tarkistetaan def hae_kaikki_kameran_viestit(service):-funktion toimivuus.
    # Testataan, että funktio toimii oikein virhe tilanteessa.
    ${tulos}    Hae Kaikki Kameran Viestit     ${None}
    # Varmistetaan, että haettu viestilista on odotettu viestilista, koska funktio hakee kaikki kameran viestit mailista.
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

Luo Feikkimaili    
    # Luodaan maili 
    # mailin alin kerros on body, joka sisältää attachmentId:n "123456".
    # mailin toiseksi alin kerros on partti, joka sisältää filename:n "video.mp4" ja body:n, joka on mailin alin kerros.
    # mailin keskikerros on parts_list, joka on lista, joka sisältää partti-dictionaryn.
    # mailin toiseksi ylin kerros on payload, joka sisältää parts_listin. 
    # mailin ylin kerros on maili, joka sisältää payloadin ja internalDate:n "1672574400000".
    ${body}    Create Dictionary    attachmentId  123456
    ${partti}    Create Dictionary    filename  video.mp4  body  ${body}
    @{parts_list}    Create List    ${partti}
    ${payload}    Create Dictionary    parts  ${parts_list}
    ${maili}    Create Dictionary    payload  ${payload}  internalDate  1672574400000
    RETURN    ${maili}
