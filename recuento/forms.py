#coding=UTF-8
from django.forms.models import ModelForm
from recuento.models import Candidato
from django import forms

class AdminCandidatoForm(ModelForm):
    class Meta:
        model = Candidato
        fields = [
            'valida', 
            'valida_sistema',
            'antiguedad_3a', 'corriente',
             'mayor_edad', 
            'circunscripcion_correcta',
            'nombre', 'apellidos', 'localidad', 'circunscripcion',
            'fecha_alta',
            'cv', 'vinculacion', 'motivacion', 'campanha', 'dni',
            'foto', 'correo_e'
            #'en_el_consejo', 'asistencia', 'grupos',
            #'frecuencia_acceso', 'aportacion'
                  ]


class NuevoCandidatoForm(ModelForm):
    class Meta:
        model = Candidato
        fields = ['nombre', 'apellidos', 'localidad', 'circunscripcion',
                  'cv', 'vinculacion', 'motivacion', 'campanha', 'dni',
                  'foto', 'correo_e', 'participacion_activa', 'veracidad',
                  # 'en_el_consejo', 'asistencia', 'grupos',
                  #'frecuencia_acceso', 'aportacion'
                  ]
        #widgets = {
        #            'asistencia': forms.CheckboxSelectMultiple,
        #            'grupos': forms.CheckboxSelectMultiple,
        #          }

    def clean_participacion_activa(self):
        data = self.cleaned_data['participacion_activa']
        if not data:
            raise forms.ValidationError(u"Para enviar la candidatura, debes aceptar el compromiso de participación")
        return data
        
    def clean_foto(self):
        data = self.cleaned_data['foto']
        max_size = 256 * 1024
        if data and len(data) > max_size:
            raise forms.ValidationError(u'El tamaño está restringido a %sKB' % (max_size / 1024))
        return data
        
    def clean_veracidad(self):
        data = self.cleaned_data['veracidad']
        if not data:
            raise forms.ValidationError(u"Para enviar la candidatura, debes dar fe de la veracidad de los datos")
        return data

    def clean_descripcion(self):
        data = self.cleaned_data['descripcion']
        return data.replace('\r\n', '\r')
        
    def clean_cv(self):
        data = self.cleaned_data['cv']
        return data.replace('\r\n', '\r')
        
    def clean_vinculacion(self):
        data = self.cleaned_data['vinculacion']
        return data.replace('\r\n', '\r')
                

class NuevoCandidato25Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NuevoCandidato25Form, self).__init__(*args, **kwargs)
    
        del self.fields['descripcion']
        self.fields['dni_presenta'].required = True

    class Meta:
        model = Candidato
        fields = ['presenta', 'dni_presenta', 'nombre', 'apellidos', 'localidad',
                  'descripcion', 'cv', 'vinculacion', 'dni', 'foto', 'correo_e', 'participacion_activa', 'veracidad']

    def clean_presenta(self):
        data = self.cleaned_data['presenta']
        if not data:
            raise forms.ValidationError(u"Se debe indicar qué consejero/a presenta al nuevo candidato/a")
        if data.candidato_set.filter(tipo=25).count() >= 2:
            raise forms.ValidationError(u"Este consejero/a ya ha presentado a dos candidatos/as")
        return data
        
    def clean_participacion_activa(self):
        data = self.cleaned_data['participacion_activa']
        if not data:
            raise forms.ValidationError(u"Para enviar la candidatura, debes aceptar el compromiso de participación")
        return data
        
    def clean_foto(self):
        data = self.cleaned_data['foto']
        max_size = 200 * 1024
        if data and len(data) > max_size:
            raise forms.ValidationError(u'El tamaño está restringido a %sKB' % (max_size / 1024))
        return data
        
    def clean_veracidad(self):
        data = self.cleaned_data['veracidad']
        if not data:
            raise forms.ValidationError(u"Para enviar la candidatura, debes dar fe de la veracidad de los datos")
        return data

    def clean_descripcion(self):
        data = self.cleaned_data['descripcion']
        return data.replace('\r\n', '\r')
        
    def clean_cv(self):
        data = self.cleaned_data['cv']
        return data.replace('\r\n', '\r')
        
    def clean_vinculacion(self):
        data = self.cleaned_data['vinculacion']
        return data.replace('\r\n', '\r')
                

class NuevoCandidatoConfirmacionForm(ModelForm):
    class Meta:
        model = Candidato
        fields = ['nombre', 'apellidos', 'localidad', 'circunscripcion',
                  'cv', 'vinculacion', 'motivacion', 'campanha', 'correo_e']
    

class AlegacionForm(forms.Form):
    alegacion = forms.CharField(max_length=200, widget=forms.Textarea)
