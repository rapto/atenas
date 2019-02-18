"""atenas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import RedirectView

from django.contrib import admin
import os
import django.views
import recuento.views
import comun.views
import verificacion.views
import django.contrib.auth.views

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

admin.autodiscover()

urlpatterns = [
#    url(r'^admin/', include(admin.site.urls)),
    url("^admin/", include(admin.site.urls)),

    url(r'^atenas/adminatenas/doc/', include('django.contrib.admindocs.urls')),
#     url(r'^atenas/adminatenas/', include(admin.site.urls)),
     url(r'^accounts/login/$', django.contrib.auth.views.login),
    url(r'^$', comun.views.selector),

    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
               
    url(r'^presentacion_50/$', recuento.views.presentacion_50),
    url(r'^presentacion_25/$', recuento.views.presentacion_25),
    url(r'^confirmar_50/$', recuento.views.confirmar_50),
    url(r'^confirmar_25/$', recuento.views.confirmar_25),
    url(r'^alegaciones_50/$', recuento.views.alegaciones_50),
    url(r'^alegaciones_25/$', recuento.views.alegaciones_25),
    url(r'^votacion_50/$', recuento.views.votacion_50),
    url(r'^votacion_25/$', recuento.views.votacion_25),
    url(r'^comision_50/$', recuento.views.comision_50),
    url(r'^comision_25/$', recuento.views.comision_25),
    url(r'^comision_50/(?P<num>\d+)/$', recuento.views.editar_candidato_50),
    url(r'^comision_25/(?P<num>\d+)/$', recuento.views.editar_candidato_25),
    url(r'^resultado_25/$', recuento.views.resultado_25),
    url(r'^resultado_50/$', recuento.views.resultado_50),
    url(r'^ver_candidatos_50/$', recuento.views.ver_candidatos_50),
    url(r'^ver_candidatos_25/$', recuento.views.ver_candidatos_25),
    url(r'^envia_clave_50/$', recuento.views.envia_clave_50),
    url(r'^envia_clave_25/$', recuento.views.envia_clave_25),
    url(r'^alegar/(?P<num>\d+)/$', recuento.views.alegar),
    url(r'^alegacion_ok/$', recuento.views.alegacion_ok),
    url(r'^ok_25/$', recuento.views.ok_25),
    url(r'^ok2_25/$', recuento.views.casi_ok_25),
    url(r'^ok_50/$', recuento.views.ok_50),
    url(r'^ok2_50/$', recuento.views.casi_ok_50),

#    url(r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(SITE_ROOT,'static')}),
#    url(r'^media/(.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^papeleta_50/(?P<ca>\d+)/$', recuento.views.papeleta_usu_50),
    url(r'^papeleta_50/(?P<ca>\d+)/registrar/$', recuento.views.registrar_usu_50),
    url(r'^papeleta_25/(?P<ca>\d+)/$', recuento.views.papeleta_usu_25),
    url(r'^papeleta_25/(?P<ca>\d+)/registrar/$', recuento.views.registrar_usu_25),
    
    url(r'^atenas_25/$', comun.views.atenas_25),
    url(r'^atenas_50/$', comun.views.atenas_50),
    url(r'^atenas_25/recuento/$', recuento.views.selector_25),
    url(r'^atenas_50/recuento/$', recuento.views.selector_50),
    url(r'^atenas_25/papeleta/(?P<ca>\d+)/$', recuento.views.papeleta_admin_25),
    url(r'^atenas_50/papeleta/(?P<ca>\d+)/$', recuento.views.papeleta_admin_50),
    url(r'^atenas_25/papeleta/anular/(?P<ca>\d+)/$', recuento.views.anular_25),
    url(r'^atenas_50/papeleta/(?P<ca>\d+)/registrar/$', recuento.views.registrar_admin_50),
    url(r'^atenas_25/papeleta/(?P<ca>\d+)/registrar/$', recuento.views.registrar_admin_25),
    url(r'^atenas_50/papeleta/anular/(?P<ca>\d+)/$', recuento.views.anular_50),
    url(r'^atenas/login/$', django.contrib.auth.views.login),
    url(r'^atenas/logout/$', django.contrib.auth.views.logout),
    url(r'^atenas_25/verificacion/$', verificacion.views.index_25),
    url(r'^atenas_25/verificacion/registrar/(?P<id_socio>\d+)/$', verificacion.views.registrar_25),
    url(r'^atenas_25/verificacion/registrar/(?P<id_socio>\d+)/ok/$', verificacion.views.registrarOK_25),
    url(r'^atenas_25/verificacion/registroKO/(?P<id_socio>\d+)/$', verificacion.views.registrarKO_25),
    url(r'^atenas_50/verificacion/$', verificacion.views.index_50),
    url(r'^atenas_50/verificacion/registrar/(?P<id_socio>\d+)/$', verificacion.views.registrar_50),
    url(r'^atenas_50/verificacion/registrar/(?P<id_socio>\d+)/ok/$', verificacion.views.registrarOK_50),
    url(r'^atenas_50/verificacion/registroKO/(?P<id_socio>\d+)/$', verificacion.views.registrarKO_50),
]
