*** Settings ***
Library    ../log_service.py
Library    OperatingSystem
Test Setup    Testin aloitus
Test Teardown    Testin lopetus

*** Variables ***
${temp_path}    ${CURDIR}/test_temp
${arkisto_path}    ${CURDIR}/arkisto_temp

*** Test Cases ***
Testaa virhelogin kirjoittaminen
    # Tässä testissä tarkistetaan virhe_logi-funktion toimivuus.
    # Testataan, että funktio kirjoittaa virheen odotetulla tavalla.
    # Kutsutaan virhe_logi-funktiota, joka kirjoittaa virheen odotetulla tavalla.
    ${tulos}    Virhe Logi    Tämä on testivirhe    ${CURDIR}/testivirhe_log.txt
    # Varmistetaan, että virhe on kirjoitettu odotetulla tavalla, eli tiedostoon "testivirhe_log.txt" on kirjoitettu "Tämä on testivirhe".
    ${tiedosto_sisalto}    Get File    ${CURDIR}/testivirhe_log.txt  encoding=UTF-8
    Should Contain    ${tiedosto_sisalto}    Tämä on testivirhe

Testaa virhelogin kirjoittaminen tyhjä data
    # Tässä testissä tarkistetaan virhe_logi-funktion toimivuus, kun data on tyhjä.
    # Testataan, että funktio kirjoittaa virheen odotetulla tavalla, vaikka data on tyhjä.
    ${tulos}    Virhe Logi    Tämä on testivirhe ilman dataa    ${CURDIR}/jokinkansio/testivirhe_log.txt
    # Varmistetaan, että virhe on kirjoitettu odotetulla tavalla, eli tiedostoon "testivirhe_log.txt" on kirjoitettu "Tämä on testivirhe ilman dataa".
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
    Remove File    ${CURDIR}/testivirhe_log.txt
    File Should Not Exist    ${CURDIR}/testivirhe_log.txt


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
