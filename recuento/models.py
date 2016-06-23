# coding=UTF-8
from django.db import models
from django.contrib.auth.models import User
from comun.models import Circunscripcion

from django.utils import timezone
from django.conf import settings
from comun import claveAleatoria
from django.core.validators import MaxLengthValidator


class Consejero(models.Model):
    nombre=models.CharField(max_length=200)
    apellidos=models.CharField(max_length=200)
    activo = models.BooleanField()
    usuario=models.ForeignKey(User, null=True, blank=True)
    circunscripcion_voto=models.ForeignKey(Circunscripcion, null=True,blank=True, related_name='circunscripcion_voto_25')
    fecha_voto=models.DateTimeField(null=True,blank=True)
    correo_electronico=models.EmailField(null=True, blank=True)
    clave=models.CharField(max_length=50, null=True, blank=True)
    def fecha_voto_legible(self):
        return self.fecha_voto.strftime("%H:%M %d-%m-%Y")
    def __unicode__(self):
        return u"%s %s" % (self.nombre, self.apellidos)
    class Meta:
        ordering = ('apellidos','nombre')
    def puedeVotar(self, electronica=False):
        if not self.activo:
            return False, u'No activo'
        if self.fecha_voto:
            return False,u'Registrado voto %s' % (self.fecha_voto_legible(),)
        return True, ''
            
    def registraVoto(self, usuario, circunscripcion_voto=None):
        assert self.puedeVotar()[0]
        self.circunscripcion_voto_id=18
        self.usuario=usuario
        self.fecha_voto=timezone.now()

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

class Reunion(models.Model):
    nombre = models.CharField(max_length=200)
    orden = models.IntegerField()
    class Meta:
        ordering = ('orden', 'nombre')
    
    def __unicode__(self):
        return self.nombre
    
class Grupo(models.Model):
    nombre = models.CharField(max_length=200)
    orden = models.IntegerField()
    class Meta:
        ordering = ('orden', 'nombre')
    
    def __unicode__(self):
        return self.nombre
    
class Candidato(models.Model):
    fecha_sistema = models.DateTimeField(default=timezone.now, verbose_name=u'Fecha presentación candidatura')
    tipo = models.IntegerField(verbose_name=u'Convocatoria (0=No confirmada')
    nombre=models.CharField(max_length=200)
    apellidos=models.CharField(max_length=200)
    presenta = models.ForeignKey(Consejero, null=True, blank=True, verbose_name=u'Miembro del Consejo que presenta al candidato/a')
    n_socio=models.CharField(max_length=20, verbose_name=u"Nº de socio/a",blank=True, null=True)
    localidad=models.CharField(max_length=200)
    circunscripcion=models.ForeignKey(Circunscripcion, verbose_name=u"Circunscripción")
    fecha_alta=models.DateField(blank=True, null=True, verbose_name=u'Fecha antigüedad')
    descripcion=models.TextField(max_length=150, verbose_name=u"Breve descripción -máximo 150 caracteres-",blank=True, null=True)
    cv=models.TextField(max_length=1000, blank=True, verbose_name=u'Currículum profesional -máximo 1000 caracteres-',
                        validators=[MaxLengthValidator(1000)])
    vinculacion=models.TextField(max_length=1000, blank=True, verbose_name=u'Vinculación con Greenpeace -máximo 1000 caracteres-',
                        validators=[MaxLengthValidator(1000)])
    motivacion=models.TextField(max_length=1000, blank=True, verbose_name=u'Motivación para presentar la candidatura -máximo 1000 caracteres-',validators=[MaxLengthValidator(1000)])
    campanha=models.TextField(max_length=150, blank=True, verbose_name=u'¿Qué campaña crees que le falta a Greenpeace España y por qué? -máximo 150 caracteres-',validators=[MaxLengthValidator(1000)])
    dni = models.FileField(upload_to="%Y/%m/%d", verbose_name=u'Copia del DNI/ Pasaporte/ Tarjeta de residente')
    dni_presenta=models.FileField(upload_to="%Y/%m/%d", verbose_name=u'Miembro del Consejo que presenta al candidato/a: Copia del DNI/ Pasaporte/ Tarjeta de residente', null=True, blank = True)
    foto=models.ImageField(upload_to="%Y/%m/%d", verbose_name=u'Foto -máximo 200kB-', null=True, blank = True)
    correo_e=models.EmailField(verbose_name=u'Correo electrónico -para facilitar a la comisión electoral la resolución de errores-')
    participacion_activa=models.BooleanField(verbose_name=u'Compromiso de participación activa: Al presentar esta candidatura adquiero el compromiso, en caso de resultar elegido/a, de participar activamente en las labores que el Consejo tiene señaladas o se señalen.')
    veracidad=models.BooleanField(verbose_name=u'Doy fe de la veracidad de los datos')
    mayor_edad=models.NullBooleanField()
    antiguedad_3a=models.NullBooleanField(verbose_name=u'Antigüedad > 3 años')
    valida_sistema=models.NullBooleanField(verbose_name='Comprobada por el sistema')
    circunscripcion_correcta=models.NullBooleanField(verbose_name=u'Circunscripción correcta')
    valida=models.NullBooleanField(verbose_name=u'Validada por la Comisión Electoral')
    comentarios=models.TextField(max_length=1000, blank=True,
                        validators=[MaxLengthValidator(1000)])
    alegaciones=models.TextField(max_length=1000, blank=True,
                        validators=[MaxLengthValidator(1000)])
    en_el_consejo = models.BooleanField(verbose_name=u'Consejero en la actualidad')
    asistencia = models.ManyToManyField(Reunion, blank=True, verbose_name=u'Señala las asambleas y encuentros a las que hayas asistido en tu último mandato')
    grupos = models.ManyToManyField(Grupo, blank=True, verbose_name=u'Indica en qué grupos has participado activamente')
    frecuencia_acceso = models.IntegerField(null=True, blank=True, choices=[
                                (1, u'Diariamente'),
                                (2, u'Semanalmente'),
                                (3, u'Mensualmente'),
                                ],
                                verbose_name=u'Con qué frecuencia aproximada accedes a los medios de conversación y debate del Consejo'
                                )
    aportacion = models.IntegerField(null=True, blank=True, choices=[(n,n) for n in range(1,11)],
                                verbose_name=u'Valora, de uno a diez, tu grado de satisfacción con tu aportación al Consejo'
                                )
    
    def cuentaVotos(self):
        return self.voto_set.count()
    def __unicode__(self):
        return u"%s %s" % (self.nombre, self.apellidos)
    class Meta:
        ordering = ('fecha_alta','apellidos')
    

class Papeleta(models.Model):
    circunscripcion = models.ForeignKey(Circunscripcion)
    usuario_registro = models.ForeignKey(User, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    voto_nulo = models.BooleanField(blank=True)
    voto_blanco = models.BooleanField(blank=True)
    #socio_votante = models.ForeignKey(Socio, null=True)
    def __unicode__(self):
        return u'%s %s %s' % (self.circunscripcion, self.usuario_registro, self.fecha_registro)
    class Meta:
        permissions = (
            ("can_register_ballot", "Can register a ballot"),
        )
    def listaCandidatos(self):
        ret=list(self.voto_set.all())
        ret.sort(key=lambda x:x.candidato.fecha_alta)
        return ret
class Voto(models.Model):
    candidato=models.ForeignKey(Candidato)
    papeleta=models.ForeignKey(Papeleta)
    def __unicode__(self):
        return u'%s %s' % (self.candidato, self.papeleta)
    
