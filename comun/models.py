# coding=UTF-8
from django.db import models

class Circunscripcion(models.Model):
    ds=models.CharField(max_length=200)
    alize=models.CharField(max_length=200)
    cod_ine = models.CharField(max_length=2)
    puestos=models.IntegerField()
    orden=models.IntegerField()
    def __unicode__(self):
        return self.ds
    def cuentaPapeletas(self):
        return self.papeleta_set.count()
    def cuentaPapeletasVerificadas(self):
        if self.id == 18:
            return self.circunscripcion_voto_25.count()
        return self.circunscripcion_voto_50.count()
    def cuentaVotoBlanco(self):
        return self.papeleta_set.filter(voto_blanco=True).count()
    def cuentaVotoNulo(self):
        return self.papeleta_set.filter(voto_nulo=True).count()
    def cuentaVotantes(self):
        return self.socio_set.count()
    def indiceParticipacion(self):
        if self.cuentaVotantes():
            ret = round(100.0 * self.cuentaPapeletas()/self.cuentaVotantes(),2)
            return ('%0.2f'%(ret,)).replace('.',',')
        else:
            return 'n/a'

    def candidatos_ordenados(self):
        return self.candidato_set.filter(valida=True).order_by('fecha_alta')

    def candidatos_ordenados_por_voto(self):
        ret = list(self.candidato_set.filter(valida=True, tipo__gt=0))
        ret.sort(key=lambda c:(-c.cuentaVotos(), c.fecha_alta))
        for n, c in enumerate(ret):
            c.electo = (n < (self.puestos or 25) and c.cuentaVotos())
        return ret
            
    def candidatos_ordenados_50(self):
        return self.candidatos_ordenados().filter(tipo=50)

    def cuenta_candidatos_50(self):
        return self.candidatos_ordenados_50().count()
    
    def candidatos_ordenados_25(self):
        return self.candidatos_ordenados().filter(tipo=25)
    
    def cuenta_candidatos_25(self):
        return self.candidatos_ordenados_25().count()
    

    class Meta:
        ordering = ('orden','ds')

class Provincia(models.Model):
    ds=models.CharField(max_length=200)
    prefijo_cp = models.CharField(max_length=2)
    circunscripcion=models.ForeignKey(Circunscripcion, verbose_name=u"Circunscripción")
    
class Plazo(models.Model):
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    modulo = models.CharField(max_length=200)
    ds = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.ds

    class Meta:
        ordering = ('fecha_fin',)
