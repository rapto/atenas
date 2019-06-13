# -*- coding: utf-8 -*-
from itertools import groupby

from comun.ratelimitcache import ratelimit_post
from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mail
from django.db import connection, transaction
from django.db.models.aggregates import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from recuento import models as m
from recuento.models import Candidato, Consejero, Papeleta
from django.conf import settings
from verificacion import models as mv
import datetime
from django.contrib import messages
from recuento.forms import NuevoCandidatoForm, NuevoCandidatoConfirmacionForm,\
    AlegacionForm, NuevoCandidato25Form, AdminCandidatoForm
from django.forms.widgets import Select
from comun.views import is_modulo_activo
from comun.models import Circunscripcion, Plazo

@permission_required('recuento.can_register_ballot')
def selector_25(request):
    return selector(request, 25)

@permission_required('recuento.can_register_ballot')
def selector_50(request):
    return selector(request, 50)

def selector(request, tipo):
    circ_singular = Circunscripcion.objects.get(pk=18)
    if tipo == 25:
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

def votacion_25(request):
    return votacion(request, 25, Consejero)

def votacion_50(request):
    return votacion(request, 50, mv.Socio)

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
    if tipo == 25:
        return HttpResponseRedirect('/papeleta_%s/%s/' % (tipo, 18))
    if tipo == 50 and socio.circunscripcion.pk!=18:
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

def papeleta_usu_50(request, ca):
    return papeleta_usu(request, ca, 50, mv.Socio)

def papeleta_usu_25(request, ca):
    return papeleta_usu(request, ca, 25, Consejero)

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
    if tipo == 50:
        max_candidatos = circ.puestos
        assert socio.circunscripcion.pk == 18 or socio.circunscripcion == circ
    else:
        max_candidatos = settings.MAX_CANDIDATOS_25
    return render(request, plantilla, locals())

def papeleta_admin_25(request, ca):
    return papeleta_admin(request, ca, 25, settings.MAX_CANDIDATOS_25)

def papeleta_admin_50(request, ca):
    circ=m.Circunscripcion.objects.get(pk=ca)
    return papeleta_admin(request, ca, 50, circ.puestos)

def papeleta_admin(request, ca, tipo, puestos):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")
    circ = m.Circunscripcion.objects.get(pk=ca)
    ultimo = request.user.is_authenticated() and ultimaPapeleta(request.user,circ)
    return render(request, 'papeleta.html', locals())

@transaction.atomic    
@permission_required('recuento.can_register_ballot')
def anular_25(request,ca):
    return anular(request, ca, 25)
@transaction.atomic    
@permission_required('recuento.can_register_ballot')
def anular_50(request,ca):
    return anular(request, ca, 50)

def anular(request,ca, tipo):
    circ=m.Circunscripcion.objects.get(pk=ca)
    assert request.method=='POST'
    ultimo=ultimaPapeleta(request.user,circ)
    assert int(request.POST['ultimo'])==ultimo.id, repr(request.POST['ultimo'])+'!='+repr(ultimo.id)
    ultimo.voto_set.all().delete()
    ultimo.delete()
    return HttpResponseRedirect('/atenas_%s/papeleta/%s/' % (tipo, ca))

@transaction.atomic
def registrar_usu_50(request,ca):
    return registrar_usu(request, ca, 50, mv.Socio)

@transaction.atomic
def registrar_usu_25(request,ca):
    return registrar_usu(request, ca, 25, Consejero)

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
    if tipo == 50:
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
    if tipo == 50:
        max_candidatos = circ.puestos
    else:
        max_candidatos = settings.MAX_CANDIDATOS_25
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
def registrar_admin_50(request, ca):
    return registrar_admin(request, ca, 50)

@transaction.atomic
def registrar_admin_25(request, ca):
    return registrar_admin(request, ca, 25)

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
    if tipo == 50:
        assert len(aspas) <= circ.puestos, u'No se puede votar a más candidatos que puestos'
    else:
        assert len(aspas) <= settings.MAX_CANDIDATOS_25
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
def envia_clave_50(request):
    return envia_clave(request, 50, mv.Socio)

@transaction.atomic
@ratelimit_post(minutes = 3, requests = 10)
def envia_clave_25(request):
    return envia_clave(request, 25, Consejero)

def envia_clave(request, tipo, clase_votantes):
    
    MSG_DIRECCION_KO = u'Disculpa, pero esa dirección no está registrada como votante. Por favor, vota por correo postal.'
    if not is_modulo_activo('votacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    if request.method!="POST":
        return HttpResponseRedirect('/')
    email = request.POST.get('email')
    if not email:
        return HttpResponseRedirect('/votacion_%s/' % tipo)
    socios = clase_votantes.objects.filter(correo_electronico=email)
    level = messages.WARNING
    if not socios:
        msg = MSG_DIRECCION_KO
    elif len(socios) > 1:
        msg = u'Disculpa, pero esa dirección corresponde a más de una persona. Por favor, vota por correo postal.'
    else:
        socio = socios[0]
        if socio.clave or socio.puedeVotar(True)[0]:
            email_text = u'Estimado/a %s %s\r\nÉsta es tu clave: %s\r\nPuedes votar en https://elecciones.greenpeace.es' % (socio.nombre, socio.apellidos, socio.get_clave())
            send_mail(u"[Greenpeace España/Elecciones] Clave para votar ", email_text, 'no-reply@greenpeace.es', [socio.correo_electronico], 
                  fail_silently= False)
            msg = u'Por favor, verifica tu buzón de correo. En breve te llegará un mensaje con la clave para votar.'
            level = messages.SUCCESS
        else:
            msg = MSG_DIRECCION_KO
    messages.add_message(request, level, msg)
    return HttpResponseRedirect('/votacion_%s/' % tipo)

@ratelimit_post(minutes = 3, requests = 10)
def presentacion_50(request):
    return presentacion(request, 50)

@ratelimit_post(minutes = 3, requests = 10)
def presentacion_25(request):
    return presentacion(request, 25)

def presentacion(request, tipo):
    if not is_modulo_activo('presentacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    plantilla = 'presentacion.html'
    form_class = NuevoCandidatoForm if tipo==50 else NuevoCandidato25Form
    if request.method == 'POST': # If the form has been submitted...
        form = form_class(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid():
            candidato = form.save(commit=False)
            candidato.descripcion = candidato.descripcion or '-'
            candidato.tipo = 0
            if tipo == 25:
                candidato.circunscripcion_id = 18
            candidato.valida = None
            candidato.save()
            request.session['id_candidato'] = candidato.id
            return HttpResponseRedirect('/confirmar_%s/' % tipo)
    else:
        form = form_class() # An unbound form

    return render(request, plantilla, dict(form=form))

@ratelimit_post(minutes = 3, requests = 10)
def confirmar_50(request):
    return confirmar(request, 50)

@ratelimit_post(minutes = 3, requests = 10)
def confirmar_25(request):
    return confirmar(request, 25)

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
        if tipo == 25:
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
        if tipo == 25:
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

def alegaciones_50(request):
    return alegaciones(request, 50)

def alegaciones_25(request):
    return alegaciones(request, 25)

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
def comision_50(request):
    return comision(request, 50)

@permission_required('recuento.change_candidato')
def comision_25(request):
    return comision(request, 25)

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
def editar_candidato_50(request, num):
    return editar_candidato(request, 50, num)

@ratelimit_post(minutes = 3, requests = 10)
@permission_required('recuento.change_candidato')
def editar_candidato_25(request, num):
    return editar_candidato(request, 25, num)

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
    else:
        form=form = AdminCandidatoForm(instance=candidato)
    data = dict(
                candidato=candidato,
                form=form,
                )
    
    return render(request, 'editar_candidato.html', data)

def ver_candidatos_25(request):
    return ver_candidatos(request, 25)

def ver_candidatos_50(request):
    return ver_candidatos(request, 50)

def ver_candidatos(request, tipo):
    if not is_modulo_activo('votacion_%s' % tipo) and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    candidatos = m.Candidato.objects.filter(tipo=tipo)
    candidatos_valida = candidatos.filter(valida=True).order_by('circunscripcion', 'fecha_alta')
    
    ccaa = [(k, list(v)) for (k, v) in groupby(candidatos_valida, lambda x:x.circunscripcion)]
    c = dict(ccaa=ccaa)
    return render(request, 'ver_candidatos.html', c)

def resultado_25(request):
    ccaa = Circunscripcion.objects.filter(pk=18)
    return resultado(request, 25, ccaa)

def resultado_50(request):
    ccaa = Circunscripcion.objects.exclude(pk=18)
    return resultado(request, 50, ccaa)

def resultado(request, tipo, ccaa):
    modulo = is_modulo_activo('resultado_%s' % tipo)
    if not modulo and not request.user.is_superuser:
        return HttpResponseRedirect('/')
    elif not modulo:
        modulo = Plazo.objects.filter(modulo = 'resultado_%s' % tipo)
    c = dict(ccaa=ccaa, modulo=modulo[0])
    return render(request, 'resultados.html', c)

def ok_25(request):
    return render(request, 'ok_25.html')

def ok_50(request):
    return render(request, 'ok_50.html')

def alegacion_ok(request):
    return render(request, 'alegacion_ok.html')

def alegar(request, num):
    if not is_modulo_activo('alegaciones_50') and not is_modulo_activo('alegaciones_25') and not request.user.is_superuser:
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

def casi_ok_25(request):
    return render(request, 'casi_ok_25.html')

def casi_ok_50(request):
    return render(request, 'casi_ok_50.html')

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


