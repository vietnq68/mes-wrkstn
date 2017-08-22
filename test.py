from pyzbar.pyzbar import decode
from PIL import Image

a = decode(Image.open('image/reasons/fff231717.png'))
print a
