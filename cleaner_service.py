import os
import log_service
from datetime import datetime, timedelta

def siivoa_roskakori(roskakori_polku, paivia_sailytetään=30):
    try:
        # 1. Varmistetaan ensin, että kansio on edes olemassa
        if not os.path.exists(roskakori_polku):
            return True
            
        # 2. Haetaan tämän hetkinen aika
        nyt = datetime.now()
        
        # 3. Käydään läpi kaikki kansion tiedostot
        for tiedoston_nimi in os.listdir(roskakori_polku):
            full_path = os.path.join(roskakori_polku, tiedoston_nimi)
            
            # Varmistetaan, että kyseessä on tiedosto eikä alikansio
            if os.path.isfile(full_path):
                # Haetaan tiedoston viimeisin muokkausaika kiintolevyllä
                muokkausaika_timestamp = os.path.getmtime(full_path)
                muokkausaika = datetime.fromtimestamp(muokkausaika_timestamp)
                
                # Lasketaan tiedoston ikä päivissä
                ika = nyt - muokkausaika
                
                # 4. Jos ikä on suurempi kuin sallittu määrä (esim. 30 päivää)
                if ika.days >= paivia_sailytetään:
                    os.remove(full_path)
                    print(f"Poistettu vanha video lopullisesti: {tiedoston_nimi}")
                    
        return True
    except Exception as e:
        log_service.virhe_logi(f"Virhe roskakorin siivouksessa: {e}", "error_log.txt")
        return None
