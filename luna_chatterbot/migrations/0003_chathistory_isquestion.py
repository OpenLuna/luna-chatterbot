# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luna_chatterbot', '0002_auto_20160511_0805'),
    ]

    operations = [
        migrations.AddField(
            model_name='chathistory',
            name='isQuestion',
            field=models.BooleanField(default=True),
        ),
    ]
