var validations = [
   [ 'presenta', 1, 1000 ],
   [ 'nombre', 1, 200 ],
   [ 'apellidos', 1, 200 ],
   [ 'n_socio', 1, 20 ],
   [ 'cv', 0, 1000 ],
   [ 'descripcion', 1, 150 ],
   [ 'vinculacion', 0, 1000 ],
   [ 'campanha', 0, 1000 ],
   [ 'motivacion', 0, 1000 ],
   [ 'dni', 1, 1000 ],
   [ 'correo_e', 1, 254 ],
   [ 'circunscripcion', 1, 1000 ],
   [ 'localidad', 1, 200 ]
];


function verificarDatos() {
	var valida = true,
	emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
	for (var i = 0; i < validations.length; i++) {
		var validation = validations[i],
			elem = '#id_' + validation[0],
			len_min = validation[1],
			len_max = validation[2];
		if ($(elem).length == 0)
			continue;
		var len_elem = $(elem).val().length;
		if ((len_elem > len_max) || (len_elem < len_min)) {
			$(elem).effect('shake');
			$(elem).prop('title',"La longitud debe estar entre " + len_min + ' y ' + len_max);
			valida = false;
		}
	}
	elem = '#id_correo_e';
	if (!emailReg.test($(elem).val())){
		$(elem).prop('title', 'No parece una dirección de correo válida');
		$(elem).effect('shake');
		valida = false;
	}
	if (!$('#id_participacion_activa').is(":checked")){
		$('#id_participacion_activa').effect('shake');
		valida = false;
		}
	if (!$('#id_veracidad').is(":checked")){
		$('#id_veracidad').effect('shake');
		valida = false;
		}

	if (!valida)
		$.notifyBar({
			cssClass: "error",
			html:'Por favor, verifica la corrección de todos los datos. Los datos marcados* son obligatorios.'
				});
	return valida;
}

function inicializaContadores() {
	for (var i=0; i<validations.length; i++){
		var v = validations[i],
			elem_id='#id_' + v[0],
			ct_id='ct_' + v[0],
			counter = $('<div>')
	        .attr({ id : ct_id})
	        .addClass("counter");
		var elem = $(elem_id);
		elem = elem.filter('textarea');
		elem.after(counter);
		elem.simplyCountable({
			counter: '#' + ct_id,
	        countType: 'characters',
	        maxCount: v[2],
	        strictMax: true,
	        thousandSeparator:  '.',
	        countDirection: 'down'
			});
		}
	};

function onConsejeroActualClick(){
    var visible = $('#id_en_el_consejo').is(":checked");
    var casillas_en_el_consejo = $('#id_asistencia,#id_grupos,#id_frecuencia_acceso,#id_aportacion').closest('tr');
    if (visible)
        casillas_en_el_consejo.show();   
    else
        casillas_en_el_consejo.hide();
}

$(function()
    {
        $('#id_en_el_consejo').click(onConsejeroActualClick);
        onConsejeroActualClick();
    }
    )
