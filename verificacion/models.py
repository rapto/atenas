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

comma_params = ','.join(params)

class MultipleContactsError(RuntimeError):
    pass

def searchContacts(search_string):
    sf = Salesforce(**settings.SF_AUTH)
    response = sf.search('''find {{{}}} 
        in name fields 
        returning contact({} 
            where s360a__ContactCodes__c = 'Active Donor')
        limit 100    
        '''.format(search_string, comma_params))
    return response['searchRecords']
    
def getContact(email, dni, return_list=False):
    limit = 100 if return_list else 2
    ret = []
    sf = Salesforce(**settings.SF_AUTH)
    response = sf.query("""
        SELECT {} 
        FROM Contact 
        WHERE Email ='{}'
        AND s360a__ContactCodes__c = 'Active Donor'
        LIMIT {} """.format(comma_params, email, limit));
    objects = response['records']
    if len(objects) == 1 and not return_list:
        return objects[0]
    else:
        ret += objects
    response = sf.query("""
        SELECT {} 
        FROM Contact 
        WHERE DNI__c ='{}'
        AND s360a__ContactCodes__c = 'Active Donor'
        LIMIT {} """.format(comma_params, dni, limit));
    objects = response['records']
    if len(objects) == 1 and not return_list:
        return objects[0]
    else:
        ret += objects
    response = sf.query("""
        SELECT {}
        FROM Contact 
        WHERE DNI__c ='{}'
        AND s360a__ContactCodes__c = 'Active Donor'
        AND  Email ='{}' 
        LIMIT {} """.format(comma_params, dni, email, limit));
    objects = response['records']
    if len(objects) == 1:
        return objects[0]
    else:
        ret += objects
    if ret and not return_list:
        raise MultipleContactsError()
    return ret

class Socio(models.Model):
    nombre=models.CharField(max_length=200, null=True,blank=True)
    apellidos=models.CharField(max_length=200, null=True,blank=True)
    docu_id=models.CharField(max_length=200,blank=True, verbose_name=u'Documento de identidad')
    num_socio=models.CharField(max_length=200, verbose_name=u'Número de socio/a')
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

    @staticmethod
    def buscaVotante(buscado):
        try:
            info = getContact(buscado, buscado)
            if info:
                num_socio = info[u'AlizeConstituentID__c']
                income = info['Income_ultimos_12_meses_CONSEJO__c']
                fecha_alta = parse_date(info['Activation_Date__c'])
                today = datetime.date.today()
                meses_active = min(12, diff_month(today, fecha_alta)) 
                if income / meses_active < settings.MIN_INCOME / 12:
                    msg = u'''Cuota insuficiente'''
                if fecha_alta > settings.FECHA_CONVOCATORIA:
                    msg = u'''Para poder participar en estas elecciones necesitabas pertenecer a Greenpeace España en el momento de su convocatoria. Te esperamos en las próximas elecciones.'''
                if info['Birthdate']:
                    fecha_nacimiento = parse_date(info['Birthdate'])
                    if fecha_nacimiento > settings.FECHA_MAXIMA_NACIMIENTO:
                        msg = u'''Menor de edad'''
                elif fecha_alta > settings.FECHA_MAXIMA_NACIMIENTO:
                    msg = u'''Sin info fecha nacimiento'''
                soc_local = mv.Socio.objects.filter(num_socio=num_socio).exclude(fecha_voto=None).first()
                if soc_local:
                    msg = u'''El sistema tiene registrado tu voto en {:%d-%m-%Y %H:%M}'''.format(soc_local.fecha_voto)
            else:
                msg = u'''No encontrado'''
        except mv.MultipleContactsError:
            info = None
            msg = u'''Hay más de una persona en nuestra base de datos que cumple esta
            condición.Por favor, ponte en contacto con nuestra oficina,
            teléfono: 900 535 025, correo electrónico: sociasysocios.es@greenpeace.org.
            Cuando esté resuelto, inténtalo de nuevo. Te esperamos.'''
