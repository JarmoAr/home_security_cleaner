import cv2
import os
from ultralytics import YOLO
import vision_service

def poimi_kaikki_mallikuvat(video_polku):
    try:
        # Varmistetaan, että suojatut kansiot ovat fyysisesti olemassa
        os.makedirs("images/ihmiset", exist_ok=True)
        os.makedirs("images/koira", exist_ok=True)
        
        print(f"Avataan yhteisvideo: {video_polku}...")
        kuvat = vision_service.ota_kuvakaappaukset(video_polku)
        
        if not kuvat:
            print("Videota ei voitu avata tai kuvakaappaukset puuttuvat.")
            return

        print(f"Saatiin {len(kuvat)} kuvakaappausta. Etsitään sinua ja koiraa...")
        malli = YOLO("yolov8n.pt")
        
        ihmis_nro = 1
        koira_nro = 1
        
        for kuva in kuvat:
            tulokset = malli.predict(source=kuva, verbose=False)
            
            for box in tulokset[0].boxes:
                luokka_id = int(box.cls[0])
                nimi = malli.names[luokka_id]
                
                # 1. POIMITAAN IHMISEN KASVOT / HAHMO (tuttu_henkilo)
                if nimi == 'person' and ihmis_nro <= 3:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    leikkaus = kuva[y1:y2, x1:x2]
                    if leikkaus.size > 0:
                        polku = f"images/ihmiset/tuttu_henkilo{ihmis_nro}.jpg"
                        cv2.imwrite(polku, leikkaus)
                        print(f"Tallennettu: {polku}")
                        ihmis_nro += 1
                        
                # 2. POIMITAAN KOIRAN HAHMO (oma_koira)
                elif nimi == 'dog' and koira_nro <= 3:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    leikkaus = kuva[y1:y2, x1:x2]
                    if leikkaus.size > 0:
                        polku = f"images/koira/oma_koira{koira_nro}.jpg"
                        cv2.imwrite(polku, leikkaus)
                        print(f"Tallennettu: {polku}")
                        koira_nro += 1
                        
        print(f"\nValmis! Poimittu {ihmis_nro-1} ihmiskuvaa ja {koira_nro-1} koirankuvaa.")

    except Exception as e:
        print(f"Virhe poiminnassa: {e}")

if __name__ == "__main__":
    # HUOM: Laita tähän alle sen sinun yhteisvideosi tarkka polku ja nimi!
    yhteis_video = r"D:\valvontakamera\temp\01_20260602142110215.mp4" 
    poimi_kaikki_mallikuvat(yhteis_video)
