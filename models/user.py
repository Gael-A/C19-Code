from config.settings import db
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

usuarios = db["usuarios"]

# Inserta un nuevo usuario en la base de datos.
def create(user_data):
    return usuarios.insert_one(user_data)

# Busca un usuario en la base de datos por su correo.
def select_by_correo(correo):
    return usuarios.find_one({"correo": correo})

# Verifica si el correo y la contraseña coinciden con un usuario registrado.
def select_by_correo_and_password(correo, password):
    usuario = select_by_correo(correo)
    if usuario and check_password_hash(usuario["password"], password):
        return usuario
    return None

# Busca un usuario en la base de datos por su ID.
def select_by_id(id):
    return usuarios.find_one({"_id": ObjectId(id)})

# Busca a todos los usuarios en la base de datos.
def select_all():
    return usuarios.find()

# Actualiza un usuario por su _id.
def update_by_id(id, user_data):
    return usuarios.update_one({"_id": ObjectId(id)}, user_data)

# Elimina un usuario por su _id.
def delete_by_id(id):
    return usuarios.delete_one({"_id": ObjectId(id)})
