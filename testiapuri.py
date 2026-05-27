

def luo_feikki_service(palautettava_data):
    # Luodaan lennossa olio, jolla on tarvittavat metodit
    class FeikkiService:
        def users(self): return self
        def messages(self): return self
        def attachments(self): return self
        def get(self, **kwargs): return self
        def execute(self): return palautettava_data
        
    return FeikkiService()