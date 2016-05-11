# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-06 14:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fb_laskobot', '0002_events'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='feed',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='fb_laskobot.Feed'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='events',
            name='sent',
            field=models.BooleanField(default=False),
        ),
    ]