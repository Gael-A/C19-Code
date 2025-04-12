from config.settings import db

anuncios = db["anuncios"]


# Inserta un nuevo anuncio en la base de datos.
def create(anuncio_data):
    return anuncios.insert_one(anuncio_data)

# Obtiene todos los anuncios de la base de datos.
def select_all():
    return anuncios.find()

# Obtiene un anuncio específico de la base de datos por su UIDD.
def select_by_UIDD(anuncio_id):
    return anuncios.find_one({"UIDD": anuncio_id})

# Actualiza un anuncio por su UIDD en la base de datos.
def update_by_UIDD(anuncio_id, update_data):
    return anuncios.update_one({"UIDD": anuncio_id}, update_data)

# Elimina un anuncio por su UIDD en la base de datos.
def delete_by_UIDD(anuncio_id):
    return anuncios.delete_one({"UIDD": anuncio_id})