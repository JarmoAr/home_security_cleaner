*** Settings ***
Library    ../vision_service.py
Library    ../testiapuri.py

*** test cases ***
Testaa ota kuvankaappaukset try except
    # Tässä testissä tarkistetaan, että ota kuvankaappaukset -funktion 
    # try except toimii odotetusti.
    
    ${tulos}    vision_service.Ota Kuvakaappaukset    ${None}
    # Varmistetaan, että kuvankaappaukset on tallennettu oikeaan paikkaan.
    Should Be Empty    ${tulos}