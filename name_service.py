from datetime import datetime

def aikaleiman_muutos(aikaleima):
    try:
       aikaleima = int(aikaleima) / 1000
       uusi_aikaleima = datetime.fromtimestamp(aikaleima).strftime('%Y%m%d_%H%M%S')
       return uusi_aikaleima
    
    except Exception as e:
       return None



#testi osio
if __name__ == "__main__":
    test_aikaleima = "1777360465000"
    uusi_aikaleima = aikaleiman_muutos(test_aikaleima)
    if uusi_aikaleima:
        print(f"Uusi aikaleima: {uusi_aikaleima}")  
