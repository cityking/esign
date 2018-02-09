# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-19 05:22
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esign_app', '0009_auto_20180117_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=20, null=True, verbose_name='版本')),
                ('code', models.CharField(max_length=20, verbose_name='版本号')),
                ('url', models.CharField(max_length=50, verbose_name='下载地址')),
                ('forced', models.CharField(default='0', max_length=2, verbose_name='是否强制更新')),
                ('description', models.CharField(max_length=100, verbose_name='描述')),
            ],
        ),
        migrations.AlterModelOptions(
            name='sign',
            options={},
        ),
        migrations.AlterField(
            model_name='myuser',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 19, 13, 22, 18, 519549), verbose_name='加入时间'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='total_capacity',
            field=models.FloatField(default=50000000, verbose_name='容量'),
        ),
        migrations.AlterField(
            model_name='sign',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 19, 13, 22, 18, 521784), verbose_name='创建时间'),
        ),
    ]
