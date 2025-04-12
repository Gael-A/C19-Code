from pymongo import MongoClient
import gridfs

# Clave secreta para sesiones
SECRET_KEY = "SECRET_Key" # No es la clave real!

# Conexión a MongoDB
MONGO_URI = "mongodb+srv://" # No es la URI real!
client = MongoClient(MONGO_URI)
db = client["DB"] # No es la DB real!
fs = gridfs.GridFS(db)

# Configuración de sesiones
SESSION_TYPE = "mongodb"
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
SESSION_MONGODB = client
SESSION_MONGODB_DB = "DB" # No es la BD real!
SESSION_MONGODB_COLLECT = "flask_session" 

# Configuración de email con Gmail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'sendcecati19@gmail.com'
MAIL_PASSWORD = 'xxxx xxxx xxxx' # No es la clave real!
MAIL_DEFAULT_SENDER = 'sendcecati19@gmail.com'