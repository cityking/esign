# coding:utf-8
import random
import urllib.parse
import urllib.request
from datetime import datetime

from hashlib import md5
#from wallet.RedisConnector import RedisConnector
from .myredis import MyRedis


class PhoneNumberVerificator():
    # 短信网关配置
    def __init__(self):
        self.www_sms_com_API = {
            'vender': 'sms.com',
            'url': 'http://api.sms.cn/mtutf8/',
            'method': 'GET',
            'arguments_Record': {   # 已备案账号
                'uid': 'jetcloudtech',
                # pwd=md5('Admin2013jetcloudtech') 即md5(密码+用户名)
            'pwd': 'b3ffc483776c653a0e4d6e97f38bedc2',
                'mobile': '',
                'content': ''
            },
            'arguments': {
                'uid': 'jctadmin',  # 未备案账号
                # pwd=md5('Admin2014jctadmin') 即md5(密码+用户名)
                'pwd': 'a4659ff67fd595fbdb59b7e9f16af830',
                'mobile': '',
                'content': '',
            },
            'status': {
                '100': '发送成功',
                '101': '验证失败',
                '102': '短信不足',
                '103': '操作失败',
                '104': '非法字符',
                '105': '内容过多',
                '106': '号码过多',
                '107': '频率过快',
                '108': '号码内容空',
                '109': '账号冻结',
                '110': '禁止频繁单条发送',
                '112': '号码不正确',
                '120': '系统升级'
            }
        }
        self.SMSConfig = {
            'api': self.www_sms_com_API,
            'verification':
            '您的注册验证码：%s,请尽快填写完成注册。【众筹】'
        }
        # 另外一个短信接口的配置信息
        self.url = 'http://www.ztsms.cn/sendNSms.do?'
        self.username = 'jetcloudtech'
        self.productid = '95533'
        self.tkey = datetime.now().strftime('%Y%m%d%H%M%S')
        self.password = md5(
                    (md5('Vr9ztsmszpwd'.encode()).hexdigest() + self.tkey).encode()
                ).hexdigest()

#        self.connect = RedisConnector()

    # 用来检测手机号码是否合法,合法返回:"True"，否则："False"
    def phonecheck(self, phone_number):
        # 号码前缀，如果运营商启用新的号段，只需要在此列表将新的号段加上即可。
        phoneprefix = ['13', '14', '15', '17', '18']
        # 检测号码是否长度是否合法
        if len(phone_number) != 11:
            return False
        else:
            # 检测输入的号码是否全部是数字。
            if phone_number.isdigit():
                # 检测前缀是否是正确。
                if phone_number[:2] in phoneprefix:
                    return True
                else:
                    return False
            else:
                return False

    def VerificationCode(self):
        ''' 随机生成4位的验证码 '''
        code_list = []
        for i in range(10):  # 0-9数字
            code_list.append(int(i))
        code_list = random.sample(code_list, 4)  # 从list中随机获取4个元素
        int_slice = \
            code_list[0] * 1000 + \
            code_list[1] * 100 + \
            code_list[2] * 10 + \
            code_list[3] * 1
        if int_slice >= 1000:
            str_slice = str(int_slice)
        elif int_slice <= 999 and int_slice:
            str_slice = '0' + str(int_slice)
        elif int_slice <= 99 and int_slice >= 10:
            str_slice = '00' + str(int_slice)
        elif int_slice <= 9 and int_slice >= 1:
            str_slice = '000' + str(int_slice)
        else:
            str_slice = '0000'
        return str_slice

    # 发送短信验证码
    def sendMsg(self, tel, code):
        try:
            # 增加产品
            try:
                data = {
                    'mobile': str(tel),
                    'content': str(code),
                }
                if data['content'] == '' or data['mobile'] == '':
                    print ('验证码或手机号为空')
            except Exception as e:
                raise e  # 参数错误
            api_url = self.SMSConfig['api']['url']

            # 调用已备案接口
            data['content'] = \
                self.SMSConfig['verification'] % data['content']
            args = self.SMSConfig['api']['arguments_Record']
            # URL编码的方式:把需要编码的字符转化为 %xx 的形式
            args['content'] = urllib.parse.quote(data['content'])
            args['mobile'] = data['mobile']
            # 拼URL参数
            strArgs = '?'
            for (k, v) in args.items():
                # 以？开头，后面用&相连
                strArgs += ('&' if strArgs != '?' else '') + ('%s=%s' % (k, v))
            api_url += strArgs
            # print(api_url)
            response = urllib.request.urlopen(api_url)
            body = (response.read()).decode()
            # print(body)
            return body
        except Exception as e:
            raise e

    # 另一个短信发送方法
    def send(self, tel, content):
        data = {'username': self.username,
                'tkey': self.tkey,
                'password': self.password,
                'mobile': tel,
                'content': urllib.parse.quote(content),
                'productid': self.productid,
                'xh': '',
                }
        url_now = self.url + '&'.join('%s=%s' % (k, data[k]) for k in data)
        rsp = urllib.request.urlopen(url_now)
        print(rsp.read(), url_now)
        if rsp.read().decode() == '1':
            return 'success'
        else:
            return 'fail'

    # 把发送的验证码和手机号配对存入redis
    def writeCodeToRedis(self, code, mobile, time):
        key = 'mobile' + mobile
        redis = MyRedis()
        redis.set(key, code)
        redis.expire(key, time)
        if redis.get(key):
            return True 
        else:
            return False
        
        
        


    # 对键值对进行验证
    def CheckVerificationCode(self, mobile, inputCode):
        # 根据键名获取值
        key = 'mobile' + mobile
        redis = MyRedis()
        code = redis.get(key)
        if code:
            # 把取出来的验证码解码，看是否与收到的验证码吻合
            if code == inputCode:
                return True
            # 如果不吻合
            else:
                return False
        # 如果没取到
        else:
            return False

if __name__ == "__main__":
    pnv = PhoneNumberVerificator()
    phone_number = '18221339272'
    code = pnv.VerificationCode()
    print (code)
    msg_type = ''
    msg = "你正在进行众筹实名认证，验证码为%s" % code
    if pnv.phonecheck(phone_number):
#        pnv.sendMsg(phone_number, code)
        pnv.send(phone_number, msg)
