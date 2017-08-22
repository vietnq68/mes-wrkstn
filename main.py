import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils import *
from rest import *
import datetime

class Window(QWidget):
   def __init__(self):
      QWidget.__init__(self)
      self.win = QDialog()
      self.list =[]
      self.workstations =[]
      self.type =0
      self.popup = QDialog()
      self.status = 'true'

   def add_item(self,f):
      # item = QListWidgetItem(f)
      self.list.append(f)


   def show_items(self):
      t = QLabel(self.win)
      t.setText("Scan Barcode")
      t.move(250, 15)

      self.cb = QComboBox(self.win)
      self.get_workstations()
      for w in self.workstations:
         self.cb.addItem(w['type']+' - '+w['name'])
      self.cb.currentIndexChanged.connect(self.selectionchange)
      self.cb.move(250, 30)

      self.mes = QLabel(self.win)
      self.mes.setText("message:")
      self.mes.move(5, 0)
      self.mes.hide()

      x = 10
      y = 80
      for f in self.list:
         path = "image/" + f
         with Image.open(path) as img:
            width, height = img.size
         btn = QPushButton(self.win)
         btn.setIcon(QIcon(path))
         btn.setProperty('value',path)
         btn.setIconSize(QSize(width, height))
         if x + width + 20 > 600:
            x = 10
            y += height + 20
         btn.move(x, y)
         btn.clicked.connect(self.scan_barcode)
         x += width + 20
         btn.show()
         self.win.setGeometry(400,200,600,350)
         self.win.setWindowTitle("PyQt")
         self.win.show()

   def selectionchange(self, i):
      self.type = i


   def scan_barcode(self):
      self.mes.hide()
      self.checked = False
      btn = self.sender()
      #read barcode
      v = btn.property('value').toPyObject()
      barcode = decode_barcode(v)[0][0]
      #get product
      param = 'pcb_id=' + barcode
      self.product = search('products', param).json()
      print self.product
      self.workstation = self.workstations[self.type]
      #check workstation of product
      if self.product:
         if 'next_wrkstn_id' in self.product and self.product['next_wrkstn_id'] != self.workstation['_id']:
            self.show_message("Product is not scan at previous workstation","Error")
            return
      #update product
      if self.workstation['type'] == 'Test':
         self.show_popup()
         if self.checked:
            self.sender().setStyleSheet("background-color: grey")
            self.sender().setEnabled(False)
      else:
         self.update_state()
         self.sender().setStyleSheet("background-color: grey")
         self.sender().setEnabled(False)
         self.show_message("Product scan success", "Success")

   def get_workstations(self):
      self.workstations = get_all('workstations').json()

   def show_message(self,mess,type):
      self.mes.setText(mess)
      if type == 'Error':
         self.mes.setStyleSheet("color: red;")
      elif type == 'Success':
         self.mes.setStyleSheet("color: green;")
      self.mes.show()

   def show_popup(self):
      btnPass = QPushButton(self.popup)
      btnPass.setText('Pass')
      btnPass.setProperty('value', 'true')
      btnPass.setStyleSheet("color: green;")
      btnPass.move(50,10)
      btnPass.show()
      btnPass.clicked.connect(self.update_status)
      btnFail = QPushButton(self.popup)
      btnFail.setText('Fail')
      btnFail.setProperty('value', 'false')
      btnFail.setStyleSheet("color: red;")
      btnFail.move(50, 40)
      btnFail.show()
      btnFail.clicked.connect(self.update_status)
      self.popup.setGeometry(600, 300, 200, 100)
      self.popup.setWindowTitle("Product test")
      self.popup.show()

   def update_status(self):
      self.checked = True
      btn = self.sender()
      self.status = btn.property('value').toPyObject()
      self.update_state()
      self.show_message("Update state success", "Success")
      self.popup.close()

   def update_state(self):
      next_wrkstn_id = self.workstation['next_wrkstn_id'] if 'next_wrkstn_id' in self.workstation else ''
      status= str(self.status)
      scan_time = datetime.datetime.now()
      data = {
            'status':status,
            'scan_time':scan_time,
      }
      if next_wrkstn_id:
         data['next_wrkstn_id'] =next_wrkstn_id
      #update product
      update('products', self.product['_id'], data)
      #update realtime products state in webapp
      data['current_wrkstn_id'] = self.workstation['_id']
      data['_id'] = self.product['_id']
      data['pcb_id'] = self.product['pcb_id']
      pass_workstation('products', self.product['_id'], data)
      # if this workstation is the last, update realtime product number finish/error
      if 'next_wrkstn_id' not in self.workstation:
         if status == 'true':
            finished_socket('products',self.product['_id'])
         else:
            error_socket('products',self.product['_id'])

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = Window()
   files = get_files('image/')
   for f in files:
      window.add_item(f)
   window.show_items()
   sys.exit(app.exec_())