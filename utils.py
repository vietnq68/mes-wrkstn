from os import listdir
from os.path import isfile, join
from pyzbar.pyzbar import decode
from PIL import Image
from rest import *
import barcode

def get_files(path):
   files = [f for f in listdir(path) if isfile(join(path, f))]
   return files

def decode_barcode(image):
   code = decode(Image.open(str(image)))
   return code

def get_workstations():
   response = get_all('workstations').json()
   print response[0]['name']

def gen_barcode(code,type):
   EAN = barcode.get_barcode_class(type)
   ean = EAN(code, writer=barcode.writer.ImageWriter())
   path = 'image/products/'+code
   fullname = ean.save(path)
   path = path+'.png'
   im = Image.open(path)
   im = im.resize((167, 50))
   im.save(path, 'PNG', quality=100)
   # im = im.resize((167, 50))
   # im.save(path, quality=90)

# gen_barcode('aaaa46237777','code39')