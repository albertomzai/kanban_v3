from flask import Flask, send_from_directory
from . import routes

def create_app():
    """
    Application factory para crear y configurar la instancia de la aplicación Flask.
    Configura la carpeta estática para servir el frontend y registra los Blueprints.
    """
    # Configurar la aplicación para servir archivos estáticos desde el directorio '../frontend'
    app = Flask(__name__, static_folder='../frontend', static_url_path='')

    # Registrar el Blueprint de la API
    app.register_blueprint(routes.api_bp)

    @app.route('/')
    def index():
        """
        Ruta raíz que sirve el archivo index.html de la aplicación frontend.
        """
        return send_from_directory(app.static_folder, 'index.html')

    return app