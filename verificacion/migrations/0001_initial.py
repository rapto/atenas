# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-03 18:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('comun', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Socio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('apellidos', models.CharField(max_length=200)),
                ('docu_id', models.CharField(blank=True, max_length=200, verbose_name='Documento de identidad')),
                ('num_socio', models.CharField(max_length=200, verbose_name='N\xfamero de socio/a')),
                ('num_socio_antiguo', models.CharField(blank=True, max_length=200, null=True, verbose_name='N\xfamero de socio/a antiguo')),
                ('fecha_socio', models.DateTimeField(blank=True, null=True, verbose_name='Fecha antig\xfcedad')),
                ('fecha_voto', models.DateTimeField(blank=True, null=True)),
                ('fecha_nacimiento', models.DateTimeField(blank=True, null=True)),
                ('corriente', models.BooleanField(verbose_name='Al corriente de pago')),
                ('correo_electronico', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Direcci\xf3n de correo electr\xf3nico')),
                ('clave', models.CharField(blank=True, max_length=50, null=True)),
                ('circunscripcion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='comun.Circunscripcion', verbose_name='Circunscripci\xf3n')),
                ('circunscripcion_voto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='circunscripcion_voto_50', to='comun.Circunscripcion')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('apellidos', 'nombre'),
                'permissions': (('can_verify', 'Can verify identities of members'), ('can_mark_voted', 'Can mark a member has voted'), ('can_register_ballot', 'Can register a ballot')),
            },
        ),
    ]
