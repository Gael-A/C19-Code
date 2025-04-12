from flask_mailman import EmailMessage
from flask import current_app

def enviar_correo(destinatarios, asunto, cuerpo, reply_to):
    msg = EmailMessage(
        subject=asunto,
        body=cuerpo,
        to=destinatarios,
        reply_to=[reply_to]
    )
    msg.send()