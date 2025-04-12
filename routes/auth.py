from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from models import user

auth = Blueprint("auth", __name__)

# Verifica si el usuario aun existe.
@auth.before_app_request
def check_user_role():
    if 'usuario' in session:
        user_id = session['usuario']['_id']
        current_user = user.select_by_id(user_id)
        
        # Si el usuario no existe en la base de datos, cerrar sesión
        if not current_user:
            session.pop('usuario', None)
            session.modified = True
        else:
            # Verificar y actualizar todos los datos del usuario en la sesión
            session_data = session['usuario']
            db_data = {
                "nombre": current_user["nombre"],
                "apellidoPat": current_user["apellidoPat"],
                "correo": current_user["correo"],
                "rol": current_user.get("rol", "usuario")
            }
            
            # Si hay cambios, actualizar la sesión
            if session_data != db_data:
                session['usuario'].update(db_data)
                session.modified = True

# Registrar usuario
@auth.route('/register', methods=['POST'])
def register():
    data = request.form
    nombre = data.get('nombre', '').strip()
    apellido1 = data.get('apellido1', '').strip()
    apellido2 = data.get('apellido2', '').strip()
    correo = data.get('correo', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm-password', '').strip()

    # Validaciones en el controlador
    if not nombre or not apellido1 or not correo or not password or not confirm_password:
        return jsonify({"success": False, "message": "Todos los campos son obligatorios."})
    
    if user.select_by_correo(correo):
        return jsonify({"success": False, "message": "Este correo ya está registrado. Usa otro."})

    if len(password) < 8:
        return jsonify({"success": False, "message": "Mínimo 8 caracteres para la contraseña."})

    if password != confirm_password:
        return jsonify({"success": False, "message": "Las contraseñas no coinciden."})

    password_hash = generate_password_hash(password)
    
    usuario_nuevo = {
        "nombre": nombre,
        "apellidoPat": apellido1,
        "correo": correo,
        "password": password_hash,
        "rol": "usuario"
    }
    if apellido2:
        usuario_nuevo["apellidoMat"] = apellido2

    # Llamamos a la función create del modelo para insertar el usuario
    user.create(usuario_nuevo)

    return jsonify({"success": True, "message": "Registro exitoso."})

# Iniciar sesión
@auth.route("/login", methods=['POST'])
def login():
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()

    usuario = user.select_by_correo_and_password(correo, password)
    if not usuario:
        return jsonify({"success": False, "message": "Correo o contraseña incorrectos."})

    session['usuario'] = {
        "_id": str(usuario['_id']),
        "nombre": usuario["nombre"],
        "apellidoPat": usuario["apellidoPat"],
        "correo": usuario["correo"],
        "rol": usuario.get("rol", "usuario")
    }

    return jsonify({"success": True, "message": "Inicio de sesión exitoso."})

# Cerrar sesión
@auth.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("main.home"))

@auth.route("/edit", methods=['POST'])
def edit():
    # Verificar que el usuario esté autenticado
    usuario_actual = session.get("usuario")
    if not usuario_actual:
        return jsonify({"success": False, "message": "No autorizado."}), 403

    # Verificar que se envíe la contraseña actual para confirmar la edición
    current_password = request.form.get("password", "").strip()
    if not current_password:
        return jsonify({"success": False, "message": "Contraseña requerida."}), 400

    # Validar que la contraseña ingresada sea correcta para el correo de la sesión actual
    correo_actual = usuario_actual.get("correo")
    valid_user = user.select_by_correo_and_password(correo_actual, current_password)
    if not valid_user:
        return jsonify({"success": False, "message": "Contraseña inválida."}), 400

    # Obtener los datos actuales del usuario desde la DB
    current_data = user.select_by_id(usuario_actual["_id"])

    try:
        update_fields = {}
        unset_fields = {}

        # Actualizar el nombre, si se proporciona y es diferente
        new_nombre = request.form.get("nombre", "").strip()
        if new_nombre and new_nombre != current_data.get("nombre", ""):
            update_fields["nombre"] = new_nombre

        # Actualizar el primer apellido, si se proporciona y es diferente
        new_apellido1 = request.form.get("apellido1", "").strip()
        if new_apellido1 and new_apellido1 != current_data.get("apellidoPat", ""):
            update_fields["apellidoPat"] = new_apellido1

        # Actualizar el correo, si se proporciona y es diferente
        new_correo = request.form.get("correo", "").strip()
        if new_correo and new_correo != current_data.get("correo", ""):
            update_fields["correo"] = new_correo

        # Actualizar el segundo apellido (apellidoMat): 
        # si se envía y es diferente se actualiza; si viene vacío se elimina
        new_apellido2 = request.form.get("apellido2", "").strip()
        if new_apellido2:
            if new_apellido2 != current_data.get("apellidoMat", ""):
                update_fields["apellidoMat"] = new_apellido2
        else:
            if current_data.get("apellidoMat"):
                unset_fields["apellidoMat"] = ""
        
        # Manejar el cambio de contraseña (si se ingresa una nueva)
        new_password = request.form.get("new-password", "").strip()
        confirm_password = request.form.get("confirm-password", "").strip()
        if new_password:
            if new_password != confirm_password:
                return jsonify({"success": False, "message": "Las contraseñas no coinciden."}), 400
            update_fields["password"] = generate_password_hash(new_password)

        # Preparar los datos para la actualización
        update_data = {}
        if update_fields:
            update_data["$set"] = update_fields
        if unset_fields:
            update_data["$unset"] = unset_fields

        if update_data:
            result = user.update_by_id(usuario_actual["_id"], update_data)
            if result.modified_count > 0:
                # La actualización de la sesión se hará en el before_request
                return jsonify({"success": True, "message": "Usuario actualizado correctamente."}), 200
            else:
                return jsonify({"success": True, "message": "No se realizaron cambios."}), 200
        else:
            return jsonify({"success": True, "message": "No se realizaron cambios."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Eliminar usuario
@auth.route("/delete_user", methods=["POST"])
def delete_user():
    usuario_actual = session.get("usuario")

    # Verificar si el usuario está autenticado y es administrador
    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403
    
    user_id = request.form.get("id")
    if not user_id:
        return jsonify({"success": False, "message": "No se proporcionó un ID válido."})

    user_data = user.select_by_id(user_id)
    if not user_data:
        return jsonify({"success": False, "message": "El usuario no existe."})

    # Verificar si el usuario que está haciendo la eliminación es el propio usuario
    if session['usuario']['_id'] == user_id:
        return jsonify({"success": False, "message": "No puedes eliminar tu propio usuario."})

    # Eliminar usuario
    result = user.delete_by_id(user_id)
    
    if result.deleted_count > 0:
        return jsonify({"success": True, "message": "Usuario eliminado correctamente."})
    else:
        return jsonify({"success": False, "message": "No se pudo eliminar el usuario."})

# Eliminar cuenta propia
@auth.route("/delete_own_account", methods=["POST"])
def delete_own_account():
    usuario_actual = session.get("usuario")

    if not usuario_actual:
        return jsonify({"success": False, "message": "No autorizado."}), 403

    password = request.form.get("password")

    if not password:
        return jsonify({"success": False, "message": "Se requiere la contraseña."})

    # Verificar la contraseña antes de eliminar la cuenta
    user_data = user.select_by_id(usuario_actual["_id"])
    if not user_data or not check_password_hash(user_data["password"], password):
        return jsonify({"success": False, "message": "Contraseña incorrecta."})

    # Eliminar usuario
    result = user.delete_by_id(usuario_actual["_id"])
    
    if result.deleted_count > 0:
        session.clear()
        return jsonify({"success": True, "message": "Cuenta eliminada correctamente."})
    else:
        return jsonify({"success": False, "message": "No se pudo eliminar la cuenta."})

# Quitar/Dar rol de admin
@auth.route("/update_user_role", methods=["POST"])
def update_user_role():
    usuario_actual = session.get("usuario")

    # Verificar si el usuario está autenticado y es administrador
    if not usuario_actual or usuario_actual.get("rol") != "admin":
        return jsonify({"success": False, "message": "No autorizado."}), 403
    
    user_id = request.form.get("id")
    new_role = request.form.get("role")

    if not user_id or not new_role:
        return jsonify({"success": False, "message": "Faltan parámetros."})

    user_data = user.select_by_id(user_id)
    if not user_data:
        return jsonify({"success": False, "message": "El usuario no existe."})

    # Verificar si el usuario está intentando quitar su propio rol de admin
    if session.get('usuario', {}).get('_id') == user_id and new_role == "remove_admin":
        return jsonify({"success": False, "message": "No puedes eliminar tu propio rol de administrador."})

    # Cambiar el rol del usuario
    if new_role == "remove_admin":
        if user_data["rol"] == "admin":
            result = user.update_by_id(user_id, {"$set": {"rol": "usuario"}})
            if result.modified_count > 0:
                return jsonify({"success": True, "message": "Rol de admin eliminado correctamente."})
            else:
                return jsonify({"success": False, "message": "No se pudo actualizar el rol."})
        else:
            return jsonify({"success": False, "message": "El usuario no es administrador."})

    elif new_role == "add_admin":
        if user_data["rol"] != "admin":
            result = user.update_by_id(user_id, {"$set": {"rol": "admin"}})
            if result.modified_count > 0:
                return jsonify({"success": True, "message": "Rol de admin asignado correctamente."})
            else:
                return jsonify({"success": False, "message": "No se pudo actualizar el rol."})
        else:
            return jsonify({"success": False, "message": "El usuario ya es administrador."})

    return jsonify({"success": False, "message": "Rol no reconocido."})
