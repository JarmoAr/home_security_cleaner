import cv2
import os
from ultralytics import YOLO
import vision_service
import log_service

def poimi_uusi_nayte(video_polku, kohde_luokka, tallennus_kansio, tiedosto_alku):
    try:
        # 1. Varmistetaan, että kohdekansio on fyysisesti olemassa
        os.makedirs(tallennus_kansio, exist_ok=True)
        
        # 2. Haetaan kuvakaappaukset videosta
        print(f"[SAMPLE] Avataan video näytteenottoa varten: {video_polku}")
        kuvat = vision_service.ota_kuvakaappaukset(video_polku)
        if not kuvat:
            print("[SAMPLE] Videota ei voitu avata tai se on tyhjä.")
            return False

        # 3. Ladataan YOLO-malli
        malli = YOLO("yolov8n.pt")
        
        # 4. Katsotaan kansiosta seuraava vapaa numero
        if os.path.exists(tallennus_kansio):
            olemassa_olevat = [f for f in os.listdir(tallennus_kansio) if f.startswith(tiedosto_alku) and f.endswith('.jpg')]
            seuraava_numero = len(olemassa_olevat) + 1
        else:
            seuraava_numero = 1
        
        print(f"[SAMPLE] Etsitään kohdetta '{kohde_luokka}'. Kansiossa on jo {seuraava_numero-1} kuvaa. Seuraava vapaa numero: {seuraava_numero}")
        
        # 5. Etsitään videolta kohde
        for kuva in kuvat:
            tulokset = malli.predict(source=kuva, verbose=False)
            
            if tulokset:
                tulos = tulokset[0] # Otetaan listan ensimmäinen tulosolio
                
                for box in tulos.boxes:
                    # KORJAUS 1: Käytetään .item()[0] tai .int().item() purkamaan tensori numeroksi!
                    luokka_id = int(box.cls[0].item())
                    nimi = malli.names[luokka_id]
                    
                    if nimi == kohde_luokka:
                        koordinaatit = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist(), list) else box.xyxy.tolist()
                        x1, y1, x2, y2 = map(int, koordinaatit)
                        
                        # 1. Luodaan leikkaus ENSIN, jotta se on olemassa!
                        leikkaus = kuva[y1:y2, x1:x2]
                        
                        if leikkaus.size > 0:
                            # 2. Jos etsitään ihmistä (person), vaaditaan että siitä löytyy myös aitoja kasvoja!
                            if kohde_luokka == 'person':
                                import face_recognition
                                # Muutetaan kuva RGB-muotoon face_recognitionia varten
                                leikkaus_rgb = cv2.cvtColor(leikkaus, cv2.COLOR_BGR2RGB)
                                kasvot = face_recognition.face_encodings(leikkaus_rgb)
                                
                                if len(kasvot) == 0:
                                    print("[SAMPLE] Ihminen löytyi, mutta kasvot eivät näy. Etsitään parempaa kohtaa videolta...")
                                    continue # Hypätään tämän yli ja etsitään parempi kuvakulma videolta!

                            # 3. Jos kasvot löytyivät (tai kyseessä on jokin muu kohde kuten auto/koira), tallennetaan kuva!
                            uusi_nimi = f"{tiedosto_alku}{seuraava_numero}.jpg"
                            lopullinen_polku = os.path.join(tallennus_kansio, uusi_nimi)
                            
                            cv2.imwrite(lopullinen_polku, leikkaus)
                            print(f"[SAMPLE] ONNISTUI! Uusi näyte tallennettu: {lopullinen_polku}")
                            return True
                        
        print(f"[SAMPLE] Videolta ei löytynyt selkeää kohdetta '{kohde_luokka}'.")
        return False

    except Exception as e:
        log_service.virhe_logi(f"Virhe näytteenotossa: {e}", "error_log.txt")
        print(f"[SAMPLE] !!! Virhe: {e}")
        return None


# ==============================================================================
# TÄMÄN VALIKON AVULLA VOIT AJAA TÄTÄ TYÖKALUA KÄSIN
# ==============================================================================
if __name__ == "__main__":
    sample_kansio = r"d:\valvontakamera\sample"
    os.makedirs(sample_kansio, exist_ok=True)
    
    # 1. Haetaan kaikki mp4-videot automaattisesti kansiosta
    videot = [f for f in os.listdir(sample_kansio) if f.endswith(('.mp4', '.avi', '.mkv'))]
    
    if not videot:
        print(f"\n[SAMPLE] Kansio '{sample_kansio}' on tyhjä. Laita sinne ensin valvontakameran videoita!")
        exit()
        
    print(f"\n--- TEKOÄLYN NÄYTEPANKKITYÖKALU ---")
    print(f"Löydetty {len(videot)} videotiedostoa kansiosta {sample_kansio}.\n")
    
    # 2. Käydään videot läpi järjestyksessä yksi kerrallaan
    for i, videon_nimi in enumerate(videot):
        tarkka_polku = os.path.join(sample_kansio, videon_nimi)
        print("="*60)
        print(f"KÄSITELLÄÄN VIDEO {i+1}/{len(videot)}: {videon_nimi}")
        print("="*60)
        
        print("Mitä kohdetta haluat opettaa tästä videosta?")
        print("1 = Auto (car)")
        print("2 = Sinä itse (person)")
        print("3 = Koira (dog)")
        print("0 = Hypää tämän videon yli")
        print("x = Lopeta koko ohjelma")
        
        valinta = input("Valitse toiminto (1-3, 0, x): ")
        
        if valinta == "x" or valinta.lower() == "x":
            print("Lopetetaan ohjelma.")
            break
        elif valinta == "0":
            print(f"Hypätään videon {videon_nimi} yli...\n")
            continue
        elif valinta == "1":
            poimi_uusi_nayte(tarkka_polku, "car", "images/auto", "oma_auto")
        elif valinta == "2":
            poimi_uusi_nayte(tarkka_polku, "person", "images/ihmiset", "tuttu_henkilo")
        elif valinta == "3":
            poimi_uusi_nayte(tarkka_polku, "dog", "images/koira", "oma_koira")
        else:
            print("Virheellinen valinta, hypätään videon yli.\n")
            
    print("\nKaikki videot käyty läpi. Työkalu suljetaan.")
