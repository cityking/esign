import datetime
import time
import json
import random
import string
import urllib.parse

import rsa
import base64
import requests
from .alipay_conf import ALIPAY_PUB_KEY, APP_PRI_KEY, APP_PUB_KEY


class Alipay(object):
    def __init__(self):
        # 公共参数
        self.conf = dict(
            app_id='2018011101770924',
            charset='utf-8',
            sign_type='RSA2',
            version='1.0',
            # notify_url='http://120.25.159.143:8001/consumer/alipay_callback/',
            notify_url='http://city.king:9000/consumer/alipay_callback/',
        )
        # 秘钥
        self.ali_pub_key = ALIPAY_PUB_KEY
        self.app_pri_key = APP_PRI_KEY
        self.app_pub_key = APP_PUB_KEY

        # 支付宝通知链接地址
        self.alipay_url = 'https://mapi.alipay.com/gateway.do'
        self.refund_url = 'https://openapi.alipay.com/gateway.do'

    def RAS_sign(self, string):
        """传入字符串:需encode():"""
        private_key = rsa.PrivateKey.load_pkcs1(self.app_pri_key)
#        private_key = self.app_pri_key

        sign = rsa.sign(string.encode(), private_key, 'SHA-256')
        return base64.b64encode(sign).decode('utf-8')

    @staticmethod
    def nonce_str():
        char = string.ascii_letters + string.digits
        return "".join(random.choice(char) for _ in range(32))

    def dict_sort(self, raw):
        """字典排序"""
        raw = [(k, str(raw[k]) if isinstance(raw[k], int) else raw[k])
               for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        return s

    def get_sign(self, dict_object):
        return self.RAS_sign(self.dict_sort(dict_object))

    def app_pay(self, dict_object):
        """
        :param dict_object:
                    out_trade_no
                    total_amount
        :return: dict
        """
        # 业务参数
        dict_object['product_code'] = 'QUICK_MSECURITY_PAY'
        #dict_object['subject'] = '电子签名vip升级'
        # dict_object['timeout_express'] = '30m'
        # dict_object['seller_id'] = 'tdjshun@126.com'
        #dict_object['seller_id'] = 'zhangyufeng@jetcloudtech.com'
        data = self.conf
        # 添加公共参数
        data['method'] = 'alipay.trade.app.pay'
        data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['biz_content'] = json.dumps(dict_object)
        # 拼接
        sign_string = self.dict_sort(data)
        # 签名
        sign = self.RAS_sign(sign_string)
        # 对所有一级参数 url_encode
        for k, v in data.items():
            data[k] = urllib.parse.quote(v)
        # 把 sign url_encode 加在排序的后面
        return self.dict_sort(data) + '&sign=' + urllib.parse.quote(sign)

    def refund(self, unit_no, refund_amount):
        out_request_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + \
                         str(time.time()).replace('.', '')[-4:]
        dict_object = {
            'out_trade_no': unit_no,
            'refund_amount': str(refund_amount),
            'out_request_no': out_request_no,  # 分次退款订单号
        }
        # 添加公共参数
        data = self.conf
        data['method'] = 'alipay.trade.refund'
        data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['biz_content'] = json.dumps(dict_object)
        # 拼接
        sign_string = self.dict_sort(data)
        # 签名
        data['sign'] = self.RAS_sign(sign_string)
        r = requests.get(url=self.refund_url, params=data).json()
        print('退款回调', r)
        return r['alipay_trade_refund_response'], out_request_no
        # # 验签
        # d = r['alipay_trade_refund_response']
        # sign_string = self.dict_sort(d)
        # print(sign_string)
        # # sign_string = 'alipay_trade_refund_response=' + json.dumps(r['alipay_trade_refund_response'])
        # sign = r['sign']
        # try:
        #     pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(self.ali_pub_key)
        #     base_sign = base64.b64decode(sign)
        #     if rsa.verify(sign_string.encode(), base_sign, pubkey):
        #         print("----------verify sign success----------")
        #         return r['alipay_trade_refund_response']
        # # except rsa.pkcs1.VerificationError:
        # except:
        #     print("----------verify sign failed----------")
        #     return {'code': '10001'}

    # 验证签名
    def verify_sign(self, dict_object):
        if not len(dict_object) > 0:
            return False
        sign_type = dict_object.pop('sign_type')
        sign = dict_object.pop('sign')
        sign_string = self.dict_sort(dict_object)

        if sign_type.upper() == "RSA2":
            try:
                pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(self.ali_pub_key)
                base_sign = base64.b64decode(sign)
                if rsa.verify(sign_string.encode(), base_sign, pubkey):
                    print("----------verify sign success----------")
                    return True
            # except rsa.pkcs1.VerificationError:
            except:
                print("----------verify sign failed----------")
                return False
        else:
            # 支付宝当前仅支持 RSA 加密，未来也许会有其他类型
            return False
        return False

    # 验证是否是支付宝发来的通知
    def verify_url(self, partner, notify_id):
        """
        :param partner: 卖家支付宝用户ID。 seller_id
        :param notify_id: 通知校验ID
        :return:
        """
        payload = {'service': 'notify_verify', 'partner': partner, 'notify_id': notify_id}
        r = requests.get(self.alipay_url, params=payload)
        result = r.text
        print('11111', r.text)
        if result.upper() == "TRUE":
            print("----------verify url success----------")
            return True
        return False

# # 支付宝充值回调
# def alipay(request):
#     if request.method == 'POST':
#         if not len(request.POST) > 0:
#             return HttpResponse(status=400)
#         print("****************")
#         print(request.POST)
#         # 验证签名 sign
#         if verifySignString(request.POST):
#             print(request.POST)
#             try:
#                 notify_id = request.POST['notify_id']
#                 parter = request.POST['seller_id']
#                 trade_status = request.POST['trade_status']
#                 out_trade_no = request.POST['out_trade_no']
#                 # amt = request.POST['price']
#                 amt = request.POST['total_amount']  # 对账账户
#             except:
#                 return HttpResponse(status=404)
#             # 验证是否是支付宝发来的通知
#             if verifyURL(parter, notify_id):
#                 if trade_status == 'TRADE_SUCCESS':
#                     pass  # 处理成功支付
#                     return HttpResponse("success")
#                 elif trade_status == 'WAIT_BUYER_PAY':
#                     return HttpResponse("success")
#                 elif trade_status == 'TRADE_CLOSED':
#                     payment = Payment.objects.filter \
#                         (order_id=out_trade_no).first()
#                     print(payment.user.mobile)
#                     payment.status = 3
#                     payment.pay_info += ' 交易关闭'
#                     payment.save()
#                     return HttpResponse("success")
#                 else:
#                     return HttpResponse(status=400)
#     return HttpResponse(status=400)
