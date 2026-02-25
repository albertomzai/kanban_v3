from backend import create_app

# Crear la instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Ejecutar la aplicación en modo debug para desarrollo
    app.run(debug=True, port=5000)