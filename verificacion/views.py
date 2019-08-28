# -*- coding: utf-8 -*-

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from comun.models import Circunscripcion, Provincia
from verificacion.models import Socio, getContact, searchContacts, MultipleContactsError
from recuento.models import Consejero
from django.shortcuts import render
from django.utils.dateparse import parse_date

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
    buscado=buscado.strip()
    request.session['buscado']=buscado
    buscado=buscado.encode('utf-8')
    if buscado:
        if clase_votante is Socio:
            res = []
            infos = getContact(buscado, buscado, return_list=True)
            if not infos:
                infos = searchContacts(buscado)
            for info in infos:
                num_socio = info[u'AlizeConstituentID__c']
                income = info['Income_ultimos_12_meses_CONSEJO__c']
                fecha_alta = parse_date(info['Activation_Date__c'])
                socio, _ = Socio.objects.get_or_create(num_socio=num_socio)
                socio.correo_electronico = info['Email']
                socio.docu_id = info['DNI__c']
                socio.fecha_nacimiento = info['Birthdate']
                socio.nombre = info['Name']
                if info['MailingPostalCode']:
                    prefijo = info['MailingPostalCode'][:2]
                    try:
                        circunscripcion_por_cp = Provincia.objects.get(prefijo_cp=prefijo).circunscripcion
                    except ObjectDoesNotExist:
                        circunscripcion_por_cp = Circunscripcion.objects.get(id=18)
                else:
                    circunscripcion_por_cp = Circunscripcion.objects.get(id=18)
                socio.circunscripcion = circunscripcion_por_cp
                socio.save()
                res.append(socio)
        elif clase_votante is Consejero:
            res=clase_votante.objects
            for palabra in buscado.split():
                res=res.filter(
                    Q(apellidos__unaccent__icontains=palabra)
                    | Q(nombre__unaccent__icontains=palabra)
                ).limit(100)
    else:
        res=[]
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
