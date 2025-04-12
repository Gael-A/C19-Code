import os
import uuid
import tempfile
from flask import Blueprint, request, jsonify, session, abort, Response
from werkzeug.utils import secure_filename
from utils.docx_to_html import convert_docx_to_html
from models import course
from config.settings import fs, db

# Directorios locales solo para archivos temporales (DOCX)
DOCX_TEMP_DIR = "static/temp/docx/"

# Crear Blueprint
courses = Blueprint("courses", __name__)

# Agregar un curso
@courses.route("/add_course", methods=["POST"])
def add_course():
    usuario_actual = session.get("usuario")

    # Verificar si el usuario es administrador
    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403

    try:
        # Recolectar datos del formulario
        nombre = request.form.get("nombre", "").strip()
        examen_link = request.form.get("examen_link", "").strip()
        archivo_pdf = request.files.get("archivo_estandar")
        archivo_docx = request.files.get("archivo_info")

        if not nombre or not archivo_pdf or not archivo_docx:
            return jsonify({"success": False, "message": "Faltan datos requeridos"}), 400

        # Generar un UUID único para el curso
        course_uid = str(uuid.uuid4())

        # Guardar el PDF en MongoDB usando GridFS
        archivo_pdf.seek(0)
        pdf_content = archivo_pdf.read()
        pdf_file_id = fs.put(pdf_content, filename=f"{course_uid}.pdf", content_type="application/pdf")

        # Guardar el DOCX en un directorio temporal
        temp_dir = tempfile.gettempdir() if os.getenv("RENDER") else DOCX_TEMP_DIR
        os.makedirs(temp_dir, exist_ok=True)
        docx_filename = os.path.join(temp_dir, f"{course_uid}.docx")
        archivo_docx.save(docx_filename)

        # Convertir DOCX a HTML
        html_content = convert_docx_to_html(docx_filename)
        
        # Guardar el HTML en MongoDB usando GridFS
        html_file_id = fs.put(html_content.encode("utf-8"), filename=f"{course_uid}.html", content_type="text/html")

        # Eliminar el archivo DOCX temporal
        os.remove(docx_filename)

        # Guardar la información del curso en la base de datos
        curso_data = {
            "nombre": nombre,
            "UIDD": course_uid,
            "html_file_id": html_file_id,  # ID del HTML en MongoDB
            "pdf_file_id": pdf_file_id     # ID del PDF en MongoDB
        }
        if examen_link:
            curso_data["examen_link"] = examen_link

        course.create(curso_data)

        return jsonify({"success": True, "message": "Curso agregado correctamente"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Editar un curso
@courses.route("/edit_course", methods=["POST"])
def edit_course():
    usuario_actual = session.get("usuario")

    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403

    try:
        course_uid = request.form.get("uidd")
        if not course_uid:
            return jsonify({"success": False, "message": "UIDD requerido"}), 400

        # Buscar curso en la base de datos
        curso = course.select_by_UIDD(course_uid)
        if not curso:
            return jsonify({"success": False, "message": "Curso no encontrado"}), 404

        update_fields = {}
        unset_fields = {}

        # Actualizar nombre si se proporciona
        nombre = request.form.get("nombre", "").strip()
        if nombre:
            update_fields["nombre"] = nombre

        # Actualizar examen si se proporciona
        examen_link = request.form.get("examen_link", "").strip()
        if examen_link:
            update_fields["examen_link"] = examen_link
        elif "examen_link" in curso:
            unset_fields["examen_link"] = ""

        # Actualizar PDF si se proporciona
        archivo_pdf = request.files.get("archivo_estandar")
        if archivo_pdf:
            # Eliminar el PDF anterior de MongoDB si existe
            if "pdf_file_id" in curso:
                fs.delete(curso["pdf_file_id"])
            archivo_pdf.seek(0)
            pdf_content = archivo_pdf.read()
            pdf_file_id = fs.put(pdf_content, filename=f"{course_uid}.pdf", content_type="application/pdf")
            update_fields["pdf_file_id"] = pdf_file_id

        # Actualizar HTML si se proporciona nuevo DOCX
        archivo_docx = request.files.get("archivo_info")
        if archivo_docx:
            temp_dir = tempfile.gettempdir() if os.getenv("RENDER") else DOCX_TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            docx_filename = os.path.join(temp_dir, f"{course_uid}.docx")
            archivo_docx.save(docx_filename)

            # Convertir DOCX a HTML
            html_content = convert_docx_to_html(docx_filename)
            
            # Eliminar el anterior HTML de MongoDB si existe
            if "html_file_id" in curso:
                fs.delete(curso["html_file_id"])
            # Guardar nuevo HTML en MongoDB
            html_file_id = fs.put(html_content.encode("utf-8"), filename=f"{course_uid}.html", content_type="text/html")
            update_fields["html_file_id"] = html_file_id

            # Eliminar el DOCX temporal
            os.remove(docx_filename)

        # Preparar datos para actualización en MongoDB
        update_data = {"$set": update_fields} if update_fields else {}
        if unset_fields:
            update_data["$unset"] = unset_fields

        if update_data:
            course.update_by_UIDD(course_uid, update_data)
            return jsonify({"success": True, "message": "Curso actualizado correctamente"}), 200
        else:
            return jsonify({"success": True, "message": "No se realizaron cambios."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Eliminar un curso
@courses.route("/delete_course", methods=["POST"])
def delete_course():
    usuario_actual = session.get("usuario")

    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403

    try:
        course_uid = request.form.get("uidd")
        if not course_uid:
            return jsonify({"success": False, "message": "UIDD requerido."}), 400

        curso = course.select_by_UIDD(course_uid)
        if not curso:
            return jsonify({"success": False, "message": "Curso no encontrado."}), 404

        # Eliminar HTML de MongoDB
        if "html_file_id" in curso:
            fs.delete(curso["html_file_id"])
        # Eliminar PDF de MongoDB
        if "pdf_file_id" in curso:
            fs.delete(curso["pdf_file_id"])

        # Eliminar curso de la base de datos
        course.delete_by_UIDD(course_uid)

        return jsonify({"success": True, "message": "Curso eliminado correctamente."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error inesperado: {str(e)}"}), 500

# Recupera el PDF desde mongoDB.
@courses.route("/pdf/<uid>")
def serve_pdf(uid):
    # Buscar el curso por UIDD
    curso = course.select_by_UIDD(uid)
    if not curso:
        abort(404, description="Curso no encontrado")
    
    # Obtener el id del PDF guardado en GridFS
    pdf_file_id = curso.get("pdf_file_id")
    if not pdf_file_id:
        abort(404, description="PDF no encontrado")
    
    try:
        # Recuperar el archivo PDF desde GridFS
        pdf_file = fs.get(pdf_file_id)
        pdf_data = pdf_file.read()
        return Response(pdf_data, mimetype="application/pdf")
    except Exception as e:
        abort(500, description=str(e))