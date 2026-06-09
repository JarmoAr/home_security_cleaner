import os
import cv2
import log_service
import face_recognition
from ultralytics import YOLO

def ota_kuvakaappaukset(video):
    try:
        cap = cv2.VideoCapture(video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps 
        else:
            video_length = 0
        
        kuvakaappaukset = []
        sekunti = 0
        while sekunti < video_length:
            cap.set(cv2.CAP_PROP_POS_MSEC, sekunti * 1000)
            success, kuva = cap.read()
            if success:
                kuvakaappaukset.append(kuva)
            sekunti += 2
        cap.release()
        return kuvakaappaukset
    except Exception as e:
        log_service.virhe_logi(f"Virhe kuvakaappausten ottamisessa: {e}", "error_log.txt")
        return []        

def tunnista_kohteet(kuvakaappaukset):
    try:
        malli = YOLO("yolov8n.pt")
        kohteen_nimi = [] 

        tulokset = malli.predict(source=kuvakaappaukset, verbose=False)

        for i, tulos in enumerate(tulokset):
            for box in tulos.boxes:
                luokka_id = int(box.cls) if hasattr(box.cls, '__getitem__') else int(box.cls.item() if hasattr(box.cls, 'item') else box.cls)
                nimi = malli.names[luokka_id]
                
                lopullinen_leima = None

                if nimi == 'dog':
                    if onko_oma_koira(kuvakaappaukset):
                        lopullinen_leima = "oma_koira"
                    else:
                        lopullinen_leima = "vieras_elain"
                
                elif nimi in ['cat', 'bird', 'horse', 'sheep']:
                    lopullinen_leima = "vieras_elain"

                elif nimi == 'person':
                    if onko_tuttu_henkilo(kuvakaappaukset):
                        lopullinen_leima = "tuttu_ihminen"
                    else:
                        lopullinen_leima = "vieras_ihminen"

                elif nimi in ['car', 'truck']:
                    if onko_oma_auto(kuvakaappaukset, tulokset):
                        lopullinen_leima = "oma_auto"
                    else:
                        lopullinen_leima = "vieras_auto"

                if lopullinen_leima and lopullinen_leima not in kohteen_nimi:
                    kohteen_nimi.append(lopullinen_leima)
        
        return kohteen_nimi
    except Exception as e:
        log_service.virhe_logi(f"Virhe kohteiden tunnistamisessa: {e}", "error_log.txt")
        return []

def onko_oma_koira(kuvakaappaukset):
    try:
        kansio_polku = "images/koira"
        mallikuvat = []
        if os.path.exists(kansio_polku):
            for tiedosto in os.listdir(kansio_polku):
                if tiedosto.endswith((".jpg", ".JPEG", ".png")):
                    mallikuvat.append(os.path.join(kansio_polku, tiedosto))

        malli_encode = []
        for mallikuva in mallikuvat:
            mallikuva = face_recognition.load_image_file(mallikuva)
            mallikuva_encode = face_recognition.face_encodings(mallikuva)
            if len(mallikuva_encode) > 0:
                malli_encode.append(mallikuva_encode[0])

        for kuva in kuvakaappaukset:
            kuva_encofings = face_recognition.face_encodings(kuva)
            for enco in kuva_encofings:
                osumat = face_recognition.compare_faces(malli_encode, enco)
                if True in osumat:
                    return True
        return False
    except Exception as e:
        log_service.virhe_logi(f"Virhe oma-koiran tunnistamisessa: {e}", "error_log.txt")
        return None

def onko_oma_auto(kuvakaappaukset, tulokset_yolo):
    try:
        nykyinen_skripti_polku = os.path.dirname(os.path.abspath(__file__))
        kansion_polku = os.path.join(nykyinen_skripti_polku, "images", "auto")
        
        malli_histogrammit = []
        if os.path.exists(kansion_polku):
            for tiedosto in os.listdir(kansion_polku):
                if tiedosto.endswith(('.jpg', '.jpeg', '.png')):
                    polku = os.path.join(kansion_polku, tiedosto)
                    m_kuva = cv2.imread(polku)
                    
                    if m_kuva is not None:
                        # Mallikuva muutetaan BGR -> HSV
                        m_hsv = cv2.cvtColor(m_kuva, cv2.COLOR_BGR2HSV)
                        # Lasketaan 2D-histogrammi: Kanavat 0 (Sävy) ja 1 (Kylläisyys)
                        hist = cv2.calcHist([m_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                        # Normalisoidaan histogrammi, jotta vertailu on vakaa
                        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                        malli_histogrammit.append(hist)

        print(f"[DEBUG AUTO] Ladattu muistiin yhteensä {len(malli_histogrammit)} mallikuvaa polusta: {kansion_polku}")

        if len(malli_histogrammit) == 0:
            return False

        for i, tulos in enumerate(tulokset_yolo):
            kuva = kuvakaappaukset[i]
            
            for box in tulos.boxes:
                if hasattr(box.cls, 'tolist'):
                    luokat = box.cls.tolist()
                    luokka_id = int(luokat[0]) if luokat else -1
                elif hasattr(box.cls, 'item'):
                    luokka_id = int(box.cls.item())
                else:
                    luokka_id = int(box.cls)
                
                # 2 = car, 7 = truck
                if luokka_id == 2 or luokka_id == 7:
                    if hasattr(box.xyxy, 'tolist'):
                        coords = box.xyxy.tolist()[0] if isinstance(box.xyxy.tolist()[0], list) else box.xyxy.tolist()
                    else:
                        coords = box.xyxy
                    
                    x1, y1, x2, y2 = map(int, coords)
                    leveys = x2 - x1
                    korkeus = y2 - y1
                    
                    if korkeus > 0:
                        suhdeluku = leveys / korkeus
                    else:
                        suhdeluku = 0

                    auton_alue = kuva[y1:y2, x1:x2]
                    if auton_alue.size == 0:
                        continue
                        
                    # SYNKRONOINTI: Myös videon kuva muutetaan täysin samalla tavalla BGR -> HSV!
                    video_hsv = cv2.cvtColor(auton_alue, cv2.COLOR_BGR2HSV)
                    video_hist = cv2.calcHist([video_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                    cv2.normalize(video_hist, video_hist, 0, 1, cv2.NORM_MINMAX)
                    
                    for m_hist in malli_histogrammit:
                        osuma_tarkkuus = cv2.compareHist(m_hist, video_hist, cv2.HISTCMP_CORREL)
                        
                        print(f"[DEBUG AUTO] Muoto (suhdeluku): {suhdeluku:.2f}, Väriosuma: {osuma_tarkkuus:.2f}")
                        
                        # Kynnysarvo: Muoto kunnossa ja värit kohtaavat yli 45-prosenttisesti (0.45)
                        if suhdeluku > 1.2 and osuma_tarkkuus > 0.45:
                            return True 
                            
        return False
    except Exception as e:
        print(f"[DEBUG AUTO] !!! KRIITTINEN VIRHE FUNKTION SISÄLLÄ !!!: {e}")
        log_service.virhe_logi(f"Virhe oman auton tunnistamisessa: {e}", "error_log.txt")
        return None


def onko_tuttu_henkilo(kuvakaappaukset):
    try:
        kansio_polku = "images/ihmiset"
        mallikuvat = []
        if os.path.exists(kansio_polku):
            for tiedosto in os.listdir(kansio_polku):
                if tiedosto.endswith((".jpg", ".JPEG", ".png")):
                    mallikuvat.append(os.path.join(kansio_polku, tiedosto))

        malli_encode = []
        for mallikuva in mallikuvat:
            mallikuva = face_recognition.load_image_file(mallikuva)
            mallikuva_encode = face_recognition.face_encodings(mallikuva)
            if len(mallikuva_encode) > 0:
                malli_encode.append(mallikuva_encode[0])

        for kuva in kuvakaappaukset:
            kuva_encofings = face_recognition.face_encodings(kuva)
            for enco in kuva_encofings:
                osumat = face_recognition.compare_faces(malli_encode, enco)
                if True in osumat:
                    return True
        return False
    except Exception as e:
        log_service.virhe_logi(f"Virhe ihmisen tunnistamisessa: {e}", "error_log.txt")
        return None
