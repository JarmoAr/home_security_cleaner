*** Settings ***
Library    ../name_service.py
Library    OperatingSystem
Test Setup    Testin aloitus
Test Teardown    Testin lopetus

*** Variables ***
${temp_path}    ${CURDIR}/test_temp
${arkisto_path}    ${CURDIR}/arkisto_temp

*** Test Cases ***
Testaa aikaleiman muutos
    # Tässä testissä tarkistetaan aikaleiman_muutos-funktion toimivuus.
    # Testataan, että funktio muuttaa aikaleiman odotetulla tavalla.

    # Määritellään testattava aikaleima, joka on "2023.01.01_14:00:00" ja unix-aikaleima on 1672574400000.
    ${aikaleima}    Set Variable    1672574400000
    # Kutsutaan aikaleiman_muutos-funktiota, joka muuttaa aikaleiman odotetulla tavalla.
    ${tulos}    Aikaleiman Muutos    ${aikaleima}
    # Varmistetaan, että muutettu aikaleima on odotettu "2023-01-01 13:00:00", koska funktio lisää tunnin aikaleimaan.
    Should Be Equal As Strings    ${tulos}    20230101_140000 

Testaa aikaleiman muutos tyhjä data try except
    # Tässä testissä tarkistetaan aikaleiman_muutos-funktion toimivuus.
    # Testataan, että funktio muuttaa aikaleiman odotetulla tavalla.

    # Määritellään testattava aikaleima, joka on "2023.01.01_14:00:00".
    ${aikaleima}    Set Variable    2023.01.01_14:00:00
    # Kutsutaan aikaleiman_muutos-funktiota, joka muuttaa aikaleiman odotetulla tavalla.
    ${tulos}    Aikaleiman Muutos    ${aikaleima}
    # Varmistetaan, että muutettu aikaleima on odotettu "2023-01-01 13:00:00", koska funktio lisää tunnin aikaleimaan.
    Should Be Equal     ${tulos}    ${None}

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

    
