# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luna_chatterbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chathistory',
            name='text',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
