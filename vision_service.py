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

        for kuva in kuvakaappaukset:
            tulokset = malli.predict(source=kuva)
            for box in tulokset[0].boxes:
                luokka_id = int(box.cls[0])
                nimi = malli.names[luokka_id]
                if nimi not in kohteen_nimi:
                    kohteen_nimi.append(nimi)
        
        return kohteen_nimi

    except Exception as e:
        log_service.virhe_logi(f"Virhe kohteiden tunnistamisessa: {e}", "error_log.txt")
        return []


        