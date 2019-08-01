from django.contrib import admin

from .models import Circunscripcion, Plazo, Provincia

class CircunscripcionAdmin(admin.ModelAdmin):
        list_display=('ds', 'puestos', 'cuenta_candidatos_15', 'cuenta_candidatos_60', 'cuentaPapeletas', 'cuentaVotoBlanco', 'cuentaVotoNulo', 
            'cuentaVotantes', 'indiceParticipacion')
    
class PlazoAdmin(admin.ModelAdmin):
        list_display=('modulo', 'fecha_inicio', 'fecha_fin', 'ds')

class ProvinciaAdmin(admin.ModelAdmin):
        list_display=('ds', 'prefijo_cp', 'circunscripcion')

    
admin.site.register(Circunscripcion, CircunscripcionAdmin)
admin.site.register(Plazo, PlazoAdmin)
admin.site.register(Provincia, ProvinciaAdmin)

'''
    class Admin:
        list_display=('ds', 'puestos', 'cuentaCandidatos', 'cuentaPapeletas', 'cuentaVotoBlanco', 'cuentaVotoNulo', 
            'cuentaVotantes', 'indiceParticipacion')
'''
