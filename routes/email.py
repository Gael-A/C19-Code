from flask import Blueprint, request, jsonify, session
from utils.mailer import enviar_correo

email = Blueprint('email', __name__)

@email.route('/enviar_correo', methods=['POST'])
def enviar_correo_route():
    # Intentamos obtener los datos en formato JSON
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No se recibieron datos.'}), 400

    asunto = data.get('asunto')
    mensaje = data.get('mensaje')

    if not asunto or not mensaje:
        return jsonify({'success': False, 'message': 'Asunto y mensaje son obligatorios.'}), 400

    # Obtenemos el usuario actual de la sesión
    usuario_actual = session.get("usuario")
    if not usuario_actual or not usuario_actual['correo']:
        # Si el usuario no está autenticado o no tiene correo, se retorna un error
        return jsonify({'success': False, 'message': 'Usuario no autenticado o sin correo registrado.'}), 403

    # Configuramos el destinatario (podrías hacerlo dinámico si es necesario)
    destinatario = 'cecati19.asa5@dgcft.sems.gob.mx'

    try:
        # Enviamos el correo usando la función definida en utils/mailer.py
        enviar_correo([destinatario], f"{usuario_actual['correo']}: {asunto}", 
              f"{mensaje}\n\nInformación de Contacto:\n{usuario_actual['nombre']} {usuario_actual['apellidoPat']}\n{usuario_actual['correo']}", 
              reply_to=usuario_actual['correo'])
        return jsonify({'success': True, 'message': 'Correo enviado correctamente.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al enviar el correo: {str(e)}'}), 500