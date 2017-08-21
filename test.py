from pyzbar.pyzbar import decode
from PIL import Image

a = decode(Image.open('image/5.png'))
print a
