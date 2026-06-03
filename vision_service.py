import cv2
import log_service
import face_recognition
from ultralytics import YOLO

def ota_kuvakaappaukset(video):
    try:
        # Avaa video
        cap = cv2.VideoCapture(video)
        # haetaa videon fps
        fps = cap.get(cv2.CAP_PROP_FPS)
        # haetaan videon pituus sekunteina
        if fps > 0:
            video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps 
        else:
            video_length = 0
        
        # Haetaan kuvakaappaukset joka 2 sekunti
        kuvakaappaukset = []
        sekunti = 0
        while sekunti < video_length:
            # Asetetaan videon lukupiste
            cap.set(cv2.CAP_PROP_POS_MSEC, sekunti * 1000)
            # Luetaan kuva
            success, kuva = cap.read()
            if success:
                kuvakaappaukset.append(kuva)
            sekunti += 2
        # Sulje video
        cap.release()
        return kuvakaappaukset

    except Exception as e:
        log_service.virhe_logi(f"Virhe kuvakaappausten ottamisessa: {e}", "error_log.txt")
        return []        

def tunnista_kohteet(kuvakaappaukset):
    try:
        malli = YOLO("yolov8n.pt")
        kohteen_nimi = [] 

        # 1. Ajetaan YOLO-ennustus kaikille kuvakaappauksille kerralla
        # (Näin säästetään tehoja, kun mallia ei kutsuta monta kertaa)
        tulokset = malli.predict(source=kuvakaappaukset)

        # 2. Käydään läpi kunkin kuvan löydökset
        for i, tulos in enumerate(tulokset):
            for box in tulos.boxes:
                luokka_id = int(box.cls[0])
                nimi = malli.names[luokka_id]
                
                lopullinen_leima = None

                # Jos löytyy koira, tarkistetaan onko oma koira
                if nimi == 'dog':
                    if onko_oma_koira(kuvakaappaukset):
                        lopullinen_leima = "oma_koira"
                    else:
                        lopullinen_leima = "vieras_elain"
                
                # Jos löytyy muu yleinen eläin (kissa, lintu jne.)
                elif nimi in ['cat', 'bird', 'horse', 'sheep']:
                    lopullinen_leima = "vieras_elain"

                # Jos löytyy ihminen, tarkistetaan onko tuttu
                elif nimi == 'person':
                    if onko_tuttu_henkilo(kuvakaappaukset):
                        lopullinen_leima = "tuttu_ihminen"
                    else:
                        lopullinen_leima = "vieras_ihminen"

                # Jos löytyy auto, kutsutaan sitä sinun uutta hienoa funktiotasi!
                elif nimi in ['car', 'truck']:
                    # Annetaan sille sekä kuvat että nämä YOLOn saamat tulokset
                    if onko_oma_auto(kuvakaappaukset, tulokset):
                        lopullinen_leima = "oma_auto"
                    else:
                        lopullinen_leima = "vieras_auto"

                # Lisätään leima listaan, jos se löydettiin eikä ole jo listalla
                if lopullinen_leima and lopullinen_leima not in kohteen_nimi:
                    kohteen_nimi.append(lopullinen_leima)
        
        return kohteen_nimi

    except Exception as e:
        log_service.virhe_logi(f"Virhe kohteiden tunnistamisessa: {e}", "error_log.txt")
        return []


def onko_oma_koira(kuvakaappaukset):
    try:
        # 1. Tehdään lista kaikista oman koiran mallikuvista
        kansio_polku = "images/koira"
        mallikuvat = []
        if os.path.exists(kansio_polku):
            for tiedosto in os.listdir(kansio_polku):
                if tiedosto.endswith((".jpg", ".JPEG", ".png")):
                    mallikuvat.append(os.path.join(kansio_polku, tiedosto))

        malli_encode = []
        
        # 2. Ladataan ja lasketaan piirteet jokaisesta kuvasta silmukassa
        for mallikuva in mallikuvat:
            mallikuva = face_recognition.load_image_file(mallikuva)
            mallikuva_encode = face_recognition.face_encodings(mallikuva)
            if len(mallikuva_encode) > 0:
                # Otetaan ensimmäiset Löytyneet kasto talteen listaan
                malli_encode.append(mallikuva_encode[0])

        # 3. Verrataan videon kuvia näihin kaikkiin mallikuviin
        for kuva in kuvakaappaukset:
            kuva_encofings = face_recognition.face_encodings(kuva)

            for enco in kuva_encofings:
                # compare_faces osaa ottaa vastaan koko listan kerralla
                osumat = face_recognition.compare_faces(malli_encode, enco)

                # Jos yksikin kuva listalla täsmää (True), koira on tunnistettu
                if True in osumat:
                    return True
        
        return False

    except Exception as e:
        log_service.virhe_logi(f"Virhe oma-koiran tunnistamisessa: {e}", "error_log.txt")
        return None

def onko_oma_auto(kuvakaappaukset, tulokset_yolo):
    try:
        # 1. HAETAAN AUTON MALLIKUVAT AUTOMAATTISESTI KANSIOSTA JA LASKETAAN HISTOGRAMMIT
        kansion_polku = "images/auto"
        malli_histogrammit = []
        
        if os.path.exists(kansion_polku):
            for tiedosto in os.listdir(kansion_polku):
                if tiedosto.endswith(('.jpg', '.jpeg', '.png')):
                    polku = os.path.join(kansion_polku, tiedosto)
                    m_kuva = cv2.imread(polku)
                    
                    if m_kuva is not None:
                        # Muutetaan HSV-muotoon värianalyysiä varten
                        m_hsv = cv2.cvtColor(m_kuva, cv2.COLOR_BGR2HSV)
                        # Lasketaan värisormenjälki (Histogrammi)
                        hist = cv2.calcHist([m_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                        malli_histogrammit.append(hist)

        # Jos kansio on tyhjä tai kuvia ei löydy, ei voida verrata
        if len(malli_histogrammit) == 0:
            return False

        # 2. VERRATAAN VIDEON AUTOJA NÄIHIN SORMENJÄLKIIN
        for i, tulos in enumerate(tulokset_yolo):
            kuva = kuvakaappaukset[i]
            
            for box in tulos.boxes:
                luokka_id = int(box.cls[0])
                if malli.names[luokka_id] in ['car', 'truck']:
                    # Haetaan koordinaatit ja lasketaan muoto (leveys vs korkeus)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    leveys = x2 - x1
                    korkeus = y2 - y1
                    
                    if korkeus > 0:
                        suhdeluku = leveys / korkeus
                    else:
                        suhdeluku = 0

                    # Rajataan auton alue videokuvasta
                    auton_alue = kuva[y1:y2, x1:x2]
                    if auton_alue.size == 0:
                        continue
                        
                    # Lasketaan videon auton alueesta samanlainen histogrammi
                    video_hsv = cv2.cvtColor(auton_alue, cv2.COLOR_BGR2HSV)
                    video_hist = cv2.calcHist([video_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                    cv2.normalize(video_hist, video_hist, 0, 1, cv2.NORM_MINMAX)
                    
                    # Verrataan videon autoa jokaiseen mallikuvaan
                    for m_hist in malli_histogrammit:
                        # cv2.HISTCMP_CORREL antaa tuloksen väliltä -1.0 ja 1.0
                        osuma_tarkkuus = cv2.compareHist(m_hist, video_hist, cv2.HISTCMP_CORREL)
                        
                        # TÄSMÄYSTARKISTUS: Jos muoto täsmää farmariin JA värit täsmäävät kuvaan yli 60%
                        if suhdeluku > 1.8 and osuma_tarkkuus > 0.6:
                            return True # Auto tunnistettu omaksi!
                            
        return False
    except Exception as e:
        log_service.virhe_logi(f"Virhe dynaamisessa auton tunnistamisessa: {e}", "error_log.txt")
        return None

def onko_tuttu_henkilo(kuvakaappaukset):
    try:
        # 1. Tehdään lista kaikista tuttu henkilöistä mallikuvista
        kansio_polku = "images/ihmiset"
        mallikuvat = []
        if os.path.exists(kansio_polku):
            for tiedosto in os.listdir(kansio_polku):
                if tiedosto.endswith((".jpg", ".JPEG", ".png")):
                    mallikuvat.append(os.path.join(kansio_polku, tiedosto))

        malli_encode = []
        
        # 2. Ladataan ja lasketaan piirteet jokaisesta kuvasta silmukassa
        for mallikuva in mallikuvat:
            mallikuva = face_recognition.load_image_file(mallikuva)
            mallikuva_encode = face_recognition.face_encodings(mallikuva)
            if len(mallikuva_encode) > 0:
                # Otetaan ensimmäiset Löytyneet kasto talteen listaan
                malli_encode.append(mallikuva_encode[0])

        # 3. Verrataan videon kuvia näihin kaikkiin mallikuviin
        for kuva in kuvakaappaukset:
            kuva_encofings = face_recognition.face_encodings(kuva)

            for enco in kuva_encofings:
                # compare_faces osaa ottaa vastaan koko listan kerralla
                osumat = face_recognition.compare_faces(malli_encode, enco)

                # Jos yksikin kuva listalla täsmää (True), koira on tunnistettu
                if True in osumat:
                    return True
        
        return False

    except Exception as e:
        log_service.virhe_logi(f"Virhe oma-koiran tunnistamisessa: {e}", "error_log.txt")
        return None