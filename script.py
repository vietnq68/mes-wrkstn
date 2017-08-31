from rest import *
from collections import OrderedDict
from utils import *

#init workstations
def init_workstations():
    workstations = OrderedDict(
        [('w1' , {'type':'Statistic','name':'Top workstation'}),
         ('w2' , {'type':'Statistic','name':'Bot workstation'}),
         ('w3' , {'type':'Test','name':'Test workstation'}),
         ('w4',  {'type': 'Fix', 'name': 'Fix workstation'}),
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
            'pcb_id':pcbid,
            'status':'N/A'
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
            'code': code,
            'count':0,
        }
        #4642, 4345, 2350, 1251
        if data['name'] == 'Reason_1':
            data['count'] == 46
        elif data['name'] == 'Reason_2':
            data['count'] == 43
        elif data['name'] == 'Reason_3':
            data['count'] == 23
        elif data['name'] == 'Reason_4':
            data['count'] == 12
        create('reasons', data)
    print "Import reasons success"

def create_product_quality():
    data = {
        'name': 'product',
        'success_count': 421,
        'error_count': 124,
    }
    create('quality', data)

    print "Create product quality success"

init_workstations()
import_products('Top workstation')
import_reasons()
create_product_quality()


