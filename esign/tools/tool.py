import urllib
import uuid
import json
import requests
import random
import traceback
import re
from dateutil import tz  
from datetime import datetime, timedelta
from qiniu import Auth, put_data, BucketManager
from qiniu import PersistentFop, build_op, op_save, urlsafe_base64_encode
#from config.myredis import MyRedis
from .myredis import MyRedis
from .log import logger
import hashlib
from urllib.parse import urljoin
from django.http import JsonResponse

import os
import sys
from PIL import Image  
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


access_key = '4o8fd-5QVgP1Q5hO8uidQKlmPVT1cH01DDUf3GJU'
secret_key = 'd9q_qGPQ3jEfzjcd5h7cDoyKIMQADxPS7kMkglry'
bucket_name = 'media'
bucket_domain = 'http://cdn.iruyue.tv/'
redis = MyRedis()

def make_password(data):
    data = data.encode()
    m = hashlib.md5()
    m.update(data)
    psw = m.hexdigest()
    return psw

def make_identity(mobile, user):
    identity = make_password(mobile+'%.2f' % random.random())
    redis = MyRedis()
    key = 'identity_user' + identity 
    redis.set(key, user.id)
    redis.expire(key, 7200)
    return identity
def authentication(fun):
    def wrapper(request):
        identity = None
        if request.method == 'GET':
            identity = request.GET.get('identity')
            
        elif request.method == 'POST':
            identity = request.POST.get('identity')
            if not identity:
                try:
                    data = request.body
                    data = json.loads(data.decode())
                    identity = data.get('identity')
                except:
                    identity = None
        if identity:
#            filter_quto = re.match('"(.*)"', identity)
#            if filter_quto:
#                identity = filter_quto.groups()[0]
            
            key = 'identity_user' + identity
            user_id = redis.get(key)
            redis.expire(key, 24*3600)
            
            if not user_id:
                result = {'status':'301', 'message':'identity过期，请重新登录'}
                return JsonResponse(result)
        else:
            result = {'status':'300', 'message':'未登录'}
            return JsonResponse(result)
        response = fun(request)
        return response

    return wrapper
def pagination(fun):
    def wrapper(request):
        if request.method == 'GET':
            page_no = request.GET.get('page_no')
            page_count = request.GET.get('page_count')
            response = fun(request)
            data = response.content
            data = data.decode()
            data = json.loads(data)
            content = data.get('content')
            if content and content != 'none':
                length = len(content)
                if not page_no:
                    page_no = 1
                else:
                    page_no = int(page_no)
                if not page_count:
                    page_count = 5
                else:
                    page_count = int(page_count)

                pages = length/page_count
                if length % page_count:
                    pages += 1
       
                start = (page_no-1)*page_count
                if page_no == int(pages):
                    end = length 
                else:
                    end = page_no*page_count

                if page_no > pages:
                    content = []
                else:
                    content = content[start:end]
                data['content'] = content
                data['length'] = length
                return JsonResponse(data)
            else:
                data['length'] = 0
                return JsonResponse(data)
        else:
            return fun(request)
    return wrapper

def trans_to_localtime(utc_time):
    # UTC Zone  
    from_zone = tz.gettz('UTC')  
    # China Zone  
    to_zone = tz.gettz('CST')  
      
      
    # Tell the datetime object that it's in UTC time zone  
    utc = utc_time.replace(tzinfo=from_zone)  
      
    # Convert time zone  
    local = utc.astimezone(to_zone)  
    return local

def ndays_time(days):
    now = datetime.now()
    delta = timedelta(days=days)
    n_days = now + delta
    return n_days

def upload_file(data, header='', name=''):
    """
    upload file(byte) to qiuniu
    :param data: file(byte)
    :param header: file name header
    :return:url (not bucket_domain)
    """
    try:
        if name:
            tail = '.' + name.split('.')[-1]
        else:
            tail = '.' + data.name.split('.')[-1]
    except Exception:
        tail = ''
    filename = str(header) + str(uuid.uuid1()) + tail
    auth = Auth(access_key, secret_key)
    print(filename)
    upload_token = auth.upload_token(bucket_name)
    ret, info = put_data(upload_token, filename, data)
    if info.status_code == 200:
        file_url = filename
        return file_url
    else:
        raise False

def del_uploaded(url):
    filename = url.split('/')[-1]
    if not filename:
        filename = url.split('/')[-2]
    auth = Auth(access_key, secret_key)
    bucket = BucketManager(auth)
    ret, info = bucket.delete(bucket_name, filename)
    print(info)

def get_uploaded(filename):
    auth = Auth(access_key, secret_key)
    bucket = BucketManager(auth)
    ret, info = bucket.stat(bucket_name, filename)
    info = eval(info.text_body)
    print(info)
    return info

def is_img_or_video(url):
    key = url.split('/')[-1]
    info = get_uploaded(key)
    mimeType = info.get('mimeType')
    is_img = False
    is_video = False
    if re.match('^image/.*', mimeType):
        is_img = True
    elif re.match('^video/.*', mimeType):
        is_video = True
    data = dict(is_img=is_img,
            is_video=is_video)
    print(data)
    return data    
def get_screenshot(url):
    key = url.split('/')[-1]
    auth = Auth(access_key, secret_key)
    
    #截图使用的队列名称。
    pipeline = 'mpsdemo'
    
    #要进行的截图操作。
    fops = 'vframe/jpg/offset/1/w/480/h/360/rotate/90'
    
    #可以对截取后的图片进行使用saveas参数自定义命名，当然也可以不指定文件会默认命名并保存在当前空间
    file_name = key.split('.')[0] + '.jpg'
    saveas_key = urlsafe_base64_encode('%s:%s' % (bucket_name,file_name))
    fops = fops+'|saveas/'+saveas_key
    
#    pfop = PersistentFop(auth, bucket_name, pipeline)
    pfop = PersistentFop(auth, bucket_name)
    ops = []
    ops.append(fops)
    ret, info = pfop.execute(key, ops, 1)
    print(info)
    assert ret['persistentId'] is not None
    return urljoin(bucket_domain, file_name)
def log_exception():
    logger.info(traceback.format_exc())
    print('traceback.format_exc():\n%s' % traceback.format_exc())
def con_local_pdf(f_jpg):
    img = Image.open(f_jpg)  
    filename = f_jpg.name.split('.')[0]
    pdf_name = filename+'.pdf'
#    (w, h) = landscape(A4)
    (w, h) = img.size
#    c = canvas.Canvas(f_pdf, pagesize = landscape(A4))
    c = canvas.Canvas(pdf_name, pagesize = (w, h))
    reader = ImageReader(img) 
    c.drawImage(reader, 0, 0, w, h)
    c.save()
    return pdf_name

def conpdf(f_jpg):
    img = Image.open(f_jpg)  
    filename = f_jpg.name.split('.')[0]
    pdf_name = filename+'.pdf'
#    (w, h) = landscape(A4)
    (w, h) = img.size
#    c = canvas.Canvas(f_pdf, pagesize = landscape(A4))
    c = canvas.Canvas(pdf_name, pagesize = (w, h))
    reader = ImageReader(img) 
    c.drawImage(reader, 0, 0, w, h)
    c.save()
    return pdf_name
#    fsize = os.path.getsize(pdf_name)
#    pdf_reader = open(pdf_name, 'rb').read()
#    name = upload_file(pdf_reader, name=pdf_name)
#    os.remove(pdf_name)
#    url = urljoin(bucket_domain, name)
#    print(url)
#    return url, fsize 

if __name__ == "__main__":
#    del_uploaded('622d05d0-e959-11e7-ae03-9cf387d3f78e.pdf')
#    get_uploaded('622d05d0-e959-11e7-ae03-9cf387d3f78e.pdf')
#    with open(file_name, 'rb') as data:
#        print(data.name)
#        url = upload_file(data.read())
#        print(url)
    f_jpg = 'mm.jpg'
    f = open(f_jpg, 'rb')
    conpdf(f)
