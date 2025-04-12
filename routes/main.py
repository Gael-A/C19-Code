import os
from flask import Blueprint, render_template, session, redirect, url_for, request, current_app

from models import course, user, announcement

from config.settings import fs

main = Blueprint("main", __name__)

# Página principal.
@main.route("/")
def index():
    return redirect(url_for('main.home'))

# Página de inicio.
@main.route("/home")
def home():
    usuario_actual = session.get("usuario")
    images = announcement.select_all()
    cursos = course.select_all()
    return render_template('home.html', usuario=usuario_actual, images=images, cursos=cursos)

# Página de registro de usuario.
@main.route("/user_register")
def user_register():
    return render_template('user_register.html')

# Página de inicio de sesión.
@main.route("/user_login")
def user_login():
    return render_template('user_login.html')

# Página de administrador de usuarios.
@main.route("/user_manager")
def user_manager():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    
    usuarios = user.select_all()
    return render_template('user_manager.html', usuarios=usuarios)

# Página de editar usuario.
@main.route("/user_edit")
def user_edit():
    usuario_actual = session.get("usuario")
    if not usuario_actual:
        return redirect(url_for('main.home'))
    usuario = user.select_by_id(usuario_actual.get('_id'))
    return render_template("user_edit.html", usuario=usuario)

# Página de registro de curso.
@main.route("/course_register")
def course_register():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    return render_template('course_register.html', usuario=usuario_actual)

# Página de administrador de cursos.
@main.route("/course_manager")
def course_manager():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    cursos = course.select_all()

    return render_template('course_manager.html', usuario=usuario_actual, cursos=cursos)

# Página de editar curso.
@main.route("/course_edit")
def course_edit():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    
    # Obtener el ID del curso a editar.
    curso_id = request.args.get('uidd')

    curso = course.select_by_UIDD(curso_id)

    if not curso:
        return render_template('course_edit.html', usuario=usuario_actual, mensaje="No se encontró en DB")

    return render_template('course_edit.html', usuario=usuario_actual, curso=curso)

# Página de vista de curso.
@main.route("/course")
def course_template():
    usuario_actual = session.get("usuario")
    cursos = course.select_all()

    uidd = request.args.get("uidd")
    
    # Verificar si el uidd existe en MongoDB
    curso = course.select_by_UIDD(uidd)
    
    if not curso:
        # Si no se encuentra el curso en MongoDB, redirigir o mostrar error
        return render_template('course_template.html', usuario=usuario_actual, cursos=cursos, mensaje="No se encontró en DB")
    
    # Obtener el ID del archivo HTML de MongoDB
    html_file_id = curso.get('html_file_id')

    if not html_file_id:
        # Si no existe el archivo HTML en MongoDB, mostrar error
        return render_template('course_template.html', usuario=usuario_actual, cursos=cursos, mensaje="No se encontró contenido HTML")
    
    # Obtener el contenido HTML desde MongoDB (usando GridFS)
    html_content = fs.get(html_file_id).read().decode('utf-8')
    
    # Si se encuentra todo, renderizamos el curso y pasamos el HTML a la plantilla
    return render_template('course_template.html', usuario=usuario_actual, curso=curso, cursos=cursos, course_html_content=html_content)

# Página de registro de anuncios.
@main.route("/announcement_register")
def announcement_register():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    return render_template('announcement_register.html', usuario=usuario_actual)

# Página de administrador de anuncios.
@main.route("/announcement_manager")
def announcement_manager():
    usuario_actual = session.get("usuario")
    images = announcement.select_all()
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    return render_template('announcement_manager.html', images=images ,usuario=usuario_actual)

# Página de editar anuncio.
@main.route("/announcement_edit")
def announcement_edit():
    usuario_actual = session.get("usuario")
    if not usuario_actual or usuario_actual.get('rol') != 'admin':
        return redirect(url_for('main.home'))
    
    # Obtener el ID del anuncio a editar
    uidd = request.args.get("uidd")

    anuncio = announcement.select_by_UIDD(uidd)
    
    if not anuncio:
        return render_template('announcement_edit.html', usuario=usuario_actual, mensaje="No se encontró en DB")
    
    return render_template('announcement_edit.html', usuario=usuario_actual, anuncio=anuncio)

# En caso de una ruta invalida
@main.app_errorhandler(404)
def page_not_found(error):
    usuario_actual = session.get("usuario")
    error_description = f"La página '{request.path}' no existe en el sitio."
    return render_template("404.html", usuario=usuario_actual, error_description=error_description), 404
