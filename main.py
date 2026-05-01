import os

# Paths
temp_path = r"d:\valvontakamera\temp"
arkisto_path = r"d:\valvontakamera\arkisto"
image_path = r".\image"

# testing
print("Temp kansio olemassa:", os.path.exists(temp_path))
print("Arkisto kansio olemassa:", os.path.exists(arkisto_path))
print("Image kansio olemassa:", os.path.exists(image_path))