from flask import Flask, send_from_directory
from .routes import api_bp


def create_app():
    """
    Application factory para la aplicación Flask.
    Configura la app y registra los blueprints.
    """
    # Configuramos la carpeta estática para servir el frontend
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # Registramos el Blueprint de la API
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        """
        Ruta raíz que sirve el fichero index.html del frontend.
        """
        return send_from_directory(app.static_folder, 'index.html')

    return app