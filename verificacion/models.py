# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from simple_salesforce import Salesforce

from comun.models import Circunscripcion
from comun import claveAleatoria

params = '''Name Income_ultimos_12_meses_CONSEJO__c
    DNI__c Birthdate AlizeConstituentID__c MailingPostalCode Email
    Fecha_de_antiguedad__c Activation_Date__c s360a__ContactCodes__c
    s360a__ContactType__c'''.split()

class MultipleContactsError(RuntimeError):
    pass

def getContact(email, dni):
    multiple = False
    sf = Salesforce(**settings.SF_AUTH)
    comma_params = ','.join(params)
    response = sf.query("""
        SELECT {} 
        FROM Contact 
        WHERE Email ='{}'
        AND s360a__ContactCodes__c = 'Active Donor'
        LIMIT 2 """.format(comma_params, email));
    objects = response['records']
    if len(objects) == 1:
        return objects[0]
    elif len(objects) > 1:
        multiple = True
    response = sf.query("""
        SELECT {} 
        FROM Contact 
        WHERE DNI__c ='{}'
        AND s360a__ContactCodes__c = 'Active Donor'
        LIMIT 2""".format(comma_params, dni));
    objects = response['records']
    if len(objects) == 1:
        return objects[0]
    elif len(objects) > 1:
        multiple = True
    response = sf.query("""
        SELECT {}
        FROM Contact 
        WHERE DNI__c ='{}'
        AND s360a__ContactCodes__c = 'Active Donor'
        AND  Email ='{}' 
        LIMIT 2""".format(comma_params, dni, email));
    objects = response['records']
    if len(objects) == 1:
        return objects[0]
    elif len(objects) > 1:
        multiple = True
    if multiple:
        raise MultipleContactsError()    
class Socio(models.Model):
    nombre=models.CharField(max_length=200, null=True,blank=True)
    apellidos=models.CharField(max_length=200, null=True,blank=True)
    docu_id=models.CharField(max_length=200,blank=True, verbose_name=u'Documento de identidad')
    num_socio=models.CharField(max_length=200, verbose_name=u'Número de socio/a')
    num_socio_antiguo=models.CharField(max_length=200,blank=True, null=True, verbose_name=u'Número de socio/a antiguo')
    circunscripcion=models.ForeignKey(Circunscripcion, null=True,blank=True, verbose_name=u'Circunscripción')
    fecha_socio=models.DateTimeField(null=True,blank=True, verbose_name=u'Fecha antigüedad')
    fecha_voto=models.DateTimeField(null=True,blank=True)
    fecha_nacimiento=models.DateTimeField(null=True,blank=True)
    circunscripcion_voto=models.ForeignKey(Circunscripcion, null=True,blank=True, related_name='circunscripcion_voto_60')
    usuario=models.ForeignKey(User, null=True, blank=True)
    correo_electronico=models.EmailField(null=True, blank=True, verbose_name=u'Dirección de correo electrónico')
    clave=models.CharField(max_length=50, null=True, blank=True)

    def fecha_voto_legible(self):
        return self.fecha_voto.strftime("%H:%M %d-%m-%Y")

    def fecha_nacimiento_legible(self):
        if self.fecha_nacimiento:
            return self.fecha_nacimiento.strftime("%d-%m-%Y")
        return 'n/d'
    def __unicode__(self):
        return u"%s, %s" % (self.apellidos or '',self.nombre or '')

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
