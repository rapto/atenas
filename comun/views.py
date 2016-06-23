from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone

from comun.models import Plazo
from django.shortcuts import render

@login_required(login_url='/atenas/login/')
def atenas_25(request):
    return atenas(request, 25)

@login_required(login_url='/atenas/login/')
def atenas_50(request):
    return atenas(request, 50)

def atenas(request, tipo):
    return render(request, 'index.html', dict(tipo=tipo))


def get_modulos_activos():
    now = timezone.now()
    return Plazo.objects.filter(fecha_inicio__lt=now).filter(fecha_fin__gt=now)

def is_modulo_activo(modulo):
    modulos_activos = get_modulos_activos()
    return modulos_activos.filter(modulo=modulo)
    
def selector(request):
    if request.user.is_superuser:
        return render(request, 'selector_modulo.html',
                      dict(modulos=Plazo.objects.all()))
    modulos_activos = get_modulos_activos()
    if len(modulos_activos) > 1:
        return render(request, 'selector_modulo.html',
                      dict(modulos=modulos_activos))
    if len(modulos_activos) == 1:
        modulo_activo = modulos_activos[0]
        return HttpResponseRedirect('/%s/' % modulo_activo.modulo)
    return render(request,'no_hay_nada.html')


    
