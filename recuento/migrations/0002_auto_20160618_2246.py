# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recuento', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidato',
            name='aportacion',
            field=models.IntegerField(blank=True, null=True, verbose_name='Valora, de uno a diez, tu grado de satisfacci\xf3n con tu aportaci\xf3n al Consejo', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]),
        ),
        migrations.AlterField(
            model_name='candidato',
            name='asistencia',
            field=models.ManyToManyField(to='recuento.Reunion', verbose_name='Se\xf1ala las asambleas y encuentros a las que hayas asistido en tu \xfaltimo mandato', blank=True),
        ),
        migrations.AlterField(
            model_name='candidato',
            name='fecha_sistema',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha presentaci\xf3n candidatura'),
        ),
        migrations.AlterField(
            model_name='candidato',
            name='frecuencia_acceso',
            field=models.IntegerField(blank=True, null=True, verbose_name='Con qu\xe9 frecuencia aproximada accedes a los medios de conversaci\xf3n y debate del Consejo', choices=[(1, 'Diariamente'), (2, 'Semanalmente'), (3, 'Mensualmente')]),
        ),
        migrations.AlterField(
            model_name='candidato',
            name='grupos',
            field=models.ManyToManyField(to='recuento.Grupo', verbose_name='Indica en qu\xe9 grupos has participado activamente', blank=True),
        ),
        migrations.AlterField(
            model_name='papeleta',
            name='fecha_registro',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
