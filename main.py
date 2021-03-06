import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils import *
from rest import *
import datetime
import time

wrkstn_type={
   0:'Top workstation',
   1:'Bot workstation',
   2:'Test workstation',
   3:'Fix workstation',
}

label_font = QFont()
label_font.setPointSize(26)
label_font.setBold(True)

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
      self.completed = 0
      # self.progress = QProgressBar(self.win)
      # self.progress_text = QLabel(self.win)
      self.label = QLabel(self.win)

   def add_item(self,f):
      # item = QListWidgetItem(f)
      self.list.append(f)


   def show_items(self):
      # t = QLabel(self.win)
      # t.setText("Scan Barcode")
      # t.move(250, 15)

      font = QFont()
      font.setPointSize(30)
      font.setBold(True)

      self.label.setText('Top Workstation ')
      self.label.setFont(label_font)
      self.label.setStyleSheet("color: #3598DC;")
      self.label.move(160, 20)

      self.cb = QComboBox(self.win)
      self.get_workstations()
      for w in self.workstations:
         self.cb.addItem(w['type']+' - '+w['name'])
      self.cb.currentIndexChanged.connect(self.selectionchange)
      self.cb.move(190, 60)

      # self.progress.move(500, 0)
      # self.progress.hide()

      # self.progress_text.move(510, 25)
      # self.progress_text.setText('heloooooooo')
      # self.progress_text.hide()

      self.mes = QLabel(self.win)
      self.mes.setText("message:")
      self.mes.move(5, 0)
      self.mes.hide()

      x = 25
      y = 120
      count = 1
      for f in self.list:
         path = "image/products/" + f
         with Image.open(path) as img:
            width, height = img.size
         btn = QPushButton(self.win)
         btn.setText(str(count))
         btn.setFont(font)
         btn.setMinimumSize(167, 50)
         btn.resize(167, 50)
         # btn.setIcon(QIcon(path))
         btn.setProperty('value',count)
         btn.setIconSize(QSize(width, height))
         if x + width + 20 > 600:
            x = 25
            y += height + 30
         btn.move(x, y)
         btn.clicked.connect(self.scan_barcode)
         x += width + 20
         btn.show()
         self.win.setGeometry(400,200,600,350)
         self.win.setWindowTitle("VNTP-MES")
         self.win.show()
         count = count+1

   def selectionchange(self, i):
      self.type = i
      self.label.setText(wrkstn_type[i])


   def scan_barcode(self):
      self.mes.hide()
      # self.progress.hide()
      # self.progress_text.hide()
      self.tested = False
      self.fixed = False
      self.quality = search('quality', 'name=product').json()
      btn = self.sender()
      #read barcode
      barcode = btn.property('value').toPyObject()
      # barcode = decode_barcode(v)[0][0]
      #get product
      param = 'pcb_id=' + str(barcode)
      self.product = search('products', param).json()
      self.workstation = self.workstations[self.type]
      #check workstation of product
      if self.product:
         if 'next_wrkstn_id' in self.product and self.product['next_wrkstn_id'] != self.workstation['_id']:
            self.show_message("Product is not scan at previous workstation","Error")
            return
      # self.progress.show()
      # self.progress_status('running')
      #update product
      # handle if workstation is test
      if self.workstation['type'] == 'Test':
         self.processing_signal('running')
         self.update_state()
         self.product_test_popup()
         if self.tested:
            self.sender().setStyleSheet("background-color: grey")
            self.sender().setEnabled(False)
      #handle if workstation is fix
      elif self.workstation['type'] == 'Fix':
         self.processing_signal('running')
         self.update_state()
         self.product_fix_popup()
         if self.fixed:
            self.sender().setStyleSheet("background-color: grey")
            self.sender().setEnabled(False)
            # self.processing()
            self.processing_signal('finish')
      else:
         self.processing_signal('running')
         self.update_state()
         self.sender().setStyleSheet("background-color: grey")
         self.sender().setEnabled(False)
         self.show_message("Product scan success", "Success")
         # self.processing()
         self.processing_signal('finish')

   def product_test_popup(self):
      # self.processing()
      btnPass = QPushButton(self.test_popup)
      btnPass.setText('Pass')
      btnPass.setProperty('value', 'Pass')
      btnPass.setStyleSheet("color: #26C281;")
      btnPass.move(50,10)
      btnPass.show()
      btnPass.clicked.connect(self.on_tested)
      btnFail = QPushButton(self.test_popup)
      btnFail.setText('Fail')
      btnFail.setProperty('value', 'Fail')
      btnFail.setStyleSheet("color: #EF4836;")
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
      font = QFont()
      font.setPointSize(26)
      font.setBold(True)
      x = 25
      y = 60
      count = 1
      for f in range(1,10):
         # name = f.split('.')
         # reason = QLabel(self.fix_popup)
         # reason.setText(name[0])
         # path = "image/reasons/" + strf
         # with Image.open(path) as img:
         #    width, height = img.size
         width = 167
         height = 50
         btn = QPushButton(self.fix_popup)
         # btn.setIcon(QIcon(path))
         btn.setText('Reason '+str(count))
         btn.setProperty('value',count)
         btn.setMinimumSize(167, 50)
         btn.resize(167, 50)
         # btn.setIconSize(QSize(width, height))
         if x + width + 20 > 600:
            x = 25
            y += height+40
         # reason.move(x,y)
         btn.move(x, y+20)
         btn.setFont(font)
         btn.clicked.connect(self.on_fixed)
         x += width + 20
         btn.show()
         count = count+1
      self.fix_popup.setGeometry(400,100,600,350)
      self.fix_popup.setWindowTitle("PyQt")
      self.fix_popup.exec_()

   def on_tested(self):
      self.tested = True
      btn = self.sender()
      self.status = btn.property('value').toPyObject()
      self.show_message("Update state success", "Success")
      self.test_popup.close()
      self.processing_signal('finish')
      if self.status == 'Pass':
         finished_socket('products', self.product['_id'])
         update('quality',self.quality['_id'],{'success_count':self.quality['success_count'] + 1})
      else:
         error_socket('products', self.product['_id'])
         update('quality', self.quality['_id'], {'error_count': self.quality['error_count'] + 1})

   def on_fixed(self):
      self.fixed = True
      self.status = 'Pass'
      # read barcode
      v = self.sender().property('value').toPyObject()
      barcode = str(v)
      # get reason
      param = 'code=' + barcode
      reason = search('reasons', param).json()
      data = {
         'error_reason':reason['_id']
      }
      finished_socket('products', self.product['_id'])
      update('products', self.product['_id'], data)
      update('reasons', reason['_id'],{'count':reason['count']+1})
      paretoChart(self.product['_id'])
      self.fix_popup.close()

   def update_state(self):
      next_wrkstn_id = self.workstation['next_wrkstn_id'] if 'next_wrkstn_id' in self.workstation else ''
      # status= str(self.status)
      scan_time = datetime.datetime.now()
      data = {
            'scan_time':scan_time,
            'current_wrkstn_id':self.workstation['_id'],
      }
      # if next_wrkstn_id:
      #    data['next_wrkstn_id'] =next_wrkstn_id
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

   def get_workstations(self):
      self.workstations = get_all('workstations').json()

   def show_message(self,mess,type):
      self.mes.setText(mess)
      if type == 'Error':
         self.mes.setStyleSheet("color: #EF4836;")
      elif type == 'Success':
         self.mes.setStyleSheet("color: #26C281;")
      self.mes.show()

   def processing(self):
      #script for demo
      self.completed = 0
      delay = 0
      if self.workstation['name'] == 'Bot workstation':#script line pending
         while self.completed < 65:
            self.completed += 0.00004
            self.progress.setValue(self.completed)

         self.processing_signal('pending')
         self.progress_status('pending')
         time.sleep(3)

         self.processing_signal('running')
         self.progress_status('running')

         while self.completed < 100:
            self.completed += 0.00004
            self.progress.setValue(self.completed)
      else:
         while self.completed < 100:
            self.completed += 0.00004
            self.progress.setValue(self.completed)
      self.progress_status('finish')

   def processing_signal(self,type):
      signal =0
      if type == 'running':
         signal = 1
      data = {
         'progress':type,
         'signal':signal,
         'status': str(self.status),
         'product': self.product['_id'],
         'pcb_id': self.product['pcb_id'],
         'workstation_name': self.workstation['name'],
         'workstation_id': self.workstation['_id'],
      }

      product_data = {
         'process': type,
      }

      if self.status =='Pass':
         data['next_wrkstn_name'] = 'None'
      elif 'next_wrkstn_id' in self.workstation:
         next_workstation = get_one('workstations', self.workstation['next_wrkstn_id']).json()
         data['next_wrkstn_name'] = next_workstation['name']
         if type == 'finish':
            product_data['status'] = str(self.status)
            product_data['next_wrkstn_id'] = next_workstation['_id']


      workstation_process(self.product['_id'], data)
      update('products', self.product['_id'], product_data)

   def progress_status(self,status):
      # self.progress_text.show()
      if status == 'running':
         self.progress_text.setText('Running ...')
         self.progress_text.setStyleSheet("color: #3598dc")
         self.progress.setStyleSheet("background-color: #3598dc")
      elif status == 'finish':
         self.progress_text.setText('     Finish')
         self.progress_text.setStyleSheet("color: #26C281")
         self.progress.setStyleSheet("background-color: #26C281")
      elif status == 'pending':
         self.progress_text.setText('    Pending')
         self.progress_text.setStyleSheet("color: orange")

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = Window()
   files = get_files('image/products/')
   for f in files:
      window.add_item(f)
   window.show_items()
   sys.exit(app.exec_())