# -*- coding: utf-8 -*-

from django.db.models import Q
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from comun.models import Circunscripcion
from verificacion.models import Socio
from recuento.models import Consejero
from django.shortcuts import render

@permission_required('verificacion.verify')
def registrar_60(request, id_socio):
    return registrar(request, id_socio, 60, Socio)

@permission_required('verificacion.verify')
def registrar_15(request, id_socio):
    return registrar(request, id_socio, 15, Consejero)

def registrar(request, id_socio, tipo, clase_votante):
    circunscripciones=Circunscripcion.objects.all()
    socio=clase_votante.objects.get(pk=id_socio)
    return render(request, 'registrar.html', locals())

@permission_required('verificacion.can_mark_voted')
def registrarKO_15(request, id_socio):
    return registrarKO(request, id_socio, 15, Consejero)

@permission_required('verificacion.can_mark_voted')
def registrarKO_60(request, id_socio):
    return registrarKO(request, id_socio, 60, Socio)

def registrarKO(request, id_socio, tipo, clase_votante):
    assert request.method=='POST'
    socio=clase_votante.objects.filter(usuario=request.user).order_by('-fecha_voto')[0]
    assert int(id_socio)==socio.id
    socio.desregistraVoto()
    socio.save()
    return HttpResponseRedirect('../../')

@permission_required('verificacion.can_mark_voted')
def registrarOK_15(request, id_socio):
    return registrarOK(request, id_socio, 15, Consejero)

@permission_required('verificacion.can_mark_voted')
def registrarOK_60(request, id_socio):
    return registrarOK(request, id_socio, 60, Socio)

def registrarOK(request, id_socio, tipo, clase_votante):
    assert request.method=='POST'
    socio=clase_votante.objects.get(pk=id_socio)
    circunscripcion_voto=request.POST.get('circunscripcion_voto', 18)
    try:
        socio.registraVoto(request.user, circunscripcion_voto)
    except AssertionError:
        return HttpResponseRedirect('../../')
    socio.save()
    return HttpResponseRedirect('../../../')
    

@permission_required('verificacion.can_verify')
def index_15(request):
    return index(request, 15, Consejero)

@permission_required('verificacion.can_verify')
def index_60(request):
    return index(request, 60, Socio)

def index(request, tipo, clase_votante):
    try:
        ultimosocio=clase_votante.objects.filter(usuario=request.user).order_by('-fecha_voto')[0]
    except IndexError:
        ultimosocio=None
    buscado=request.GET.get('buscado',request.session.get('buscado', '' ))
    if isinstance(buscado,str):
        buscado=unicode(buscado,'utf8')
    buscado=buscado.upper().strip()
    buscado=buscado.replace(u'ñ',u'Ñ')
    buscado=buscado.replace(u'á',u'A')
    buscado=buscado.replace(u'é',u'É')
    buscado=buscado.replace(u'í',u'I')
    buscado=buscado.replace(u'ó',u'O')
    buscado=buscado.replace(u'ú',u'U')
    buscado=buscado.replace(u'Á',u'A')
    buscado=buscado.replace(u'É',u'É')
    buscado=buscado.replace(u'Í',u'I')
    buscado=buscado.replace(u'Ó',u'O')
    buscado=buscado.replace(u'Ú',u'U')

    request.session['buscado']=buscado
    buscado=buscado.encode('utf-8')
    if buscado:
        if clase_votante is Socio:
            res=clase_votante.objects.filter(
                    Q(num_socio__contains=buscado)
                    | Q(docu_id__contains=buscado)
                    )
        if clase_votante is Consejero or res.count()==0:
            res=clase_votante.objects
            for palabra in buscado.split():
                res=res.filter(
                    Q(apellidos__icontains=palabra)
                    | Q(nombre__icontains=palabra)
                )
    else:
        res=[]
    res=res[:100]
    if tipo == 15:
        circunscripciones=Circunscripcion.objects.filter(pk=18)
    else:
        circunscripciones=Circunscripcion.objects.all()
    c=dict(res=res,
        ultimosocio=ultimosocio,
        buscado=buscado,
        circunscripciones=circunscripciones,
        tipo=tipo,
        )
    return render(request, 'verificacion.html', c)
