from .models import Candidato, Papeleta, Voto, Consejero, Reunion, Grupo
from django.contrib import admin


class SimpleAdmin(admin.ModelAdmin):
    list_display=('__unicode__', 'orden')
    
class CandidatoAdmin(admin.ModelAdmin):
    #fieldsets=[(None, {'fields':['nombre','apellidos','circunscripcion','orden']})]
    list_display=('__unicode__','circunscripcion', 'valida','fecha_sistema','cuentaVotos','tipo')
    list_filter=('circunscripcion', 'tipo', 'valida')
    search_fields = ['nombre','apellidos']


class VotoAdmin(admin.ModelAdmin):
    list_display=('papeleta','candidato', )


class PapeletaAdmin(admin.ModelAdmin):
    list_display=('circunscripcion','usuario_registro','fecha_registro',)


class ConsejeroAdmin(admin.ModelAdmin):
    list_display=('__unicode__', 'correo_electronico', 'fecha_voto')


admin.site.register(Candidato, CandidatoAdmin)
admin.site.register(Reunion, SimpleAdmin)
admin.site.register(Grupo, SimpleAdmin)
admin.site.register(Papeleta, PapeletaAdmin)
admin.site.register(Voto, VotoAdmin)
admin.site.register(Consejero, ConsejeroAdmin)
