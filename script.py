from rest import *
from collections import OrderedDict
from utils import *

#init workstations
def init_workstations():
    workstations = OrderedDict(
        [('w1' , {'type':'Statistic','name':'w1'}),
         ('w2' , {'type':'Statistic','name':'w2'}),
         ('w3' , {'type':'Test','name':'w3'}),
         ('w4',  {'type': 'Fix', 'name': 'w4'}),
         ]
    )
    previous_id = ''
    for key, value in workstations.iteritems():
        response = create('workstations',value)
        if previous_id:
            data = {
                'next_wrkstn_id':response.json().get('_id')
            }
            update('workstations',previous_id,data)
        previous_id = response.json().get('_id')
    print "Init workstations success"


def import_products(workstation_name):
    files = get_files('image/products/')
    for f in files:
        path = 'image/products/'+f
        pcbid = decode_barcode(path)[0][0]
        param = 'name='+workstation_name
        fisrt_workstation = search('workstations',param).json()
        data ={
            'next_wrkstn_id':fisrt_workstation['_id'],
            'pcb_id':pcbid
        }
        create('products',data)
    print "Import products success"

def import_reasons():
    files = get_files('image/reasons/')
    for f in files:
        path = 'image/reasons/' + f
        name = f.split('.')
        code = decode_barcode(path)[0][0]
        data = {
            'name': name[0],
            'code': code
        }
        create('reasons', data)
    print "Import reasons success"

init_workstations()
import_products('w1')
import_reasons()


