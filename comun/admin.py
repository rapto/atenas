from django.contrib import admin

from .models import Circunscripcion, Plazo

class CircunscripcionAdmin(admin.ModelAdmin):
        list_display=('ds', 'puestos', 'cuenta_candidatos_25', 'cuenta_candidatos_50', 'cuentaPapeletas', 'cuentaVotoBlanco', 'cuentaVotoNulo', 
            'cuentaVotantes', 'indiceParticipacion')
    
class PlazoAdmin(admin.ModelAdmin):
        list_display=('modulo', 'fecha_inicio', 'fecha_fin', 'ds')

    
admin.site.register(Circunscripcion, CircunscripcionAdmin)
admin.site.register(Plazo, PlazoAdmin)

'''
    class Admin:
        list_display=('ds', 'puestos', 'cuentaCandidatos', 'cuentaPapeletas', 'cuentaVotoBlanco', 'cuentaVotoNulo', 
            'cuentaVotantes', 'indiceParticipacion')
'''