# -*- coding: utf-8 -*-
from itertools import groupby

from comun.ratelimitcache import ratelimit_post
from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mail
from django.core.validators import EmailValidator, ValidationError
from django.db import connection, transaction
from django.db.models.aggregates import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.dateparse import parse_date
from recuento import models as m
from recuento.models import Candidato, Consejero, Papeleta
from django.conf import settings
from verificacion import models as mv

import datetime
from django.contrib import messages
from recuento.forms import NuevoCandidatoForm, NuevoCandidatoConfirmacionForm,\
    AlegacionForm, NuevoCandidato15Form, AdminCandidatoForm
from django.forms.widgets import Select
from comun.views import is_modulo_activo
from comun.models import Circunscripcion, Provincia, Plazo


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

@permission_required('recuento.can_register_ballot')
def selector_15(request):
    return selector(request, 15)

@permission_required('recuento.can_register_ballot')
def selector_60(request):
    return selector(request, 60)

def selector(request, tipo):
    circ_singular = Circunscripcion.objects.get(pk=18)
    if tipo == 15:
        papeletas = Papeleta.objects.filter(circunscripcion__id=18
                                            ).order_by('-fecha_registro')[:5]
        ccaa = Circunscripcion.objects.filter(id=18)
    else:
        papeletas = Papeleta.objects.all().order_by('-fecha_registro')[:5]
        ccaa = m.Circunscripcion.objects.all()
    return render(request, 'selector.html', 
                  dict(ccaa=ccaa,
                       papeletas=papeletas,
                       tipo=tipo))

def votacion_15(request):
    return votacion(request, 15, Consejero)

def votacion_60(request):
    return votacion(request, 60, mv.Socio)

def votacion(request, tipo, clase_votantes):
    if not is_modulo_activo('votacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    if request.method!="POST":
        return render(request, 'login.html', dict(tipo=tipo))
    clave=request.POST['clave']
    try:
        socio=clase_votantes.objects.get(clave=clave)
    except clase_votantes.DoesNotExist:
        mensaje = u'Verifique el identificador, por favor'
        messages.add_message(request, messages.INFO, mensaje) 
        return render(request, 'login.html', dict(tipo=tipo))
    puedeVotar, msg = socio.puedeVotar(True)
    if not puedeVotar:
        messages.add_message(request, messages.WARNING, u'No puede votar: %s' % msg)
        return HttpResponseRedirect('/')
    request.session['usu%s' % tipo]=socio.pk
    if tipo == 15:
        return HttpResponseRedirect('/papeleta_%s/%s/' % (tipo, 18))
    if tipo == 60 and socio.circunscripcion.pk!=18:
        return HttpResponseRedirect('/papeleta_%s/%s/' % (tipo, socio.circunscripcion.pk))
    else:
        return render(request, 'selector_usu.html',
                      dict(tipo=tipo,
                           ccaa=m.Circunscripcion.objects.all()))

def ultimaPapeleta(user,circ):
    try:
        ultimo=m.Papeleta.objects.filter(usuario_registro=user).filter(circunscripcion=circ).order_by('-fecha_registro')[0]
    except IndexError:
        ultimo=None
    return ultimo

def papeleta_usu_60(request, ca):
    return papeleta_usu(request, ca, 60, mv.Socio)

def papeleta_usu_15(request, ca):
    return papeleta_usu(request, ca, 15, Consejero)

def papeleta_usu(request, ca, tipo, clase_votantes):
    if not is_modulo_activo('votacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    usu=request.session.get('usu%s' % tipo)
    if not usu:
        return HttpResponseRedirect("/")
    socio=clase_votantes.objects.get(pk=usu)
    puedeVotar, msg = socio.puedeVotar(True)
    if not puedeVotar:
        mensaje=u'No puede votar en esta web; intente votar por correo postal: '+msg
        messages.add_message(request, messages.SUCCESS, mensaje)
        return render(request, 'mensaje_pub.html')
    circ=m.Circunscripcion.objects.get(pk=ca)
    plantilla = 'papeleta_pub.html'
    if tipo == 60:
        max_candidatos = circ.puestos
        assert socio.circunscripcion.pk == 18 or socio.circunscripcion == circ
    else:
        max_candidatos = settings.MAX_CANDIDATOS_15
    return render(request, plantilla, locals())

def papeleta_admin_15(request, ca):
    return papeleta_admin(request, ca, 15, settings.MAX_CANDIDATOS_15)

def papeleta_admin_60(request, ca):
    circ=m.Circunscripcion.objects.get(pk=ca)
    return papeleta_admin(request, ca, 60, circ.puestos)

def papeleta_admin(request, ca, tipo, puestos):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")
    circ = m.Circunscripcion.objects.get(pk=ca)
    ultimo = request.user.is_authenticated() and ultimaPapeleta(request.user,circ)
    return render(request, 'papeleta.html', locals())

@transaction.atomic    
@permission_required('recuento.can_register_ballot')
def anular_15(request,ca):
    return anular(request, ca, 15)
@transaction.atomic    
@permission_required('recuento.can_register_ballot')
def anular_60(request,ca):
    return anular(request, ca, 60)

def anular(request,ca, tipo):
    circ=m.Circunscripcion.objects.get(pk=ca)
    assert request.method=='POST'
    ultimo=ultimaPapeleta(request.user,circ)
    assert int(request.POST['ultimo'])==ultimo.id, repr(request.POST['ultimo'])+'!='+repr(ultimo.id)
    ultimo.voto_set.all().delete()
    ultimo.delete()
    return HttpResponseRedirect('/atenas_%s/papeleta/%s/' % (tipo, ca))

@transaction.atomic
def registrar_usu_60(request,ca):
    return registrar_usu(request, ca, 60, mv.Socio)

@transaction.atomic
def registrar_usu_15(request,ca):
    return registrar_usu(request, ca, 15, Consejero)

# ya está en la llamada @transaction.atomic
def registrar_usu(request,ca, tipo, clase_votantes):
    if not is_modulo_activo('votacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    if request.method=="GET":
        return HttpResponseRedirect('/')
    id_usu=request.session.get('usu%s' % tipo)
    if not id_usu:
        return HttpResponseRedirect("/")
    circ=m.Circunscripcion.objects.get(pk=ca)
    usu= clase_votantes.objects.get(pk=id_usu)
    if tipo == 60:
        assert usu.circunscripcion_id==18 or circ.pk==usu.circunscripcion_id, 'Se está votando por una circ no autorizada'
    puedeVotar, msg = usu.puedeVotar(True)
    if not puedeVotar:
        messages.add_message(request, messages.WARN, 'No puede votar: '+msg)
        return HttpResponseRedirect('/')
    usu.fecha_voto=datetime.datetime.now()
    usu.save()
    papeleta=m.Papeleta(circunscripcion=circ,
        usuario_registro=request.user.is_authenticated() and request.user or None)
    aspas=[int(v) for k,v in request.POST.items() if k.startswith('cdto')]
    if tipo == 60:
        max_candidatos = circ.puestos
    else:
        max_candidatos = settings.MAX_CANDIDATOS_15
    assert len(aspas)<=max_candidatos, u'No se puede votar a más candidatos que puestos'
    if request.POST.get('nulo'):
        assert not aspas, u'Aspas y nulo'
        papeleta.voto_nulo=True
        papeleta.voto_blanco=False
    elif request.POST.get('blanco'):
        assert not aspas, u'Aspas y blanco'
        papeleta.voto_blanco=True
        papeleta.voto_nulo=False
    else:
        assert aspas, u'Ni aspas ni blanco'
        papeleta.voto_blanco = False
        papeleta.voto_nulo = False
    papeleta.save()
    for aspa in aspas:
        candidato=m.Candidato.objects.get(pk=aspa)
        #Sólo en caso de hostilidad
        assert candidato.circunscripcion.pk==circ.pk, u'Se está votando por candidatos de otra papeleta'
        voto=m.Voto(candidato=candidato, papeleta=papeleta)
        voto.save()
    msg = u'<span style="font-size:300%;color:green;">Voto registrado</span>'
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect('/')

@transaction.atomic
def registrar_admin_60(request, ca):
    return registrar_admin(request, ca, 60)

@transaction.atomic
def registrar_admin_15(request, ca):
    return registrar_admin(request, ca, 15)

def registrar_admin(request, ca, tipo):
    if not is_modulo_activo('recuento_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    if request.method=="GET":
        return HttpResponseRedirect('/')
    id_usu=request.session.get('usu%s' % tipo)
    if not request.user.is_authenticated() and not id_usu:
        return HttpResponseRedirect("../..")
    circ=m.Circunscripcion.objects.get(pk=ca)
    papeleta=m.Papeleta(circunscripcion=circ,
        usuario_registro=request.user.is_authenticated() and request.user or None)
    aspas=[int(v) for k,v in request.POST.items() if k.startswith('cdto')]
    if tipo == 60:
        assert len(aspas) <= circ.puestos, u'No se puede votar a más candidatos que puestos'
    else:
        assert len(aspas) <= settings.MAX_CANDIDATOS_15
    if request.POST.get('nulo'):
        assert not aspas, u'Aspas y nulo'
        papeleta.voto_nulo=True
        papeleta.voto_blanco=False
    elif request.POST.get('blanco'):
        assert not aspas, u'Aspas y blanco'
        papeleta.voto_blanco=True
        papeleta.voto_nulo=False
    else:
        assert aspas, u'Ni aspas ni blanco'
        papeleta.voto_blanco = False
        papeleta.voto_nulo = False
    papeleta.save()
    for aspa in aspas:
        candidato=m.Candidato.objects.get(pk=aspa)
        #Sólo en caso de hostilidad
        assert candidato.circunscripcion.pk==circ.pk, u'Se está votando por candidatos de otra papeleta'
        
        voto=m.Voto(candidato=candidato)
        papeleta.voto_set.add(voto)
        voto.save()
    if not id_usu and request.user.is_authenticated():
        return HttpResponseRedirect('./../')
    msg = u'<span style="font-size:300%;color:green;">Voto registrado</span>'
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect('.')

@transaction.atomic
@ratelimit_post(minutes = 3, requests = 10)
def envia_clave_60(request):
    return envia_clave(request, 60, mv.Socio)

@transaction.atomic
@ratelimit_post(minutes = 3, requests = 10)
def envia_clave_15(request):
    return envia_clave(request, 15, Consejero)

def envia_clave(request, tipo, clase_votantes):
    if not is_modulo_activo('votacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    if request.method!="POST":
        return HttpResponseRedirect('/')
    email = request.POST.get('email')
    if not email:
        return HttpResponseRedirect('/votacion_%s/' % tipo)
    info = mv.getContact(email, email)
    msg = ''
    if info:
        num_socio = info[u'AlizeConstituentID__c']
        income = info['Income_ultimos_12_meses_CONSEJO__c']
        fecha_alta = parse_date(info['Activation_Date__c'])
        today = datetime.date.today()
        meses_active = min(12, diff_month(today, fecha_alta)) 
        if income / meses_active < settings.MIN_INCOME / 12:
            msg = u'''Parece que hay algún problema con el pago de tu cuota,
            por favor, ponte en contacto con nuestra oficina, teléfono: 900 535 025,
            correo electrónico:
            <a href="mailto:sociasysocios.es@greenpeace.org">sociasysocios.es@greenpeace.org</a>.
            Cuando esté resuelto, inténtalo de nuevo. Te esperamos.'''
        if info['Birthdate']:
            fecha_nacimiento = parse_date(info['Birthdate'])
            if fecha_nacimiento > settings.FECHA_MAXIMA_NACIMIENTO:
                msg = u'''Para poder participar en estas elecciones necesitabas ser mayor de edad
                en el momento de la convocatoria. Te esperamos en las próximas elecciones'''
        else:
            msg = u'''Para poder votar necesitas tener fecha de nacimiento en la base de 
            datos. Por favor, ponte en contacto con nuestra oficina, teléfono: 900 535 025, 
            correo electrónico: sociasysocios.es@greenpeace.org o actualízala en
             Tu perfil greenpeace. Cuando esté resuelto, inténtalo de nuevo. Te esperamos.'''
        try:
            EmailValidator()(info['Email'])
        except ValidationError:
            msg = u'''Para poder votar electrónicamente, necesitamos que tengas una dirección de correo electrónico registrada en la base de datos de Greenpeace España para enviarte la clave. Por favor, ponte en contacto con nuestra oficina, teléfono: 900 535 025, correo electrónico: sociasysocios.es@greenpeace.org. Cuando esté resuelto, inténtalo de nuevo. Te esperamos.'''
        if fecha_alta > settings.FECHA_CONVOCATORIA:
            msg = u'''Para poder participar en estas elecciones necesitabas pertenecer a Greenpeace España en el momento de su convocatoria. Te esperamos en las próximas elecciones.'''
        soc_local = mv.Socio.objects.filter(num_socio=num_socio).exclude(fecha_voto=None).first()
        if soc_local:
            msg = u'''El sistema tiene registrado tu voto en {:%d-%m-%Y %H:%M}'''.format(soc_local.fecha_voto)
    else:
        msg = u'''No hay ninguna persona en nuestra base de datos que cumpla esta condición.
        Por favor, ponte en contacto con nuestra oficina, teléfono: 900 535 025,
        correo electrónico: <a href="mailto:sociasysocios.es@greenpeace.org">sociasysocios.es@greenpeace.org</a>.
        Cuando esté resuelto, inténtalo de nuevo. Te esperamos.'''
    
    if msg == '':
        socio, created = mv.Socio.objects.get_or_create(num_socio=num_socio)
        socio.correo_electronico = info['Email']
        socio.nombre = info['Name']
        if info['MailingPostalCode']:
            prefijo = info['MailingPostalCode'][:2]
            circunscripcion_por_cp = Provincia.objects.get(prefijo_cp=prefijo).circunscripcion
        else:
            circunscripcion_por_cp = Provincia.objects.get(id=18)
        socio.circunscripcion = circunscripcion_por_cp
        socio.save()
        email_text = u'Estimado/a %s\r\nÉsta es tu clave: %s\r\nPuedes votar en https://elecciones.greenpeace.es' % (socio.nombre, socio.get_clave())
        send_mail(u"[Greenpeace España/Elecciones] Clave para votar ", email_text, 'no-reply@greenpeace.es', [socio.correo_electronico], 
              fail_silently= False)
        msg = u'Por favor, verifica tu buzón de correo. En breve te llegará un mensaje con la clave para votar.'
        level = messages.SUCCESS
    else:
        level = messages.WARNING
    messages.add_message(request, level, msg)
    return HttpResponseRedirect('/votacion_%s/' % tipo)

@ratelimit_post(minutes = 3, requests = 10)
def presentacion_60(request):
    return presentacion(request, 60)

@ratelimit_post(minutes = 3, requests = 10)
def presentacion_15(request):
    return presentacion(request, 15)

def presentacion(request, tipo):
    if not is_modulo_activo('presentacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    plantilla = 'presentacion.html'
    form_class = NuevoCandidatoForm if tipo==60 else NuevoCandidato15Form
    if request.method == 'POST': # If the form has been submitted...
        form = form_class(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid():
            candidato = form.save(commit=False)
            candidato.descripcion = candidato.descripcion or '-'
            candidato.tipo = 0
            if tipo == 15:
                candidato.circunscripcion_id = 18
            candidato.valida = None
            candidato.save()
            request.session['id_candidato'] = candidato.id
            return HttpResponseRedirect('/confirmar_%s/' % tipo)
    else:
        form = form_class() # An unbound form

    return render(request, plantilla, dict(form=form))

@ratelimit_post(minutes = 3, requests = 10)
def confirmar_60(request):
    return confirmar(request, 60)

@ratelimit_post(minutes = 3, requests = 10)
def confirmar_15(request):
    return confirmar(request, 15)

def confirmar(request, tipo):
    if not is_modulo_activo('presentacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    candidato = Candidato.objects.get(pk=request.session['id_candidato'])
    if request.method == 'POST': # If the form has been submitted...
        candidato.tipo = tipo
        candidato.n_socio = 'n/a'
        socios = list(mv.Socio.objects.filter(num_socio=candidato.n_socio.zfill(8)))
        socios += list(mv.Socio.objects.filter(num_socio_antiguo='S' + candidato.n_socio.zfill(7)))
        socios += list(mv.Socio.objects.filter(num_socio_antiguo=candidato.n_socio))
        if len(socios) != 1:
            socios = mv.Socio.objects.filter(correo_electronico=candidato.correo_e)
        if len(socios) != 1:
            candidato.save()
            envia_confirmacion(candidato)
            return HttpResponseRedirect('/ok2_%s/' % tipo)
        socio = socios[0]
        
        candidato.valida_sistema = True
        candidato.fecha_alta = socio.fecha_socio
        candidato.valida_sistema = True
        if socio.fecha_nacimiento:
            if socio.fecha_nacimiento > datetime.datetime(2013 - 18, 4, 21):
                candidato.comentarios += '\nMenor de edad'
                candidato.valida_sistema = False
        else:
            candidato.comentarios += '\nFecha de nacimiento no disponible'
            candidato.valida_sistema = False

        if not socio.corriente:
            candidato.comentarios += '\nNo corriente'
            candidato.valida_sistema = False
        if tipo == 15:
            fecha_alta_tope = datetime.datetime(2013 - 3, 4, 21)
        else:
            fecha_alta_tope = datetime.datetime(2013 - 3, 10, 20)
        if socio.fecha_socio > fecha_alta_tope:
            candidato.comentarios += '\nSocio demasiado reciente'
            candidato.valida_sistema = False
        if socio.circunscripcion != candidato.circunscripcion:
            candidato.comentarios += u'\nNo coincide circunscripción'
            candidato.valida_sistema = False
            
        candidato.save()
        envia_confirmacion(candidato)
        if candidato.valida_sistema:
            return HttpResponseRedirect('/ok_%s/' % tipo)
        return HttpResponseRedirect('/ok2_%s/' % tipo)
    else:
        form = NuevoCandidatoConfirmacionForm(instance=candidato)
        if tipo == 15:
            del form.fields['descripcion']
            del form.fields['circunscripcion']
        c = dict(form=form, candidato=candidato)
        for k in form.fields:
            w = form.fields[k].widget
            if isinstance(w, Select):
                w.attrs['disabled'] = True
            else:
                w.attrs['readonly'] = True
            
        return render(request, 'presentacion_previa.html', c)

def alegaciones_60(request):
    return alegaciones(request, 60)

def alegaciones_15(request):
    return alegaciones(request, 15)

def alegaciones(request, tipo):
    if not is_modulo_activo('alegaciones_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    candidatos = m.Candidato.objects.filter(tipo=tipo)
    candidatos_valida = candidatos.filter(valida=True).order_by('circunscripcion', 'fecha_alta')
    candidatos_novalida = candidatos.exclude(valida=True).order_by('apellidos', 'nombre')
 
    ccaa = [(k, list(v)) for (k, v) in groupby(candidatos_valida, lambda x:x.circunscripcion)]
    c = dict(ccaa=ccaa, candidatos_novalida=candidatos_novalida)
    return render(request, 'alegaciones.html', c)

@permission_required('recuento.change_candidato')
def comision_60(request):
    return comision(request, 60)

@permission_required('recuento.change_candidato')
def comision_15(request):
    return comision(request, 15)

def comision(request, tipo):
    if (not is_modulo_activo('comision_%s' % tipo) 
        and not request.user.is_superuser):
        return HttpResponseRedirect('/')
    candidatos = m.Candidato.objects.filter(tipo=tipo)
    candidatos_valida = candidatos.filter(valida=True).order_by('circunscripcion', 'fecha_alta')
    candidatos_novalida = candidatos.filter(valida=False).order_by('apellidos', 'nombre')
    candidatos_pendiente = candidatos.filter(valida__isnull=True).order_by('apellidos', 'nombre')
 
    ccaa = [(k, list(v)) for (k, v) in groupby(candidatos_valida, lambda x:x.circunscripcion)]
    c = dict(ccaa=ccaa, candidatos_novalida=candidatos_novalida, candidatos_pendiente=candidatos_pendiente)
    return render(request, 'admin_candidatos.html', c)

@ratelimit_post(minutes = 3, requests = 10)
@permission_required('recuento.change_candidato')
def editar_candidato_60(request, num):
    return editar_candidato(request, 60, num)

@ratelimit_post(minutes = 3, requests = 10)
@permission_required('recuento.change_candidato')
def editar_candidato_15(request, num):
    return editar_candidato(request, 15, num)

def editar_candidato(request, tipo, id_candidato):
    if (not is_modulo_activo('comision_%s' % tipo) 
        and not request.user.is_superuser):
        return HttpResponseRedirect('/')
    candidato = Candidato.objects.get(pk=id_candidato)
    assert candidato.tipo == tipo

    if request.method == 'POST':
        form = AdminCandidatoForm(request.POST, request.FILES, instance=candidato)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/comision_%s/' % tipo)
        info = dict(info='Se han detectado errores')
    else:
        if candidato.valida_sistema:
            info = dict(info='Ya validado')
        else:
            info = mv.getContact(candidato.correo_e, candidato.num_dni)
            if info:
                if info['Income_ultimos_12_meses_CONSEJO__c'] >= settings.MIN_INCOME:
                    candidato.corriente = True
                    candidato.save()
                if info['Birthdate']:
                    candidato.fecha_nacimiento = parse_date(info['Birthdate'])
                    if candidato.fecha_nacimiento <= settings.FECHA_MAXIMA_NACIMIENTO:
                        candidato.mayor_edad = True
                    candidato.save()
                if info['Fecha_de_antiguedad__c']:
                    candidato.fecha_alta = parse_date(info['Fecha_de_antiguedad__c'])
                    candidato.antiguedad_3a = candidato.fecha_alta <= settings.FECHA_MAXIMA_ANTIGUEDAD
                    candidato.save()
                if info['MailingPostalCode']:
                    prefijo = info['MailingPostalCode'][:2]
                    circunscripcion_por_cp = Provincia.objects.get(prefijo_cp=prefijo).circunscripcion
                    candidato.circunscripcion_correcta = candidato.circunscripcion == circunscripcion_por_cp
                    candidato.save()
                candidato.valida_sistema = candidato.corriente == True \
                        and candidato.circunscripcion_correcta == True\
                        and candidato.mayor_edad == True\
                        and candidato.antiguedad_3a == True
                candidato.save()
            else:
                info = dict(info='Sin resultados')
        form=form = AdminCandidatoForm(instance=candidato)
    data = dict(
                candidato=candidato,
                form=form,
                info=info,
                )
    
    return render(request, 'editar_candidato.html', data)

def ver_candidatos_15(request):
    return ver_candidatos(request, 15)

def ver_candidatos_60(request):
    return ver_candidatos(request, 60)

def ver_candidatos(request, tipo):
    if not is_modulo_activo('votacion_%s' % tipo) and \
       not is_modulo_activo('ver_candidaturas_%s' % tipo) and \
        not request.user.is_superuser:
        return HttpResponseRedirect('/')
    candidatos = m.Candidato.objects.filter(tipo=tipo)
    candidatos_valida = candidatos.filter(valida=True).order_by('circunscripcion', 'fecha_alta')
    
    ccaa = [(k, list(v)) for (k, v) in groupby(candidatos_valida, lambda x:x.circunscripcion)]
    c = dict(ccaa=ccaa)
    return render(request, 'ver_candidatos.html', c)

def resultado_15(request):
    ccaa = Circunscripcion.objects.filter(pk=18)
    return resultado(request, 15, ccaa)

def resultado_60(request):
    ccaa = Circunscripcion.objects.exclude(pk=18)
    return resultado(request, 60, ccaa)

def resultado(request, tipo, ccaa):
    modulo = is_modulo_activo('resultado_%s' % tipo)
    if not modulo and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    elif not modulo:
        modulo = Plazo.objects.filter(modulo = 'resultado_%s' % tipo)
    c = dict(ccaa=ccaa, modulo=modulo[0])
    return render(request, 'resultados.html', c)

def ok_15(request):
    return render(request, 'ok_15.html')

def ok_60(request):
    return render(request, 'ok_60.html')

def alegacion_ok(request):
    return render(request, 'alegacion_ok.html')

def alegar(request, num):
    if not is_modulo_activo('alegaciones_60') and not is_modulo_activo('alegaciones_15') and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    candidato = m.Candidato.objects.get(pk=num)
    if request.method == 'POST':
        form = AlegacionForm(request.POST)
        if form.is_valid():
            candidato.alegaciones += '\n' + form.cleaned_data['alegacion']
            candidato.save()
            return HttpResponseRedirect('/alegacion_ok/')
    else:
        form=form = AlegacionForm()
    data = dict(
                candidato=candidato,
                form=form,
                )
    return render(request, 'formulario_alegacion.html', data)

def casi_ok_15(request):
    return render(request, 'casi_ok_15.html')

def casi_ok_60(request):
    return render(request, 'casi_ok_60.html')

def envia_confirmacion(candidato):
    form = NuevoCandidatoConfirmacionForm(instance=candidato)
    ret = u'Se ha recibido la siguiente candidatura al Consejo de Greenpeace España:\n'
    for f in form:
        ret += '\n%s: %s' % (f.label, f.value())
    ret += u'\nSi lo consideras necesario, contacta con la Comisión Electoral en eleccion.es@greenpeace.org.\nGracias'
    destinatarios = [form['correo_e'].value()]
    if candidato.presenta and candidato.presenta.correo_electronico:
        destinatarios.append(candidato.presenta.correo_electronico)
    send_mail(subject=u"Candidatura al Consejo de Greenpeace España",
              message=ret,
              from_email='eleccion.es@greenpeace.org',
              recipient_list=destinatarios,
              )


