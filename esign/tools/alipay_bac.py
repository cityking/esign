import OpenSSL  
import json  
import time  
import urllib  
import base64  
 
class Alipay(object):
    def __init__(self, appid, app_private_key, alipay_public_key, method, notify_url, version, product_code):
        self.appid = appid,
        self.app_private_key = app_private_key,
        self.format = 'json'
        self.charset = 'UTF-8'
        self.alipay_public_key = alipay_public_key
        self.sign_type = 'RSA'
        self.method = method
        self.notify_url = notify_url
        self.version = version
        self.product_code = product_code
    def build_params(self, out_trade_no, subject, body, total_amount):  
        ''''' 
        Doc：https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.MVkRGo&treeId=193&articleId=105465&docType=1 
        将参数按照支付宝规定组织并签名之后，返回 
        '''  
        params = {}  
        # 获取配置文件  
        params['app_id']            = self.appid  
        params['method']            = self.method  
        params['format']            = self.format  
        params['charset']           = self.charset  
        params['sign_type']         = self.sign_type  
        params['timestamp']         = time.strftime('%Y-%m-%d %H:%M:%S')  
        params['version']           = self.version  
        params['notify_url']        = self.notify_url  
          
        # 业务参数  
        params['biz_content'] = {}  
        params['biz_content']['body']              = body           # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里  
        params['biz_content']['subject']           = subject        # 商品的标题/交易标题/订单标题/订单关键字等。  
        params['biz_content']['out_trade_no']      = out_trade_no   # 商户网站唯一订单号      
        params['biz_content']['total_amount']      = '%.2f' % (float(total_amount) / 100)   # 订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000]      
        params['biz_content']['product_code']      = self.product_code  
        params['biz_content']                      = json.dumps(params['biz_content'], separators=(',', ':'))  
          
        params['sign'] = self.build_sign(params)  
          
        return urllib.urlencode(params)  
 
    def build_sign(self, param_map):  
        ''''' 
        Doc: https://doc.open.alipay.com/doc2/detail.htm?treeId=200&articleId=105351&docType=1 
        '''  
        # 将筛选的参数按照第一个字符的键值ASCII码递增排序（字母升序排序），如果遇到相同字符则按照第二个字符的键值ASCII码递增排序，以此类推。  
        sort_param = sorted([(key, unicode(value, self.charset).encode(self.charset)) for key, value in param_map.items()], key=lambda x: x[0])  
        # 将排序后的参数与其对应值，组合成“参数=参数值”的格式，并且把这些参数用&字符连接起来，此时生成的字符串为待签名字符串。SDK中已封装签名方法，开发者可直接调用，详见SDK说明。  
        # 如自己开发，则需将待签名字符串和私钥放入SHA1 RSA算法中得出签名（sign）的值。  
        content = '&'.join(['='.join(x) for x in sort_param])  
        return base64.encodestring(OpenSSL.crypto.sign(self.app_private_key, content, 'sha1'))  
    def check_sign(self, message, sign):  
       '''''Doc: https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.dDRpeK&treeId=204&articleId=105301&docType=1'''  
       try:  
           OpenSSL.crypto.verify(self.alipay_public_key, sign, message, 'SHA1')  
           return True  
       except Exception as _:  
           return False                
         
 
 

