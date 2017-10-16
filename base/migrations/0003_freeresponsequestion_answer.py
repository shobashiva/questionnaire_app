# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_freeresponseanswer_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='freeresponsequestion',
            name='answer',
            field=models.CharField(default='N/A', max_length=1000),
        ),
    ]
