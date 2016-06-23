# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('comun', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha_sistema', models.DateTimeField(default=datetime.datetime.now, verbose_name='Fecha presentaci\xf3n candidatura')),
                ('tipo', models.IntegerField(verbose_name='Convocatoria (0=No confirmada')),
                ('nombre', models.CharField(max_length=200)),
                ('apellidos', models.CharField(max_length=200)),
                ('n_socio', models.CharField(max_length=20, null=True, verbose_name='N\xba de socio/a', blank=True)),
                ('localidad', models.CharField(max_length=200)),
                ('fecha_alta', models.DateField(null=True, verbose_name='Fecha antig\xfcedad', blank=True)),
                ('descripcion', models.TextField(max_length=150, null=True, verbose_name='Breve descripci\xf3n -m\xe1ximo 150 caracteres-', blank=True)),
                ('cv', models.TextField(blank=True, max_length=1000, verbose_name='Curr\xedculum profesional -m\xe1ximo 1000 caracteres-', validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('vinculacion', models.TextField(blank=True, max_length=1000, verbose_name='Vinculaci\xf3n con Greenpeace -m\xe1ximo 1000 caracteres-', validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('motivacion', models.TextField(blank=True, max_length=1000, verbose_name='Motivaci\xf3n para presentar la candidatura -m\xe1ximo 1000 caracteres-', validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('campanha', models.TextField(blank=True, max_length=150, verbose_name='\xbfQu\xe9 campa\xf1a crees que le falta a Greenpeace Espa\xf1a y por qu\xe9? -m\xe1ximo 150 caracteres-', validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('dni', models.FileField(upload_to=b'%Y/%m/%d', verbose_name='Copia del DNI/ Pasaporte/ Tarjeta de residente')),
                ('dni_presenta', models.FileField(upload_to=b'%Y/%m/%d', null=True, verbose_name='Miembro del Consejo que presenta al candidato/a: Copia del DNI/ Pasaporte/ Tarjeta de residente', blank=True)),
                ('foto', models.ImageField(upload_to=b'%Y/%m/%d', null=True, verbose_name='Foto -m\xe1ximo 200kB-', blank=True)),
                ('correo_e', models.EmailField(max_length=254, verbose_name='Correo electr\xf3nico -para facilitar a la comisi\xf3n electoral la resoluci\xf3n de errores-')),
                ('participacion_activa', models.BooleanField(verbose_name='Compromiso de participaci\xf3n activa: Al presentar esta candidatura adquiero el compromiso, en caso de resultar elegido/a, de participar activamente en las labores que el Consejo tiene se\xf1aladas o se se\xf1alen.')),
                ('veracidad', models.BooleanField(verbose_name='Doy fe de la veracidad de los datos')),
                ('mayor_edad', models.NullBooleanField()),
                ('antiguedad_3a', models.NullBooleanField(verbose_name='Antig\xfcedad > 3 a\xf1os')),
                ('valida_sistema', models.NullBooleanField(verbose_name=b'Comprobada por el sistema')),
                ('circunscripcion_correcta', models.NullBooleanField(verbose_name='Circunscripci\xf3n correcta')),
                ('valida', models.NullBooleanField(verbose_name='Validada por la Comisi\xf3n Electoral')),
                ('comentarios', models.TextField(blank=True, max_length=1000, validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('alegaciones', models.TextField(blank=True, max_length=1000, validators=[django.core.validators.MaxLengthValidator(1000)])),
                ('en_el_consejo', models.NullBooleanField(verbose_name='Consejero en la actualidad')),
                ('frecuencia_acceso', models.IntegerField(null=True, choices=[(1, 'Diariamente'), (2, 'Semanalmente'), (3, 'Mensualmente')])),
            ],
            options={
                'ordering': ('fecha_alta', 'apellidos'),
            },
        ),
        migrations.CreateModel(
            name='Consejero',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('apellidos', models.CharField(max_length=200)),
                ('activo', models.BooleanField()),
                ('fecha_voto', models.DateTimeField(null=True, blank=True)),
                ('correo_electronico', models.EmailField(max_length=254, null=True, blank=True)),
                ('clave', models.CharField(max_length=50, null=True, blank=True)),
                ('circunscripcion_voto', models.ForeignKey(related_name='circunscripcion_voto_25', blank=True, to='comun.Circunscripcion', null=True)),
                ('usuario', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('apellidos', 'nombre'),
            },
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('orden', models.IntegerField()),
            ],
            options={
                'ordering': ('orden', 'nombre'),
            },
        ),
        migrations.CreateModel(
            name='Papeleta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha_registro', models.DateTimeField(default=datetime.datetime.now)),
                ('voto_nulo', models.BooleanField()),
                ('voto_blanco', models.BooleanField()),
                ('circunscripcion', models.ForeignKey(to='comun.Circunscripcion')),
                ('usuario_registro', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('can_register_ballot', 'Can register a ballot'),),
            },
        ),
        migrations.CreateModel(
            name='Reunion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('orden', models.IntegerField()),
            ],
            options={
                'ordering': ('orden', 'nombre'),
            },
        ),
        migrations.CreateModel(
            name='Voto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('candidato', models.ForeignKey(to='recuento.Candidato')),
                ('papeleta', models.ForeignKey(to='recuento.Papeleta')),
            ],
        ),
        migrations.AddField(
            model_name='candidato',
            name='asistencia',
            field=models.ManyToManyField(to='recuento.Reunion', verbose_name='Se\xf1ala las asambleas y encuentros a las que hayas asistido en tu \xfaltimo mandato'),
        ),
        migrations.AddField(
            model_name='candidato',
            name='circunscripcion',
            field=models.ForeignKey(verbose_name='Circunscripci\xf3n', to='comun.Circunscripcion'),
        ),
        migrations.AddField(
            model_name='candidato',
            name='grupos',
            field=models.ManyToManyField(to='recuento.Grupo', verbose_name='Se\xf1ala los grupos en los que has participado'),
        ),
        migrations.AddField(
            model_name='candidato',
            name='presenta',
            field=models.ForeignKey(verbose_name='Miembro del Consejo que presenta al candidato/a', blank=True, to='recuento.Consejero', null=True),
        ),
    ]
