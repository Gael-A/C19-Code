import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app, Response
from werkzeug.utils import secure_filename
from models import announcement
from config.settings import fs, db  # GridFS ya está configurado aquí

announcements = Blueprint("announcements", __name__)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Agregar un anuncio
@announcements.route("/add_announcement", methods=["POST"])
def add_announcement():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403
    try:
        # Obtener datos del formulario
        titulo = request.form.get("titulo").strip()
        link = request.form.get("link", "").strip()
        file = request.files.get("archivo_imagen")
        if not titulo or not file:
            return jsonify({"success": False, "message": "Faltan campos requeridos."}), 400
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "Formato de archivo no permitido."}), 400

        # Generar un UIDD único
        uidd = str(uuid.uuid4())
        ext = file.filename.rsplit(".", 1)[1].lower()
        # Leer el contenido binario de la imagen
        file.seek(0)
        image_data = file.read()
        # Definir el content type (trata jpg como jpeg)
        content_type = f"image/{'jpeg' if ext=='jpg' else ext}"
        # Guardar la imagen en GridFS
        image_file_id = fs.put(image_data, filename=f"{uidd}.{ext}", content_type=content_type)

        # Guardar en MongoDB la información del anuncio
        anuncio_data = {
            "UIDD": uidd,
            "titulo": titulo,
            "extension": ext,  # opcional, si se necesita para referencia
            "image_file_id": image_file_id
        }
        if link:
            anuncio_data["link"] = link

        announcement.create(anuncio_data)
        
        return jsonify({"success": True, "message": "Anuncio agregado correctamente."}), 200
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado: {str(e)}"}), 500

# Actualizar un anuncio
@announcements.route('/update_announcement', methods=['POST'])
def update_announcement():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403
    try:
        # Obtener el UIDD del anuncio
        anuncio_uidd = request.form.get("uidd")
        if not anuncio_uidd:
            return jsonify({"success": False, "message": "UIDD requerido."}), 400

        # Buscar el anuncio en la base de datos
        anuncio = announcement.select_by_UIDD(anuncio_uidd)
        if not anuncio:
            return jsonify({"success": False, "message": "Anuncio no encontrado."}), 404

        set_fields = {}
        unset_fields = {}

        # Actualizar el título, si se proporciona y es diferente
        new_titulo = request.form.get("titulo", "").strip()
        if new_titulo and new_titulo != anuncio.get("titulo", ""):
            set_fields["titulo"] = new_titulo

        # Actualizar el link: si se envía uno nuevo se actualiza; si viene vacío se elimina
        new_link = request.form.get("link", "").strip()
        if new_link != anuncio.get("link", ""):
            if new_link:
                set_fields["link"] = new_link
            else:
                unset_fields["link"] = ""

        # Procesar un nuevo archivo de imagen, si se envía
        file = request.files.get("archivo_imagen")
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({"success": False, "message": "Formato de archivo no permitido."}), 400

            new_ext = file.filename.rsplit(".", 1)[1].lower()
            file.seek(0)
            image_data = file.read()
            content_type = f"image/{'jpeg' if new_ext=='jpg' else new_ext}"
            # Eliminar la imagen antigua en GridFS, si existe
            if "image_file_id" in anuncio:
                fs.delete(anuncio["image_file_id"])
            # Guardar la nueva imagen en GridFS
            new_image_file_id = fs.put(image_data, filename=f"{anuncio_uidd}.{new_ext}", content_type=content_type)
            set_fields["extension"] = new_ext
            set_fields["image_file_id"] = new_image_file_id

        update_data = {}
        if set_fields:
            update_data["$set"] = set_fields
        if unset_fields:
            update_data["$unset"] = unset_fields

        if update_data:
            announcement.update_by_UIDD(anuncio_uidd, update_data)
            return jsonify({"success": True, "message": "Anuncio actualizado correctamente."}), 200
        else:
            return jsonify({"success": True, "message": "No se realizaron cambios."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado: {str(e)}"}), 500

# Eliminar un anuncio
@announcements.route('/delete_announcement', methods=['POST'])
def delete_announcement():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403

    try:
        anuncio_uidd = request.form.get("uidd")
        if not anuncio_uidd:
            return jsonify({"success": False, "message": "UIDD requerido."}), 400

        # Buscar el anuncio en la base de datos
        anuncio = announcement.select_by_UIDD(anuncio_uidd)
        if not anuncio:
            return jsonify({"success": False, "message": "Anuncio no encontrado."}), 404

        # Eliminar la imagen almacenada en GridFS, si existe
        if "image_file_id" in anuncio:
            fs.delete(anuncio["image_file_id"])

        # Eliminar el anuncio de la base de datos
        announcement.delete_by_UIDD(anuncio_uidd)

        return jsonify({"success": True, "message": "Anuncio eliminado correctamente."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado: {str(e)}"}), 500

# Ruta para servir la imagen del anuncio desde GridFS
@announcements.route("/announcement/image/<uidd>")
def serve_announcement_image(uidd):
    # Buscar el anuncio en la base de datos
    anuncio = announcement.select_by_UIDD(uidd)
    if not anuncio:
        return jsonify({"success": False, "message": "Anuncio no encontrado."}), 404

    image_file_id = anuncio.get("image_file_id")
    if not image_file_id:
        return jsonify({"success": False, "message": "Imagen no encontrada."}), 404

    try:
        image_file = fs.get(image_file_id)
        return Response(image_file.read(), mimetype=image_file.content_type)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al recuperar la imagen: {str(e)}"}), 500
