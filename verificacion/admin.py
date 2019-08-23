from models import Socio
from django.contrib import admin


class SocioAdmin(admin.ModelAdmin):
    list_display=('nombre','apellidos','num_socio','circunscripcion')
    list_filter=('circunscripcion',)
    search_fields = ['nombre','apellidos','num_socio']

admin.site.register(Socio, SocioAdmin)
