# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_freeresponsequestion_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freeresponsequestion',
            name='answer',
        ),
        migrations.AlterField(
            model_name='freeresponseanswer',
            name='answer',
            field=models.TextField(default='N/A'),
        ),
    ]
