import os
import cv2
from ultralytics import YOLO
import vision_service
from config import AI_RESULTS_PATH

def analysoi_video_yksitellen(video_polku, tarkistus_kansio):
    videon_perusnimi = os.path.splitext(os.path.basename(video_polku))[0]
    print(f"\n" + "="*60)
    print(f"ANALYSOIDAAN MYSTEERIVIDEO: {os.path.basename(video_polku)}")
    print(f"="*60)

    # 1. Otetaan kuvakaappaukset samalla tavalla kuin aito main.py tekee
    kuvat = vision_service.ota_kuvakaappaukset(video_polku)
    print(f"Video pilkottu {len(kuvat)} kuvakaappaukseen (2 sekunnin välein).")

    # 2. Ladataan YOLO-malli
    malli = YOLO("yolov8n.pt")
    
    # 3. Ajetaan ennustus kuville
    tulokset = malli.predict(source=kuvat, verbose=False, conf=0.55)

    haamuloydokset = False

    # 4. Käydään kuvat ja löydökset läpi erittäin tarkasti aikaleimoittain
    for i, tulos in enumerate(tulokset):
        aika_sekunteina = i * 2
        # Otetaan kopio alkuperäisestä kuvasta piirtämistä varten
        piirros_kuva = kuvat[i].copy()
        kuvaan_piirretty = False
        
        if len(tulos.boxes) > 0:
            for box in tulos.boxes:
                if hasattr(box.cls, 'tolist'):
                    luokat = box.cls.tolist()
                    luokka_id = int(luokat[0]) if luokat else -1
                elif hasattr(box.cls, 'item'):
                    luokka_id = int(box.cls.item())
                else:
                    luokka_id = int(box.cls)
                    
                nimi = malli.names[luokka_id] if luokka_id in malli.names else f"Tuntematon ({luokka_id})"
                varmuus = float(box.conf.item() if hasattr(box.conf, 'item') else box.conf)
                
                print(f"  [Aikaleima {aika_sekunteina:02d}s] --> Havaittu kohde: '{nimi}' ({varmuus*100:.1f}%)")
                haamuloydokset = True
                
                # Haetaan laatikon koordinaatit piirtämistä varten
                if hasattr(box.xyxy, 'tolist'):
                    coords = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist()[0], list) else box.xyxy.tolist()
                else:
                    coords = box.xyxy
                x1, y1, x2, y2 = map(int, coords)

                # Syvät AI-vertailut ja dynaaminen piirtäminen tärkeille kohteille
                if luokka_id == 2 or luokka_id == 7 or nimi in ['car', 'truck']:
                    if vision_service.onko_oma_auto(kuvat, [tulos]):
                        print(f"    └── 🟩 AI-PÄÄTÖS: Kohde on OMA AUTO!")
                        cv2.rectangle(piirros_kuva, (x1, y1), (x2, y2), (0, 255, 0), 2) # Vihreä laatikko omalle autolle
                        cv2.putText(piirros_kuva, f"Oma auto {varmuus*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    else:
                        print(f"    └── 🟥 AI-PÄÄTÖS: VIERAS AJONEUVO!")
                        cv2.rectangle(piirros_kuva, (x1, y1), (x2, y2), (0, 0, 255), 2) # Punainen laatikko vieraalle
                        cv2.putText(piirros_kuva, f"Vieras auto {varmuus*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    kuvaan_piirretty = True

                elif luokka_id == 0 or nimi == 'person':
                    if vision_service.onko_tuttu_henkilo(kuvat):
                        print(f"    └── 🟩 AI-PÄÄTÖS: Kohde on TUTTU IHMINEN!")
                        cv2.rectangle(piirros_kuva, (x1, y1), (x2, y2), (255, 255, 0), 2) # Keltainen tutuille
                    else:
                        print(f"    └── 🟥 AI-PÄÄTÖS: VIERAS TAI TUNNISTAMATON IHMINEN!")
                        cv2.rectangle(piirros_kuva, (x1, y1), (x2, y2), (0, 0, 255), 2) # Punainen laatikko haamulle/vieraalle
                        cv2.putText(piirros_kuva, f"HAAMU IHMINEN {varmuus*100:.0f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    kuvaan_piirretty = True

                elif luokka_id == 16 or nimi == 'dog':
                    if vision_service.onko_oma_koira(kuvat, [tulos]):
                        print(f"    └── 🟩 AI-PÄÄTÖS: Kohde on OMA KOIRA!")
                        cv2.rectangle(piirros_kuva, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    else:
                        print(f"    └── 🟥 AI-PÄÄTÖS: VIERAS ELÄIN!")
                        cv2.rectangle(piirros_kuva, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    kuvaan_piirretty = True

            # Jos kyseisellä sekunnilla piirrettiin jokin tärkeä kohde, tallennetaan kuva levylle katsottavaksi!
            if kuvaan_piirretty:
                kuvan_nimi = f"{videon_perusnimi}_havainto_{aika_sekunteina:02d}s.jpg"
                kuvan_polku = os.path.join(tarkistus_kansio, kuvan_nimi)
                cv2.imwrite(kuvan_polku, piirros_kuva)
                print(f"    [INFO] Kohde piirretty ja tallennettu kuvaan: {kuvan_nimi}")
                
    if not haamuloydokset:
        print("\n[INFO] YOLO ei löytänyt tästä videosta mitään haamuja!")
    print("="*60 + "\n")

if __name__ == "__main__":
    tarkistus_kansio = str(AI_RESULTS_PATH)
    os.makedirs(tarkistus_kansio, exist_ok=True)
    
    videot = [f for f in os.listdir(tarkistus_kansio) if f.endswith(('.mp4', '.avi', '.mkv'))]
    
    if not videot:
        print(f"\n[INFO] Kansio '{tarkistus_kansio}' on tyhjä.")
        exit()
        
    print(f"\n--- VALVONTAKAMEAN AI-TARKISTUSTYÖKALU (VISUAALINEN ANALYYSI) ---")
    print(f"Löydetty {len(videot)} videotiedostoa tarkistettavaksi.\n")
    
    for videon_nimi in videot:
        tarkka_polku = os.path.join(tarkistus_kansio, videon_nimi)
        analysoi_video_yksitellen(tarkka_polku, tarkistus_kansio)
        
    print("Kaikki tarkistettavat videot analysoitu ja havaintokuvat tallennettu!")
