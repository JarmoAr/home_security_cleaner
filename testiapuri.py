import sys
from types import ModuleType

# 1. Tehdään feikki face_recognition -kirjasto
feikki_fr = ModuleType("face_recognition")
feikki_fr.load_image_file = lambda polku: "feikkikuva"
feikki_fr.face_encodings = lambda kuva: [[0.1, 0.2, 0.3]]
feikki_fr.compare_faces = lambda lista, enco: [True]
sys.modules["face_recognition"] = feikki_fr

# 2. Tehdään feikki ultralytics (YOLO) -kirjasto
feikki_ultra = ModuleType("ultralytics")
class FeikkiYOLO:
    def __init__(self, malli): pass
    def predict(self, source, verbose=False):
        class FeikkiTulos:
            class FeikkiBox:
                def __init__(self):
                    self.cls = [0]
                    self.xyxy = [10, 20, 100, 200]
            def __init__(self):
                self.boxes = [FeikkiBox()]
        return [FeikkiTulos()]

feikki_ultra.YOLO = FeikkiYOLO
sys.modules["ultralytics"] = feikki_ultra
# 3. Tehdään feikki cv2 (OpenCV) -kirjasto pilviajoa varten
feikki_cv2 = ModuleType("cv2")
# Tehdään tyhjä VideoCapture-luokka, jotta ota_kuvakaappaukset ei kaadu heti alussa
class FeikkiVideoCapture:
    def __init__(self, *args, **kwargs): pass
    def get(self, *args): return 0
    def set(self, *args): return True
    def read(self): return False, None
    def release(self): pass

feikki_cv2.VideoCapture = FeikkiVideoCapture
feikki_cv2.COLOR_BGR2HSV = 40  # OpenCV:n käyttämä kiinteä numeroarvo
feikki_cv2.HISTCMP_CORREL = 0
feikki_cv2.cvtColor = lambda kuva, koodi: "feikki_hsv"
feikki_cv2.calcHist = lambda *args: "feikki_hist"
feikki_cv2.normalize = lambda *args: None
feikki_cv2.compareHist = lambda *args: 1.0
sys.modules["cv2"] = feikki_cv2

def luo_feikki_service(palautettava_data):
    # Luodaan lennossa olio, jolla on tarvittavat metodit
    class FeikkiService:
        def users(self): return self
        def messages(self): return self
        def list(self, **kwargs): return self
        def attachments(self): return self
        def get(self, **kwargs): return self
        def execute(self): return palautettava_data
        
    return FeikkiService()