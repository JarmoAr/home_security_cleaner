import sys
from types import ModuleType

# Luokat pitää määritellä ENSIN, jotta niitä voidaan käyttää alempana!
class FeikkiYOLO:
    def __init__(self, malli):
        self.names = {2: 'car', 0: 'person', 1: 'dog'}
        
    def predict(self, source, verbose=False):
        class FeikkiBox:
            def __init__(self):
                self.cls = [2]  
                self.xyxy = [[10, 20, 100, 200]]
                
        class FeikkiTulos:
            def __init__(self):
                self.boxes = [FeikkiBox()]
                
        return [FeikkiTulos()]

class FeikkiVideoCapture:
    def __init__(self, *args, **kwargs): pass
    def get(self, *args): return 0
    def set(self, *args): return True
    def read(self): return False, None
    def release(self): pass


# 1. Feikkikirjastot testausta varten 
# Tehdään feikki face_recognition -kirjasto
feikki_fr = ModuleType("face_recognition")
feikki_fr.load_image_file = lambda polku: "feikkikuva"
feikki_fr.face_encodings = lambda kuva: [[0.1, 0.2, 0.3]]
feikki_fr.compare_faces = lambda lista, enco: [True]
sys.modules["face_recognition"] = feikki_fr

# Feikki CV2 -kirjasto (Nyt FeikkiVideoCapture on tunnettu!)
feikki_cv2 = ModuleType("cv2")
feikki_cv2.VideoCapture = FeikkiVideoCapture
feikki_cv2.COLOR_BGR2HSV = 40  
feikki_cv2.HISTCMP_CORREL = 0
feikki_cv2.cvtColor = lambda kuva, koodi: "feikki_hsv"
feikki_cv2.calcHist = lambda *args: "feikki_hist"
feikki_cv2.normalize = lambda *args: None
feikki_cv2.compareHist = lambda *args: 1.0
sys.modules["cv2"] = feikki_cv2

# feikki numpy-kirjasto
feikki_np = ModuleType("numpy")
feikki_np.uint8 = int
feikki_np.zeros = lambda *args, **kwargs: "feikkikuva_taulukko"
sys.modules["numpy"] = feikki_np

# feikki ultralytics (YOLO) -kirjasto (Nyt FeikkiYOLO on tunnettu!)
feikki_ultra = ModuleType("ultralytics")
feikki_ultra.YOLO = FeikkiYOLO
sys.modules["ultralytics"] = feikki_ultra

# Robot avainsanat loppuun
def luo_feikki_service(palautettava_data):
    class FeikkiService:
        def users(self): return self
        def messages(self): return self
        def list(self, **kwargs): return self
        def attachments(self): return self
        def get(self, **kwargs): return self
        def execute(self): return palautettava_data
    return FeikkiService()

def luo_feikkikuva():
    import numpy as np
    return np.zeros((100, 100, 3), dtype=np.uint8)
