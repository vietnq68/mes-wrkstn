import requests
base_url = 'http://localhost:8090/'

def get_all(name):
    url = base_url + name
    response = requests.get(url)
    return response

def get_one(name,id):
    url = base_url + name +'/'+id
    response = requests.get(url)
    return response

def search(name,param):
    url = base_url + name +'?' +param
    response = requests.get(url)
    return response

def create(name,data):
    url = base_url + name
    response = requests.post(url, data=data)
    return response

def update(name,id,data):
    url = base_url + name + '/' + id
    response = requests.put(url,data)
    return response

def finished_socket(name,id):
    url = base_url + name + '/' + id +'/finished'
    response = requests.post(url)
    return response

def error_socket(name,id):
    url = base_url + name + '/' + id +'/error'
    response = requests.post(url)
    return response

def pass_workstation(name,id,data):
    url = base_url + name + '/' + id +'/pass_wrkstn'
    response = requests.put(url,data)
    return response

def workstation_process(id,data):
    url = base_url + 'products' + '/' + id + '/process'
    response = requests.put(url, data)
    return response

def paretoChart(id):
    url = base_url + 'reasons' + '/' + id + '/pareto'
    response = requests.put(url)
    return response

