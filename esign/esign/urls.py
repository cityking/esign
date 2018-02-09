"""esign URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from esign_app.views import *
from esign_app import tests
from webchat.views import unified_order, alipayback

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #注册
    url(r'^esign/register', register),
    #获取验证码
    url(r'^esign/get_certification_code', get_certification_code),
    #登录
    url(r'^esign/login', user_login),
    #更改密码
    url(r'^esign/update_password', update_user_password),
    #更改用户信息
    url(r'^esign/update_userinfo', update_userinfo),
    #更改用户头像
    url(r'^esign/update_avatar', update_avatar),
    #获取用户容量
    url(r'^esign/get_user_capacity', get_user_capacity),



    #我的文档
    url(r'^esign/get_documents', get_documents),
    #文档删除
    url(r'^esign/delete_document', delete_document),
    #收藏文档
    url(r'^esign/collect_document', collect_document),
    #删除文档
    url(r'^esign/delete_collected', delete_collected),
    #获取我的收藏列表
    url(r'^esign/get_collected', get_collected),
    #获取用户信息
    url(r'^esign/get_userinfo', get_userinfo),
    #获取vip价格列表
    url(r'^esign/get_vip_prices', get_vip_prices),
    #获取用户详细信息
    url(r'^esign/get_userdetails', get_userdetails),
 
    #获取我的签名
    url(r'^esign/get_mysign', get_mysign),
    #添加签名
    url(r'^esign/add_sign', add_sign),
    #删除签名
    url(r'^esign/delete_sign', delete_sign),
    #设置默认签名
    url(r'^esign/set_default_sign', set_default_sign),
    #新建文档
    url(r'^esign/add_document', add_document),
    #更新文档
    url(r'^esign/update_document', update_document),


    #添加版本
    url(r'^esign/add_version', add_version),
    #获取最新版本
    url(r'^esign/get_new_version', get_new_version),
    #创建合同
    url(r'^esign/make_trade_contract', make_trade_contract),
    

    #统一下单
    url(r'^esign/unified_order', unified_order),
    #支付宝回调
    url(r'^esign/alipayback', alipayback),

    #测试
    url(r'^esign/test', test_draw),
]
