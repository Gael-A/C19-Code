from config.settings import db

cursos = db["cursos"]

# Inserta un nuevo curso en la base de datos.
def create(curso_data):
    return cursos.insert_one(curso_data)

# Actualiza un curso por su UIDD.
def update_by_UIDD(uidd, update_data):
    return cursos.update_one({"UIDD": uidd}, update_data)

# Busca un curso por su UIDD en la base de datos.
def select_by_UIDD(uidd):
    return cursos.find_one({"UIDD": uidd})

# Busca todos los cursos en la base de datos.
def select_all():
    return cursos.find()

# Elimina un curso por su UIDD en la base de datos.
def delete_by_UIDD(uidd):
    return cursos.delete_one({"UIDD": uidd})