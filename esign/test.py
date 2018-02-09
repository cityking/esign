import requests
import json
import os, random, sys, requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

identity = '5b4c20ff0980f9fdbef9bc0694506e97'
base_url = 'http://192.168.123.96:9000'
def get_documents():
    url = '%s/esign/get_documents' % base_url
    data = dict(identity=identity)
#    data = dict(mobile='18321339272', password='ct989016') 
    response = requests.post(url, json=data)
    print(response.json())

get_documents()
