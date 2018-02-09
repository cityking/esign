# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-19 05:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esign_app', '0010_auto_20180119_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appversion',
            name='url',
            field=models.CharField(max_length=100, verbose_name='下载地址'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 19, 13, 23, 34, 652029), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='sign',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 19, 13, 23, 34, 654114), verbose_name='创建时间'),
        ),
    ]
