# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-29 06:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esign_app', '0018_auto_20180126_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='订单号')),
                ('trade_info', models.CharField(max_length=50, null=True, verbose_name='交易信息')),
                ('trade_money', models.FloatField(default=0, verbose_name='交易金额')),
                ('trade_time', models.DateTimeField(auto_now_add=True, verbose_name='交易时间')),
                ('trade_method', models.CharField(choices=[('0', '支付宝支付'), ('1', '微信支付')], default='1', max_length=1, verbose_name='交易方式')),
                ('trade_result', models.CharField(choices=[('0', '交易失败'), ('1', '交易成功')], default='0', max_length=1, verbose_name='交易结果')),
                ('status', models.CharField(default='normal', max_length=50, verbose_name='状态')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
            },
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 29, 14, 32, 9, 988672), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='sign',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 29, 14, 32, 9, 992146), verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='esign_app.MyUser', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='order',
            name='vip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='esign_app.Vip', verbose_name='vip信息'),
        ),
    ]
