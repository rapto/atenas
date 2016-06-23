# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from comun.models import Circunscripcion
import datetime
from django.conf import settings
from comun import claveAleatoria

FECHA_MAXIMA = datetime.datetime(1995,9,18)


class Socio(models.Model):
    nombre=models.CharField(max_length=200)
    apellidos=models.CharField(max_length=200)
    docu_id=models.CharField(max_length=200,blank=True, verbose_name=u'Documento de identidad')
    num_socio=models.CharField(max_length=200, verbose_name=u'Número de socio/a')
    num_socio_antiguo=models.CharField(max_length=200,blank=True, null=True, verbose_name=u'Número de socio/a antiguo')
    circunscripcion=models.ForeignKey(Circunscripcion, null=True,blank=True, verbose_name=u'Circunscripción')
    fecha_socio=models.DateTimeField(null=True,blank=True, verbose_name=u'Fecha antigüedad')
    fecha_voto=models.DateTimeField(null=True,blank=True)
    fecha_nacimiento=models.DateTimeField(null=True,blank=True)
    circunscripcion_voto=models.ForeignKey(Circunscripcion, null=True,blank=True, related_name='circunscripcion_voto_50')
    usuario=models.ForeignKey(User, null=True, blank=True)
    corriente=models.BooleanField(verbose_name=u'Al corriente de pago')
    correo_electronico=models.EmailField(null=True, blank=True, verbose_name=u'Dirección de correo electrónico')
    clave=models.CharField(max_length="50", null=True, blank=True)
    def fecha_voto_legible(self):
        return self.fecha_voto.strftime("%H:%M %d-%m-%Y")
    def fecha_nacimiento_legible(self):
        if self.fecha_nacimiento:
            return self.fecha_nacimiento.strftime("%d-%m-%Y")
        return 'n/d'
    def __unicode__(self):
        return u"%s, %s" % (self.apellidos,self.nombre)
    class Meta:
        permissions = (
            ("can_verify", "Can verify identities of members"),
            ("can_mark_voted", "Can mark a member has voted"),
            ("can_register_ballot", "Can register a ballot"),
        )
        ordering = ('apellidos','nombre')
    def puedeVotar(self, electronica=False):
        if self.fecha_voto:
            return False,'Registrado voto %s' % (self.fecha_voto_legible(),)
        if self.fecha_nacimiento and self.fecha_nacimiento>FECHA_MAXIMA:
            return False, u'La fecha de nacimiento es posterior a %s' % FECHA_MAXIMA.strftime('%m-%d-%Y')
        if not self.corriente:
            return False, u'El socio no está al corriente de pago'
        if self.fecha_nacimiento==None:
            if electronica:
                return False, 'Fecha nacimiento no verificable'
            return True, 'No se dispone de fecha de nacimiento',
        return True, ''
            
    def registraVoto(self, usuario, circunscripcion_voto=None):
        assert self.puedeVotar()[0]
        self.fecha_voto=datetime.datetime.now()
        self.circunscripcion_voto_id=circunscripcion_voto or self.circunscripcion_id
        self.usuario=usuario
    def desregistraVoto(self):
        assert not self.puedeVotar()[0]
        self.fecha_voto=None
        self.circunscripcion_voto_id=None
        self.usuario=None
    def get_clave(self):
        if not self.clave or not len(self.clave)== settings.LONGITUD_CLAVE:
            self.clave = claveAleatoria()
            self.save()
        return self.clave
