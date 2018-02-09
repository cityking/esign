import json
from dateutil.relativedelta import relativedelta
from tools.WXpay import WeixinPay
from esign_app.models import MyUser
from django.shortcuts import render
from django.db.utils import IntegrityError
from django.http import JsonResponse
from tools.tool import make_password, log_exception, authentication, upload_file,bucket_domain, del_uploaded
from django.views.decorators.csrf import csrf_exempt
from esign_app.models import *
from urllib.parse import urljoin
from tools.WXpay import create_pay
from tools.alipay import Alipay
import os
import time
import random

# Create your views here.
appid = 'wxb17d421b05f1eee0'
mch_id = '1497383901'
mch_key = 'hjukuuihdjkkkkksdhfhfhjjkaksebeb'
notify_url = 'http://city.king:8999/webchat/unified_order'

@csrf_exempt
@authentication
def unified_order(request):
    if request.method == 'POST':
        try:
            data = request.body.decode()
            data = json.loads(data) 
            identity = data.get('identity')
            user = MyUser.get_user_by_identity(identity)

            vip_id = data.get('vip_id')
            vip = Vip.objects.get(id=vip_id)
            order_id = str(user.id) + str(int(time.time())) + str(random.Random().randint(999,10000))
            if vip.last_time == 1:
                trade_info = '升级一个月会员'
            elif vip.last_time == 12:
                trade_info = '升级12个月会员'
            trade_money = vip.now_price
            trade_method = data.get('trade_method')
            order = Order.objects.create(vip=vip,
                    order_id = order_id,
                    user=user,
                    trade_info = trade_info,
                    trade_money = trade_money,
                    trade_method = trade_method
                    )

            if order.trade_method == '1':

                pay = create_pay()            
                
                order_info = dict(
#                       product_id= vip.id,
                       body = order.trade_info,
                       out_trade_no = order.order_id,
                       total_fee = int(order.trade_money*100),
                       spbill_create_ip = data['spbill_create_ip'],
                       trade_type = 'APP'
#                       trade_type = 'NATIVE'
                        ) 
                raw = pay.unified_order(order_info) 
                print(raw)
                if raw.return_code=='SUCCESS' and raw.result_code=='SUCCESS': 
                    prepay_id = raw.prepay_id
                    package = 'Sign=WXPay'
                    appid = pay.app_id
                    partnerid = pay.mch_id
                    noncestr = raw.nonce_str
                    timestamp = str(int(time.time()))
                    content = dict(
                           appid=appid,
                           partnerid=partnerid,
                           prepayid=prepay_id,
                           pack=package,
                           noncestr=noncestr,
                           timestamp=timestamp,
                            )
                    sign=pay.sign(content)
                    content['sign'] = sign
                    result = {'status':'200','message':'添加成功', 'content':content}
                else:
                    print(raw)
                    content = raw 
                    result = {'status':'400', 'message':'', 'content': content}
                    pass
            elif order.trade_method == '0':
                subject = order.trade_info
                out_trade_no = order.order_id
                total_amount = order.trade_money
                info = dict(subject=subject,
                        out_trade_no=out_trade_no,
                        total_amount=total_amount)
                pay = Alipay()
                content = pay.app_pay(info)
                result = {'status':'200','message':'添加成功', 'content':content}



 
        except Exception as e:
            log_exception()
            result = {'status':'400', 'message':'', 'content':'none'}
        print(result)
        return JsonResponse(result, safe=False)

 # 支付宝充值回调
def alipayback(request):
    if request.method == 'POST':
        if not len(request.POST) > 0:
            return HttpResponse(status=400)
        print("****************")
        print(request.POST)
        # 验证签名 sign
        if verifySignString(request.POST):
            print(request.POST)
            try:
                notify_id = request.POST['notify_id']
                parter = request.POST['seller_id']
                trade_status = request.POST['trade_status']
                out_trade_no = request.POST['out_trade_no']
                # amt = request.POST['price']
                amt = request.POST['total_amount']  # 对账账户
            except:
                return HttpResponse(status=404)
            # 验证是否是支付宝发来的通知
            if verifyURL(parter, notify_id):
                if trade_status == 'TRADE_SUCCESS':
                    datenow = datetime.datetime.now()
                    vip_end_date = datenow + relativedelta(months=+1)
                    pass  # 处理成功支付
                    return HttpResponse("success")
                elif trade_status == 'WAIT_BUYER_PAY':
                    return HttpResponse("success")
                elif trade_status == 'TRADE_CLOSED':
                    payment = Payment.objects.filter \
                        (order_id=out_trade_no).first()
                    print(payment.user.mobile)
                    payment.status = 3
                    payment.pay_info += ' 交易关闭'
                    payment.save()
                    return HttpResponse("success")
                else:
                    return HttpResponse(status=400)
    return HttpResponse(status=400)
