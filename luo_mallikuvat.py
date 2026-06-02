import cv2
import os
from ultralytics import YOLO
import vision_service  # Tuodaan vision_service -tiedosto, jotta saadaan ota_kuvakaappaukset käyttöön

def poimi_auton_kuvat(video_polku):
    try:
        print(f"Avataan video: {video_polku}...")
        # 1. Käytetään ota_kuvakaappaukset -funktiota ottamaan kuvakaappaukset videosta
        kuvat = vision_service.ota_kuvakaappaukset(video_polku)
        
        if not kuvat:
            print("Videolta puuttuu kuvakaappaukset tai videota ei voitu avata.")
            return

        print(f"Saatiin {len(kuvat)} kuvakaappausta. Etsitään autoa...")
        malli = YOLO("yolov8n.pt")
        
        kuva_numero = 1
        # 2. Käydään kuvat läpi ja etsitään auto
        for kuva in kuvat:
            # Otetaan vain 3 parasta mallikuvaa talteen
            if kuva_numero > 3:
                break
                
            tulokset = malli.predict(source=kuva, verbose=False)
            
            for box in tulokset[0].boxes:
                luokka_id = int(box.cls[0])
                # Jos tekoäly löytää auton
                if malli.names[luokka_id] == 'car':
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Leikataan auton kuva-alue irti
                    auton_leikkaus = kuva[y1:y2, x1:x2]
                    
                    if auton_leikkaus.size > 0:
                        tiedoston_nimi = f"oma_auto{kuva_numero}.jpg"
                        # Tallennetaan leikattu kuva levylle
                        cv2.imwrite(tiedoston_nimi, auton_leikkaus)
                        print(f"Tallennettu onnistuneesti: {tiedoston_nimi}")
                        kuva_numero += 1
                        break # Siirrytään seuraavaan kuvakaappaukseen, jotta saadaan eri kohdista videota kuvat
                        
        if kuva_numero > 3:
            print("Kaikki 3 dynaamista mallikuvaa luotu onnistuneesti!")
        else:
            print(f"Löydettiin vain {kuva_numero - 1} auton kuvaa. Tarvitaan lisää materiaalia videolta.")

    except Exception as e:
        print(f"Virhe skriptin ajossa: {e}")

if __name__ == "__main__":
    # HUOM: Vaihda tähän alle sen sinun oman autovideosi tarkka nimi tai tiedostopolku!
    autovideo = r"D:\valvontakamera\temp\01_20260602142644216.mp4"
    poimi_auton_kuvat(autovideo)
