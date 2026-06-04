*** Settings ***
Library    ../testiapuri.py
Library    ../vision_service.py


*** test cases ***
Testaa ota kuvankaappaukset try except
    # Tässä testissä tarkistetaan, että ota kuvankaappaukset -funktion 
    # try except toimii odotetusti.
    
    ${tulos}    vision_service.Ota Kuvakaappaukset    ${None}
    # Varmistetaan, että kuvankaappaukset on tallennettu oikeaan paikkaan.
    Should Be Empty    ${tulos}

Testaa onko tuttu henkilö try except
    # Tässä testissä tarkistetaan, että onko tuttu henkilö -funktion 
    # try except toimii odotetusti.
    
    ${tulos}    vision_service.Onko Tuttu Henkilo    ${None}
    # Varmistetaan, että funktio palauttaa odotetun tuloksen.
    Should Be Equal    ${tulos}    ${None}

Testaa kohteiden tunnistaminen
    # Tässä testissä tarkistetaan, että kohteiden tunnistaminen -funktion 
    # toimii odotetusti.
    # Luodaan feikkikuva testiapurin luo_feikkikuva -funktiolla.
    ${kuva}    testiapuri.luo_feikkikuva  
    @{feikkikuvat}    Create List    ${kuva}

    # Kutsutaan tunnista kohteet -funktiota
    ${tulos}    vision_service.Tunnista Kohteet    ${feikkikuvat}
    # Varmistetaan, että funktio palauttaa odotetun tuloksen.
    # Luodaan odotettu lista, joka sisältää vain "vieras_auto", koska funktio on mokattu palauttamaan sen.
    @{odotettu}    Create List    vieras_auto
    Should Be Equal    ${tulos}    ${odotettu}
