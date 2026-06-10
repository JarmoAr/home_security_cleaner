*** Settings ***
Library    ../cleaner_service.py
Library    OperatingSystem
Library    DateTime
Test Setup    Testin aloitus
Test Teardown    Testin lopetus

*** Variables ***
${temp_path}    ${CURDIR}/test_temp
${arkisto_path}    ${CURDIR}/arkisto_temp

*** Test Cases ***
Testaa siivoa roskakori try except -rakenteella
    # Testataan, että CleanerService-luokan siivoa_roskakori-metodi toimii oikein,
    #  vaikka roskakorin polku ei olisikaan määritettynä.
    # Tämä varmistaa, että metodi käsittelee tilanteen ilman virheitä ja
    #  suorittaa tarvittavat toimenpiteet.
    ${tulos}    Siivoa Roskakori    ${None}
    Should Be Equal    ${tulos}    ${None}

Testaa vanhojen tiedostojen poistaminen roskakorista
    # Testataan, että CleanerService-luokan siivoa_roskakori-metodi
    # poistaa vanhentuneet tiedostot roskakorista.
    # Luodaan testitiedosto joka ei ole vanha,
    #  jotta voidaan varmistaa, että se ei poistu roskakorista.
    Create File    ${temp_path}/uusi_video.mp4
    # Luo testitiedosto roskakoriin, joka on vanhentunut (esim. 31 päivää vanha).
    Create File    ${temp_path}/vanha_video.mp4
    Set Modified Time    ${temp_path}/vanha_video.mp4    2020-01-01 12:00:00   
    # Kutsu siivoa_roskakori-metodia, joka poistaa vanhentuneet tiedostot.
    ${tulos}    Siivoa Roskakori    ${temp_path}    paivia_sailytetään=30
    File Should Exist    ${temp_path}/uusi_video.mp4
    File Should Not Exist    ${temp_path}/vanha_video.mp4

Testaa alusta virheloki
    # Testataan, että CleanerService-luokan alusta_virheloki-metodi luo virhelokin oikein.
    # Kutsu alusta_virheloki-metodia, joka luo virhelokin.
    Alusta Virheloki    ${CURDIR}/testivirhe_log.txt
    # Tarkista, että virheloki on luotu ja se on tyhjä.
    File Should Exist    ${CURDIR}/testivirhe_log.txt
    ${sisalto}    Get File    ${CURDIR}/testivirhe_log.txt
    # varmistetaan että virhelokista löytyy teksti "Virheloki luotu:"
    # joka on alusta_virheloki-metodin kirjoittama teksti, mutta muuten loki on tyhjä.
    Should Contain    ${sisalto}    Virheloki luotu:

Testaa alusta virheloki try except -rakenteella
    # Testataan, että CleanerService-luokan alusta_virheloki-metodi toimii oikein,
    # vaikka virhelokin polku ei olisikaan määritettynä.
    ${tulos}    Alusta Virheloki    ${None}
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

