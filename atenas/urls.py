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
from django.conf.urls import include, url, static
from django.views.generic import RedirectView, TemplateView
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
#    url("^adminatenas/", include(admin.site.urls)),

    url(r'^atenas/adminatenas/doc/', include('django.contrib.admindocs.urls')),
    url(r'^atenas/adminatenas/', include(admin.site.urls)),
    url(r'^accounts/login/$', django.contrib.auth.views.login),
    url(r'^$', comun.views.selector),

    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
               
    url(r'^presentacion_60/$', recuento.views.presentacion_60),
    url(r'^presentacion_15/$', recuento.views.presentacion_15),
    url(r'^confirmar_60/$', recuento.views.confirmar_60),
    url(r'^confirmar_15/$', recuento.views.confirmar_15),
    url(r'^alegaciones_60/$', recuento.views.alegaciones_60),
    url(r'^alegaciones_15/$', recuento.views.alegaciones_15),
    url(r'^votacion_60/$', recuento.views.votacion_60),
    url(r'^votacion_15/$', recuento.views.votacion_15),
    url(r'^comision_60/$', recuento.views.comision_60),
    url(r'^comision_15/$', recuento.views.comision_15),
    url(r'^comision_60/(?P<num>\d+)/$', recuento.views.editar_candidato_60),
    url(r'^comision_15/(?P<num>\d+)/$', recuento.views.editar_candidato_15),
    url(r'^resultado_15/$', recuento.views.resultado_15),
    url(r'^resultado_60/$', recuento.views.resultado_60),
    url(r'^ver_candidaturas_60/$', recuento.views.ver_candidatos_60),
    url(r'^ver_candidaturas_15/$', recuento.views.ver_candidatos_15),
    url(r'^envia_clave_60/$', recuento.views.envia_clave_60),
    url(r'^envia_clave_15/$', recuento.views.envia_clave_15),
    url(r'^alegar/(?P<num>\d+)/$', recuento.views.alegar),
    url(r'^alegacion_ok/$', recuento.views.alegacion_ok),
    url(r'^ok_15/$', recuento.views.ok_15),
    url(r'^ok2_15/$', recuento.views.casi_ok_15),
    url(r'^ok_60/$', recuento.views.ok_60),
    url(r'^ok2_60/$', recuento.views.casi_ok_60),
    url(r'^ver_plazos/$', TemplateView.as_view(template_name='no_hay_nada.html'), name='ver_plazos'),
    url(r'^papeleta_60/(?P<ca>\d+)/$', recuento.views.papeleta_usu_60),
    url(r'^papeleta_60/(?P<ca>\d+)/registrar/$', recuento.views.registrar_usu_60),
    url(r'^papeleta_15/(?P<ca>\d+)/$', recuento.views.papeleta_usu_15),
    url(r'^papeleta_15/(?P<ca>\d+)/registrar/$', recuento.views.registrar_usu_15),
    
    url(r'^atenas_15/$', comun.views.atenas_15),
    url(r'^atenas_60/$', comun.views.atenas_60),
    url(r'^atenas_15/recuento/$', recuento.views.selector_15),
    url(r'^atenas_60/recuento/$', recuento.views.selector_60),
    url(r'^atenas_15/papeleta/(?P<ca>\d+)/$', recuento.views.papeleta_admin_15),
    url(r'^atenas_60/papeleta/(?P<ca>\d+)/$', recuento.views.papeleta_admin_60),
    url(r'^atenas_15/papeleta/anular/(?P<ca>\d+)/$', recuento.views.anular_15),
    url(r'^atenas_60/papeleta/(?P<ca>\d+)/registrar/$', recuento.views.registrar_admin_60),
    url(r'^atenas_15/papeleta/(?P<ca>\d+)/registrar/$', recuento.views.registrar_admin_15),
    url(r'^atenas_60/papeleta/anular/(?P<ca>\d+)/$', recuento.views.anular_60),
    url(r'^atenas/login/$', django.contrib.auth.views.login),
    url(r'^atenas/logout/$', django.contrib.auth.views.logout),
    url(r'^atenas_15/verificacion/$', verificacion.views.index_15),
    url(r'^atenas_15/verificacion/registrar/(?P<id_socio>\d+)/$', verificacion.views.registrar_15),
    url(r'^atenas_15/verificacion/registrar/(?P<id_socio>\d+)/ok/$', verificacion.views.registrarOK_15),
    url(r'^atenas_15/verificacion/registroKO/(?P<id_socio>\d+)/$', verificacion.views.registrarKO_15),
    url(r'^atenas_60/verificacion/$', verificacion.views.index_60),
    url(r'^atenas_60/verificacion/registrar/(?P<id_socio>\d+)/$', verificacion.views.registrar_60),
    url(r'^atenas_60/verificacion/registrar/(?P<id_socio>\d+)/ok/$', verificacion.views.registrarOK_60),
    url(r'^atenas_60/verificacion/registroKO/(?P<id_socio>\d+)/$', verificacion.views.registrarKO_60),
]
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)