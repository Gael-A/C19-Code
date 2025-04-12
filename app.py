from flask import Flask
from flask_session import Session
from flask_mailman import Mail
from config.settings import SECRET_KEY

from routes.auth import auth
from routes.main import main
from routes.email import email
from routes.courses import courses
from routes.announcements import announcements

app = Flask(__name__)

# Cargar toda la configuración desde config/settings.py
app.config.from_object('config.settings')

# Configuración de la clave secreta y sesión (ya se carga también de settings)
app.secret_key = SECRET_KEY

# Inicializar extensiones
Session(app)
mail = Mail(app)

# Registrar blueprints (rutas)
app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(email)
app.register_blueprint(courses)
app.register_blueprint(announcements)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
