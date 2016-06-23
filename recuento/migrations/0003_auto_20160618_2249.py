# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recuento', '0002_auto_20160618_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidato',
            name='en_el_consejo',
            field=models.BooleanField(default=True, verbose_name='Consejero en la actualidad'),
            preserve_default=False,
        ),
    ]
