# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-24 06:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esign_app', '0014_auto_20180124_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='img_url',
            field=models.CharField(max_length=1500, null=True, verbose_name='图片地址'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 24, 14, 46, 27, 670884), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='sign',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 24, 14, 46, 27, 673116), verbose_name='创建时间'),
        ),
    ]