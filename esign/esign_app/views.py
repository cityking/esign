from django.shortcuts import render
from django.db.utils import IntegrityError
from django.http import JsonResponse
from tools.PhoneNumberVerificator import PhoneNumberVerificator
from tools.tool import make_password, log_exception, authentication, upload_file,bucket_domain, del_uploaded
from django.views.decorators.csrf import csrf_exempt
from .models import *
from urllib.parse import urljoin
from tools.tool import conpdf
from tools.covert_to_pdf import combine_pdf, make_contract, draw_FinancingContract_second, draw_FinancingContract_third, draw_FinancingContract_forth, draw_FinancingContract_fifth, draw_FinancingContract_eighth, make_FinancingContract
from tools.WXpay import create_pay
from tools.alipay import Alipay
import os
import time
import random

@csrf_exempt
def register(request):
    """
    group = "电子签名";
    status = "work";
    protocol = "http";
    method = "post";
    path = "192.168.123.102:9000";
    name = "注册";
    header = {name="Accept-Charset",value="utf-8"};
    header = {name="Content-Type",value="application/json"};
    parameter = {name = "phone", type = "string", description = "手机号码", required = true};
    parameter = {name = "use", type = "string", description = "用途", required = true};
    response = {name = "statusCode",description = "状态码", type = "string", required = true};
    """

    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            phone = data['phone']
            code = data['code']
            password = data['password']
            confirm_password = data['confirm_password']
            verificator=PhoneNumberVerificator()
            if not verificator.CheckVerificationCode(phone, code):
                return JsonResponse({'status':'400', 'message':'验证码错误', 'content':'none'})
            if not verificator.phonecheck(phone):
                return JsonResponse({'status':'400', 'message':'输入的手机号码有误', 'content':'none'})
            if password != confirm_password:
                return JsonResponse({'status':'400', 'message':'两次输入的密码不一样', 'content':'none'})
            try:
                user = MyUser.objects.create(phone=phone,
                    password=make_password(password),
                    nick_name=phone)
            except IntegrityError:
                return JsonResponse({'status':'400', 'message':'手机号已经被注册', 'content':'none'})
            user.save()
            result = {'status':'200', 'message':'注册成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

def get_certification_code(request):
    """
    group = "电子签名";
    status = "work";
    protocol = "http";
    method = "get";
    path = "192.168.123.102:9000";
    name = "获取验证码";
    header = {name="Accept-Charset",value="utf-8"};
    header = {name="Content-Type",value="application/json"};
    parameter = {name = "phone", type = "string", description = "手机号码", required = true};
    parameter = {name = "use", type = "string", description = "用途", required = true};
    response = {name = "statusCode",description = "状态码", type = "string", required = true};
    """
    if request.method == 'GET':
        try:
            phone = request.GET.get('phone')
            use = request.GET.get('use')

            if not phone:
                result = {'status':'400', 'message':'请传入手机号', 'content':'none'}
                return JsonResponse(result, safe=False)
            #获取验证码
            verificator=PhoneNumberVerificator()
            code = verificator.VerificationCode()
            if use == 'password':
                msg = "【海签】你正在进行密码修改，验证码为%s, 5分钟失效" % code
            elif use == 'register':
                msg = "【海签】你正在进行注册，验证码为%s, 5分钟失效" % code
            if verificator.phonecheck(phone):
                verificator.send(phone, msg)
                verificator.writeCodeToRedis(code, phone, 300)

            result = {'status':'200', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
        
            phone = data.get('phone')
            password = data.get('password')
            identity = MyUser.login(phone, password)
            
            if identity == '0':
                result = {'status':'400', 'message':'密码错误'}
            elif identity == '1':
                result = {'status':'400', 'message':'用户不存在'}
            else:
                data = {'identity':identity}
                result = {'status':'200', 'message':'登录成功', 'content':data}
             
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':''}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
def update_user_password(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            phone = data['phone']
            code = data['code']
            password = data['password']
            password_again = data['confirm_password']
            verificator=PhoneNumberVerificator()
            user = MyUser.objects.filter(phone=phone)
            if not user:
                return JsonResponse({'status':'400', 'message':'该用户不存在', 'content':'none'})

            if not verificator.CheckVerificationCode(phone, code):
                return JsonResponse({'status':'400', 'message':'验证码错误', 'content':'none'})
            if password != password_again:
                return JsonResponse({'status':'400', 'message':'两次输入的密码不一样', 'content':'none'})
            user = user[0]
            user.password = make_password(password)
            user.save()
            result = {'status':'200', 'message':'重置成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

#@authentication
#def get_documents(request):
#    if request.method == 'GET':
#        try:
#            identity = request.GET.get('identity')
#            user = MyUser.get_user_by_identity(identity)
#            document_list = Documents.get_documents_by_user(user)
#            result = {'status':'200','message':'获取成功', 'content':document_list}
#        except Exception as e:
#            log_exception()
#            result = {'status':'400', 'message':'', 'content':'none'}
#        print(result)
#        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def get_documents(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data) 
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            capacity = user.get_capacity()
            used_capacity = capacity.get('used_capacity')
            total_capacity = capacity.get('total_capacity')
            demo_list = Contract_demo.get_list()
            document_list = Documents.get_documents_by_user(user)
            document_list = demo_list + document_list
            result = {'status':'200','message':'获取成功', 'used_capacity':used_capacity, 'total_capacity':total_capacity,'content':document_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)


@csrf_exempt
@authentication
def delete_document(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            documents = data.get('document_id')
            for document_id in documents:
                document = Documents.objects.get(id=document_id)
                document.delete()
            result = {'status':'200', 'message':'删除成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def collect_document(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            documents = data.get('document_id')
            for document_id in documents:
                document = Documents.objects.get(id=document_id)
                document.add_collect()
            result = {'status':'200', 'message':'收藏成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def delete_collected(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            documents = data.get('document_id')
            for document_id in documents:
                document = Documents.objects.get(id=document_id)
                document.cancel_collect()
            result = {'status':'200', 'message':'删除成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

#@authentication
#def get_collected(request):
#    if request.method == 'GET':
#        try:
#            identity = request.GET.get('identity')
#            user = MyUser.get_user_by_identity(identity)
#            document_list = Documents.get_collected_by_user(user)
#            result = {'status':'200', 'message':'获取成功', 'content':document_list}
#        except Exception as e:
#            log_exception()
#            result = {'status':'400', 'message':'', 'content':'none'}
#        print(result)
#        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def get_collected(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            document_list = Documents.get_collected_by_user(user)
            result = {'status':'200', 'message':'获取成功', 'content':document_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)


#@authentication
#def get_userinfo(request):
#    if request.method == 'GET':
#        try:
#            identity = request.GET.get('identity')
#            user = MyUser.get_user_by_identity(identity)
#            userinfo = user.get_info()
#            result = {'status':'200','message':'获取成功', 'content':userinfo}
#        except Exception as e:
#            log_exception()
#            result = {'status':'400', 'message':'', 'content':'none'}
#        print(result)
#        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def get_userinfo(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            userinfo = user.get_info()
            result = {'status':'200','message':'获取成功', 'content':userinfo}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def get_user_capacity(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            content = user.get_capacity()
            result = {'status':'200','message':'获取成功', 'content':content}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)


@csrf_exempt
@authentication
def get_userdetails(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            userinfo = user.get_detail()
            result = {'status':'200','message':'获取成功', 'content':userinfo}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def update_userinfo(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            user.update(data)
            result = {'status':'200','message':'修改成功', 'content':'none'} 
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def update_avatar(request):
    if request.method == 'POST':
        try:
            identity = request.POST.get('identity')
            user = MyUser.get_user_by_identity(identity)
            files = request.FILES.getlist('avatar')
            bucket_domain = 'http://cdn.iruyue.tv/' 
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    url = urljoin(bucket_domain, url)
                    old_url = user.avatar_url
                    user.avatar_url = url
                    if old_url:
                        del_uploaded(old_url)
                user.save()
                result = {'status':'200','message':'修改成功', 'content':'none'}
            else:
                result = {'status':'400','message':'未上传头像', 'content':'none'}
           
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)


#@authentication
#def get_mysign(request):
#    if request.method == 'GET':
#        try:
#            identity = request.GET.get('identity')
#            user = MyUser.get_user_by_identity(identity)
#            sign_list = Sign.get_sign_by_user(user)
#            result = {'status':'200','message':'获取成功', 'content':sign_list}
#        except Exception as e:
#            log_exception()
#            result = {'status':'400', 'message':'', 'content':'none'}
#        print(result)
#        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def get_mysign(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            identity = data.get('identity')

            user = MyUser.get_user_by_identity(identity)
            sign_list = Sign.get_sign_by_user(user)
            result = {'status':'200','message':'获取成功', 'content':sign_list}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def add_sign(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)

            files = request.FILES.getlist('sign_img')
            bucket_domain = 'http://cdn.iruyue.tv/' 
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    url = urljoin(bucket_domain, url)
                    signs = Sign.get_sign_by_user(user)
                    if signs:
                        sign = Sign.objects.create(sign_url=url, user=user)
                    else:
                        sign = Sign.objects.create(sign_url=url, user=user, is_default='1')
                result = {'status':'200','message':'添加成功', 'content':'none'}
            else:
                result = {'status':'400','message':'未上传签名', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':''}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def delete_sign(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            sign_id = data.get('sign_id')
            if sign_id:
                sign = Sign.objects.get(id=sign_id)
                sign.delete()
                result = {'status':'200', 'message':'删除成功', 'content':'none'}
            else:
                result = {'status':'400', '未传入sign_id':'', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def set_default_sign(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            sign_id = data.get('sign_id')
            if sign_id:
                sign = Sign.objects.get(id=sign_id)
                sign.set_default()
                result = {'status':'200', 'message':'设置成功', 'content':'none'}
            else:
                result = {'status':'400', '未传入sign_id':'', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def add_document(request):
    if request.method == 'POST':
        try: 
            data = request.POST.dict()
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            document_title = data.get('document_title')
            document_type = data.get('document_type') 
            files = request.FILES.getlist('document')
            urls = []
            image_url = []
            pdf_files = []
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    image_url.append(urljoin(bucket_domain, url))
                    pdf_name = conpdf(_file) 
                    pdf_files.append(pdf_name)
            
                if document_type == 'trade_contract': 
                    second_party = 'static/pdf/trade_contract/trade_contract_2.pdf'   
                    end_party = 'static/pdf/trade_contract/trade_contract_3_2.pdf'
                    if pdf_files:

                        pdf_list = pdf_files[0:1]
                        pdf_list.append(second_party)
                        pdf_list = pdf_list + pdf_files[1:]
                        pdf_list.append(end_party)
                        combine_file_name = combine_pdf(pdf_list, document_title+'.pdf')
                        for pdf in pdf_files:
                            os.remove(pdf)                    
                        combine_file = open(combine_file_name, 'rb')
                        reader = combine_file.read()
                        document_size = len(reader)
                        url = upload_file(reader, name=combine_file_name)
                        document_url = urljoin(bucket_domain, url)
                        os.remove(combine_file_name)

                        document = Documents.objects.create(document_title=document_title, 
                            document_url=document_url,
                            document_size = document_size,
                            img_url = str(image_url),
                            user=user,
                            document_type=document_type
                            )
                else:
                    if pdf_files:
                        combine_file_name = combine_pdf(pdf_files, document_title+'.pdf')
                        combine_file = open(combine_file_name, 'rb')
                        reader = combine_file.read()
                        document_size = len(reader)
                        capacity = user.get_capacity()
                        if capacity['used_capacity']+document_size > capacity['total_capacity']:
                            result = {'status':'205', 'message':'空间不足', 'content':'none'}
                            print(result)
                            return JsonResponse(result, safe=False) 
                        url = upload_file(reader, name=combine_file_name)
                        document_url = urljoin(bucket_domain, url)
                        for pdf in pdf_files:
                            os.remove(pdf)                    
                        os.remove(combine_file_name)
                        document_type = 'common'
                        document = Documents.objects.create(document_title=document_title, 
                            document_url=document_url,
                            document_size = document_size,
                            img_url = str(image_url),
                            user=user,
                            document_type=document_type
                            )
                   
                    
                       
                    
                    if document:
                        result = {'status':'200', 'message':'添加成功', 'content':'none'} 
                    else:
                        result = {'status':'400', 'message':'', 'content':'none'}
            else:
                result = {'status':'400', 'message':'未收到上传数据', 'content':'none'}
        
        except Exception as e:
            log_exception() 
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result) 
        return JsonResponse(result, safe=False) 

@csrf_exempt
@authentication
def update_document(request):
    if request.method == 'POST':
        try: 
            data = request.POST.dict()
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)
            document_title = data.get('document_title')
            document_type = data.get('document_type') 
            document_id = data.get('document_id')
            files = request.FILES.getlist('document')
            urls = []
            image_url = []
            pdf_files = []
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    image_url.append(urljoin(bucket_domain, url))
                    pdf_name = conpdf(_file) 
                    pdf_files.append(pdf_name)
            
                if document_type == 'trade_contract': 
                    second_party = 'static/pdf/trade_contract/trade_contract_2.pdf'   
                    end_party = 'static/pdf/trade_contract/trade_contract_3_2.pdf'
                    if pdf_files:

                        pdf_list = pdf_files[0:1]
                        pdf_list.append(second_party)
                        pdf_list = pdf_list + pdf_files[1:]
                        pdf_list.append(end_party)
                        combine_file_name = combine_pdf(pdf_list, document_title+'.pdf')
                        for pdf in pdf_files:
                            os.remove(pdf)                    
                        combine_file = open(combine_file_name, 'rb')
                        reader = combine_file.read()
                        document_size = len(reader)
                        url = upload_file(reader, name=combine_file_name)
                        document_url = urljoin(bucket_domain, url)
                        os.remove(combine_file_name)

                        document = Documents.objects.get(id=document_id)
                        document.document_url = document_url
                        document.document_title=document_title
                        document.document_size = document_size
                        document.img_url = str(image_url)
                        document.save()
                else:
                    if pdf_files:
                        combine_file_name = combine_pdf(pdf_files, document_title+'.pdf')
                        combine_file = open(combine_file_name, 'rb')
                        reader = combine_file.read()
                        document_size = len(reader)
                        url = upload_file(reader, name=combine_file_name)
                        document_url = urljoin(bucket_domain, url)
                        for pdf in pdf_files:
                            os.remove(pdf)                    
                        os.remove(combine_file_name)

                        document = Documents.objects.get(id=document_id)
                        document.document_url = document_url
                        document.document_title=document_title
                        document.document_size = document_size
                        document.img_url = str(image_url)
                        document.save()

                   
                       
                    
                if document:
                    content = [document.get_info()]
                    result = {'status':'200', 'message':'更新成功', 'content':content} 
                else:
                    result = {'status':'400', 'message':'', 'content':'none'}
            else:
                result = {'status':'400', 'message':'未收到上传数据', 'content':'none'}
        
        except Exception as e:
            log_exception() 
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result) 
        return JsonResponse(result, safe=False) 


@csrf_exempt
def get_vip_prices(request):
    if request.method == 'POST':
        try:
            vips = Vip.objects.all().order_by('last_time')
            data = [vip.get_info() for vip in vips]
            
            result = {'status':'200','message':'获取成功', 'content':data}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
def add_version(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            files = request.FILES.getlist('apk_file')
            bucket_domain = 'http://cdn.iruyue.tv/' 
            if files:
                for _file in files:
                    url = upload_file(_file.file.read(), name=_file.name)
                    url = urljoin(bucket_domain, url)
                    
                if url:
                    data['url'] = url
                AppVersion.create(data) 
                result = {'status':'200','message':'添加成功', 'content':'none'}
            else:
                result = {'status':'400','message':'未上传apk文件', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':''}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
def get_new_version(request):
    if request.method == 'POST':
        try:
            version = AppVersion.objects.latest('code')
            content = version.get_info()
            
            result = {'status':'200','message':'获取成功', 'content':content}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
def create_contract(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data)
            contract = Contract_info.create(data)
            draw_first_page(contract)
            draw_last_page(contract)
            combine()

            result = {'status':'200','message':'创建成功', 'content':'none'}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':''}
        print(result)
        return JsonResponse(result, safe=False)

@csrf_exempt
@authentication
def make_trade_contract(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data) 
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)

            data['user'] = user

            contract = Contract_info.create(data)
            contract_type = data.get('contract_type')
            document_info = make_contract(contract, contract_type)            
            document_title = document_info.get('document_title')
            document_url = document_info.get('document_url')
            document_size = document_info.get('document_size')
            img_url = document_info.get('img_url')
            document_type = document_info.get('document_type')
            document = Documents.objects.create(document_title=document_title, 
               document_url=document_url,
               document_size = document_size,
               img_url = str(img_url),
               user=user,
               document_type=document_type
               )
            content = [document.get_info()]
            result = {'status':'200','message':'添加成功', 'content':content}
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)



def test_draw(request):
    if request.method == 'GET':
        contract = FinancingContract.objects.all()[0]
        title = make_FinancingContract(contract)
        result = {'status':'200', 'message':'', 'content':title}
        return JsonResponse(result, safe=False)
