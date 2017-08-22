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
      self.test_popup = QDialog()
      self.fix_popup = QDialog()
      self.status = 'N/A'

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
         path = "image/products/" + f
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
      self.tested = False
      btn = self.sender()
      #read barcode
      v = btn.property('value').toPyObject()
      barcode = decode_barcode(v)[0][0]
      #get product
      param = 'pcb_id=' + barcode
      self.product = search('products', param).json()
      self.workstation = self.workstations[self.type]
      #check workstation of product
      if self.product:
         if 'next_wrkstn_id' in self.product and self.product['next_wrkstn_id'] != self.workstation['_id']:
            self.show_message("Product is not scan at previous workstation","Error")
            return
      #update product
      # handle if workstation is test
      if self.workstation['type'] == 'Test':
         self.product_test_popup()
         if self.tested:
            self.sender().setStyleSheet("background-color: grey")
            self.sender().setEnabled(False)
      #handle if workstation is fix
      elif self.workstation['type'] == 'Fix':
         self.product_fix_popup()
      else:
         self.update_state()
         self.sender().setStyleSheet("background-color: grey")
         self.sender().setEnabled(False)
         self.show_message("Product scan success", "Success")

   def product_test_popup(self):
      btnPass = QPushButton(self.test_popup)
      btnPass.setText('Pass')
      btnPass.setProperty('value', 'true')
      btnPass.setStyleSheet("color: green;")
      btnPass.move(50,10)
      btnPass.show()
      btnPass.clicked.connect(self.on_tested)
      btnFail = QPushButton(self.test_popup)
      btnFail.setText('Fail')
      btnFail.setProperty('value', 'false')
      btnFail.setStyleSheet("color: red;")
      btnFail.move(50, 40)
      btnFail.show()
      btnFail.clicked.connect(self.on_tested)
      self.test_popup.setGeometry(600, 300, 200, 100)
      self.test_popup.setWindowTitle("Product test")
      self.test_popup.exec_()

   def product_fix_popup(self):
      t = QLabel(self.fix_popup)
      t.setText("Scan Reason")
      t.move(250, 15)
      files = get_files('image/reasons/')
      x = 10
      y = 60
      for f in files:
         name = f.split('.')
         reason = QLabel(self.fix_popup)
         reason.setText(name[0])
         path = "image/reasons/" + f
         with Image.open(path) as img:
            width, height = img.size
         btn = QPushButton(self.fix_popup)
         btn.setIcon(QIcon(path))
         btn.setProperty('value',path)
         btn.setIconSize(QSize(width, height))
         if x + width + 20 > 600:
            x = 10
            y += height+40
         reason.move(x,y)
         btn.move(x, y+20)
         btn.clicked.connect(self.on_fixed)
         x += width + 20
         btn.show()
      self.fix_popup.setGeometry(400,100,600,350)
      self.fix_popup.setWindowTitle("PyQt")
      self.fix_popup.exec_()

   def on_tested(self):
      self.tested = True
      btn = self.sender()
      self.status = btn.property('value').toPyObject()
      self.update_state()
      self.show_message("Update state success", "Success")
      self.test_popup.close()

   def on_fixed(self):
      # read barcode
      v = self.sender().property('value').toPyObject()
      barcode = decode_barcode(v)[0][0]
      # get reason
      param = 'code=' + barcode
      reason = search('reasons', param).json()
      data = {
         'error_reason':reason['_id']
      }
      update('products', self.product['_id'], data)
      self.fix_popup.close()

   def update_state(self):
      next_wrkstn_id = self.workstation['next_wrkstn_id'] if 'next_wrkstn_id' in self.workstation else ''
      status= str(self.status)
      scan_time = datetime.datetime.now()
      data = {
            'status':status,
            'scan_time':scan_time,
      }
      if self.workstation['type'] == 'Test' and self.status == 'true':
         next_wrkstn_id=''
      if next_wrkstn_id:
         data['next_wrkstn_id'] =next_wrkstn_id
      #update product
      update('products', self.product['_id'], data)
      #update realtime products state in webapp
      if next_wrkstn_id:
         next_workstation = get_one('workstations', next_wrkstn_id).json()
         data['next_wrkstn_name'] = next_workstation['name']
      data['current_wrkstn_name'] = self.workstation['name']
      data['_id'] = self.product['_id']
      data['pcb_id'] = self.product['pcb_id']
      pass_workstation('products', self.product['_id'], data)
      # if this workstation is the last, update realtime product number finish/error
      if self.workstation['type'] == 'Test':
         if status == 'true':
            finished_socket('products',self.product['_id'])
         else:
            error_socket('products',self.product['_id'])

   def get_workstations(self):
      self.workstations = get_all('workstations').json()

   def show_message(self,mess,type):
      self.mes.setText(mess)
      if type == 'Error':
         self.mes.setStyleSheet("color: red;")
      elif type == 'Success':
         self.mes.setStyleSheet("color: green;")
      self.mes.show()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = Window()
   files = get_files('image/products/')
   for f in files:
      window.add_item(f)
   window.show_items()
   sys.exit(app.exec_())