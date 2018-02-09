from django.db import models
from django.db import models
from django.contrib.auth import login, logout, authenticate
from tools.tool import make_password, make_identity, trans_to_localtime
from tools.myredis import MyRedis
import datetime
import urllib
import requests
import json

class Vip(models.Model):
    last_time = models.IntegerField(default=0, verbose_name='持续时间')
    ori_price = models.FloatField(default=0, verbose_name='原价')
    now_price = models.FloatField(default=0, verbose_name='现价')
    class Meta:
        verbose_name = 'vip信息'
        verbose_name_plural = verbose_name

    def get_info(self):
        return dict(last_time=self.last_time,
                ori_price=self.ori_price,
                now_price=self.now_price,
                vip_id = self.id)
class MyUser(models.Model):
    password = models.CharField(max_length=32, null=True, verbose_name='密码')
    avatar_url = models.CharField(max_length=300, null=True, verbose_name='用户头像')
    nick_name = models.CharField(max_length=300, null=True, verbose_name='用户昵称')
    join_date = models.DateTimeField(default=datetime.datetime.now(), verbose_name='加入时间')
    phone = models.CharField(max_length=32, null=True, unique=True, verbose_name='手机号')
    sex = models.CharField(max_length=10, default='男', verbose_name='性别')
    birthday = models.CharField(max_length=20, null=True, verbose_name='生日')
    region = models.CharField(max_length=32, null=True, verbose_name='地区')
    level = models.CharField(max_length=32, default='free', verbose_name='等级')
    state = models.IntegerField(default=0, verbose_name='0:开启；1：禁用')
    total_capacity = models.FloatField(default=50000000, verbose_name='容量')
#    vip_end_date = models.DateTimeField(null=True, verbose_name='vip过期时间')
    left_time = models.IntegerField(default=0, verbose_name='剩余时间')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nick_name

    def get_capacity(self):
        used_capacity = Documents.get_user_capacity(self)
        return dict(used_capacity=used_capacity,
                total_capacity=self.total_capacity)

    def get_info(self):
        used_capacity = Documents.get_user_capacity(self)
        return dict(user_id=self.id,
                left_time=self.left_time,
                phone = self.phone,
                avatar_url=self.avatar_url,
                nick_name=self.nick_name,
                level=self.level,
                used_capacity=used_capacity,
                total_capacity=self.total_capacity
                )
    def get_detail(self):
        return dict(user_id=self.id,
                phone = self.phone,
                avatar_url=self.avatar_url,
                nick_name=self.nick_name,
                sex = self.sex,
                birthday = self.birthday,
                region = self.region,
                )
    def update(self, data):
        nickname = data.get('nickname')
        if nickname:
            self.nick_name = nickname
        sex = data.get('sex')
        if sex:
            self.sex = sex
        birthday = data.get('birthday')
        if birthday:
            self.birthday = birthday
        region = data.get('region')
        if region:
            self.region = region
        self.save()
        return self


    @classmethod
    def login(cls, phone, password):
        if phone:
            user = cls.objects.filter(phone=phone)
        else:
            return '1'
        if user:
            user = user[0]
            password = make_password(password)
            if user.password and password == user.password:
                identity = make_identity(phone, user)
                return identity
            else:
                return '0'
        else:
             return '1'
    @classmethod
    def get_user_by_identity(cls, identity):
        redis = MyRedis()
        key = 'identity_user' + identity
        user_id = redis.get(key) 
        if user_id:
            user = cls.objects.get(id=user_id)
            if user:
                return user
            else:
                return None
        else:
             return None
class Documents(models.Model):
    document_title = models.CharField(max_length=100, null=True, verbose_name='标题')
    document_url = models.CharField(max_length=300, null=True, verbose_name='文档地址')
    img_url = models.CharField(max_length=1500, null=True, verbose_name='图片地址')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,verbose_name='用户')
    is_collected = models.CharField(max_length=10, default='0', verbose_name='是否收藏')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#    mobile = models.CharField(max_length=32, null=True, unique=True, verbose_name='手机号')
    document_size = models.FloatField(default=0, verbose_name='文档大小')
    is_signed = models.CharField(max_length=10, default='0', verbose_name='是否签名') #'0'未签名 '1'已签名
    document_type = models.CharField(max_length=20, default='trade_contract', verbose_name='文档类型')
    

    class Meta:
        verbose_name = '文档信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.document_title
    def get_info(self):
        create_time = trans_to_localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        img_url = eval(self.img_url)
        return dict(document_id=self.id,
                document_title=self.document_title,
                create_time=create_time,
                document_size=self.document_size,
                document_url=self.document_url,
                img_url = img_url,
                document_type = self.document_type,
                is_collected = self.is_collected,
                demo_type = ''
                )
    def add_collect(self):
        self.is_collected = '1'
        self.save()
    def cancel_collect(self):
        self.is_collected = '0'
        self.save()
    @classmethod
    def get_documents_by_user(cls, user):
        documents = cls.objects.filter(user=user).order_by('-create_time')
        return [document.get_info() for document in documents]
    @classmethod
    def get_user_capacity(cls, user):
        documents = cls.objects.filter(user=user)
        capacity = 0
        for document in documents:
            capacity += document.document_size
        return capacity 

    @classmethod
    def get_collected_by_user(cls, user):
        documents = cls.objects.filter(user=user).filter(is_collected='1')
        return [document.get_info() for document in documents]
class Sign(models.Model):
    sign_url = models.CharField(max_length=300, null=True, verbose_name='签名地址')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,verbose_name='用户')
    is_default = models.CharField(max_length=10, default='0', verbose_name='是否为默认')
    create_time = models.DateTimeField(default=datetime.datetime.now(), verbose_name='创建时间')

    class meta:
        verbose_name = '签名信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sign_url
    def get_info(self):
        return dict(sign_id=self.id,sign_url=self.sign_url,is_default=self.is_default)

    def set_default(self):
        user = self.user
        default_sign = Sign.objects.filter(user=user).filter(is_default='1')
        if default_sign:
            default_sign[0].is_default='0'
            default_sign[0].save()
        self.is_default = '1'
        self.save()

    @classmethod
    def get_sign_by_user(cls, user):
        signs = cls.objects.filter(user=user).order_by('-id')
        sign_list = [sign.get_info() for sign in signs]
        return sign_list
class AppVersion(models.Model):
    version = models.CharField(max_length=20, null=True, verbose_name='版本')
    code = models.CharField(max_length=20,verbose_name='版本号')
    url = models.CharField(max_length=500, verbose_name='下载地址')
    forced = models.CharField(max_length=2, default='0', verbose_name='是否强制更新')
    description = models.CharField(max_length=500, verbose_name='描述')

    class meta:
        verbose_name = '版本信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.version
    def get_info(self):
        return dict(version=self.version,
                code=self.code,
                url=self.url,
                forced=self.forced,
                description = self.description
                )

    @classmethod
    def create(cls, data):
        apk = cls.objects.create(version=data.get('version'),
                code=data.get('code'),
                url=data.get('url'),
                forced=data.get('forced'),
                description=data.get('description'))
class Trade_contract(models.Model):
    first_party = models.CharField(max_length=20, null=True, verbose_name='甲方')
    address = models.CharField(max_length=100, null=True, verbose_name='联系地址')
    phone = models.CharField(max_length=11, null=True, verbose_name='联系电话')
    application_scene = models.CharField(max_length=100, null=True, verbose_name='应用场景')
    date1 = models.CharField(max_length=20, null=True, verbose_name='日期')
    date2 = models.CharField(max_length=20, null=True, verbose_name='日期')
    trade_accounts = models.CharField(max_length=200, null=True, verbose_name='交易宝账号')
    user = models.ForeignKey(MyUser, null=True, on_delete=models.CASCADE,verbose_name='用户')

    class meta:
        verbose_name = '交易宝合同信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.first_party
   
    @classmethod
    def create(cls, data):
        first_party = data.get('first_party')
        address = data.get('address')
        phone = data.get('phone')
        application_scene = data.get('application_scene')
        date1 = data.get('calendarX')
        date2 = data.get('calendarY')
        user = data.get('user')
        trade_accounts = data.get('trade_accounts')
        contract = cls.objects.create(first_party=first_party,
                address=address,
                phone=phone,
                application_scene=application_scene,
                date1=date1,
                date2=date2,
                user=user,
                trade_accounts=trade_accounts)
        return contract
class Contract_info():
    def create(data): 
        if data['contract_type'] == 'trade_contract':
            return Trade_contract.create(data)
        else:
            return FinancingContract.create(data)
class FinancingContract(models.Model):
    first_party = models.CharField(max_length=20, null=True, verbose_name='甲方')
    ID_card = models.CharField(max_length=18, null=True, verbose_name='身份证号')
    address = models.CharField(max_length=100, null=True, verbose_name='联系地址')
    phone = models.CharField(max_length=11, null=True, verbose_name='联系电话')
    copies = models.IntegerField(default=1, verbose_name='投资份数')
    money_upper = models.CharField(max_length=100, null=True, verbose_name='投资金额大写(万元)')
    money = models.FloatField(default=0, verbose_name='投资金额')
    start_date = models.CharField(max_length=20, null=True, verbose_name='起投日期')
    account_holder8 = models.CharField(max_length=20, null=True, verbose_name='开户人')
    account_bank8 = models.CharField(max_length=20, null=True, verbose_name='开户行')
    account8 = models.CharField(max_length=20, null=True, verbose_name='账号')
    account_holder10 = models.CharField(max_length=20, null=True, verbose_name='开户人')
    account_bank10 = models.CharField(max_length=20, null=True, verbose_name='开户行')
    account10 = models.CharField(max_length=20, null=True, verbose_name='账号')
    create_date = models.CharField(max_length=20, null=True, verbose_name='签订日期')
    pay_method = models.CharField(max_length=2, default='1', verbose_name='付款方式') #'1'银行转账， '2' 现金
    contract_type = models.CharField(max_length=30, null=True, verbose_name='合同种类')
    user = models.ForeignKey(MyUser, null=True, on_delete=models.CASCADE,verbose_name='用户')

    class meta:
        verbose_name = '合同信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.first_party
   
    @classmethod
    def create(cls, data):
        first_party = data.get('first_party')
        ID_card = data.get('ID_card')
        copies = data.get('copies')
        money_upper = data.get('money_upper')
        money = data.get('money')
        start_date = data.get('start_date')
        account_holder8 = data.get('account_holder8')
        account_bank8 = data.get('account_bank8')
        account8 = data.get('account8')
        account_holder10 = data.get('account_holder10')
        account_bank10 = data.get('account_bank10')
        account10 = data.get('create_date')
        create_date = data.get('create_date')
        pay_method = data.get('pay_method')
        if not pay_method:
            pay_method = '1'
        contract_type = data.get('contract_type')
        address = data.get('address')
        phone = data.get('phone')
        user = data.get('user')
        contract = cls.objects.create(first_party=first_party,
                address=address,
                phone=phone,
                user=user,
                ID_card=ID_card,
                copies=copies,
                money_upper=money_upper,
                money=money,
                start_date=start_date,
                account_holder8=account_holder8,
                account_bank8=account_bank8,
                account8=account8,
                account_holder10=account_holder10,
                account_bank10=account_bank10,
                account10=account10,
                create_date=create_date,
                pay_method=pay_method,
                contract_type=contract_type,
                )
        return contract
class Contract_demo(models.Model):     
    demo_name = models.CharField(max_length=300, null=True, verbose_name='模版名称')
    demo_url = models.CharField(max_length=300, null=True, verbose_name='模版地址')  
    demo_type = models.CharField(max_length=300, default='trade_contract', verbose_name='模版类型')
    size = models.FloatField(default=3000000, verbose_name='容量')
    class meta:
        verbose_name = '合同模版'
        verbose_name_plural = verbose_name

    def get_info(self):
        return dict(document_id=self.id,
                document_title=self.demo_name,
                create_time='',
                document_size=self.size,
                document_url=self.demo_url,
                img_url = [],
                is_collected = '0',
                document_type = 'demo',
                demo_type = self.demo_type 
                )
    @classmethod
    def get_list(cls):
        demo_list = cls.objects.all()
        return [demo.get_info() for demo in demo_list]


    def __str__(self):
        return self.demo_name
class Order(models.Model):    
    methods = (('0','支付宝支付'),('1', '微信支付'))
    results = (('0','交易失败'),('1', '交易成功'))
    order_id = models.CharField(max_length=50, primary_key=True, verbose_name='订单号')
    trade_info = models.CharField(max_length=50, null=True, verbose_name='交易信息')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,verbose_name='用户')
    trade_money = models.FloatField(default=0,verbose_name='交易金额')

    vip = models.ForeignKey(Vip, on_delete=models.CASCADE,verbose_name='vip信息')
    trade_time = models.DateTimeField(auto_now_add=True, verbose_name='交易时间')
    trade_method = models.CharField(max_length=1, choices=methods, default='1', verbose_name='交易方式')
    trade_result = models.CharField(max_length=1, choices=results, default='0', verbose_name='交易结果')
    status = models.CharField(max_length=50, default='normal', verbose_name='状态') #normal正常 deleted已删除
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def get_bref_info(self):
        order_id = self.order_id
        trade_time = self.get_trade_time() 
        info = dict(order_id=order_id,
                trade_time=trade_time)
        return info

    def get_trade_time(self):
        return trans_to_localtime(self.trade_time).strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_list(cls):
        orders = cls.objects.filter(status='normal').order_by('-trade_time')
        order_list = [order.get_bref_info() for order in orders]
        return order_list

    def delete(self):
        self.status = 'deleted'
        self.save()

    @classmethod
    def get_user_orders(cls, user, status=None):
        pass

    @classmethod
    def create(cls, data):
        pass

    def __str__(self):
        return self.order_id

