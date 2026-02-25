# Documentación Técnica: API de Gestión de Tareas

## Visión General del Proyecto

Este proyecto constituye una aplicación web backend diseñada para la gestión eficiente de una lista de tareas (To-Do List). Implementada utilizando el framework micro `Flask` en Python, la aplicación sigue un patrón de diseño limpio y modular, separando la configuración de la aplicación de la lógica de enrutamiento a través del uso de Blueprints.

La arquitectura está pensada para ser ligera y autocontenida, utilizando un sistema de persistencia basado en archivos JSON (`tasks.json`) en lugar de una base de datos tradicional. Esto permite que la aplicación sea fácilmente desplegable y portátil para prototipos rápidos o uso personal. La aplicación actúa como una API RESTful que sirve tanto los endpoints de datos como los archivos estáticos del frontend, facilitando una experiencia de usuario unificada bajo un mismo servidor. El enfoque principal es proporcionar operaciones CRUD (Crear, Leer, Actualizar, Borrar) simples y robustas sobre las tareas.

## Arquitectura del Sistema

El sistema sigue una arquitectura monolítica simplificada típica de aplicaciones Flask pequeñas a medianas. La comunicación se establece entre el cliente (navegador) y el servidor Flask, que gestiona tanto la entrega de contenido estático como la lógica de negocio de la API.

### Componentes Principales

| Componente | Descripción | Tecnología |
| :--- | :--- | :--- |
| **Application Factory** | Función `create_app` encargada de inicializar la instancia de Flask y configurar el contexto de la aplicación. | Flask (`__init__.py`) |
| **API Blueprint** | Módulo que agrupa todas las rutas relacionadas con la gestión de tareas bajo el prefijo `/api`. | Flask Blueprint (`routes.py`) |
| **Capa de Persistencia** | Sistema de almacenamiento de datos utilizando un archivo plano JSON para leer y escribir el estado de las tareas. | Python `json` module |
| **Servidor de Archivos Estáticos** | Configuración para servir la interfaz de usuario (HTML/CSS/JS) ubicada en una carpeta hermana al backend. | Flask `send_from_directory` |

### Diagrama de Arquitectura

```mermaid
graph TD
    Client[Cliente / Navegador]
    
    subgraph "Flask Application Server"
        App[Application Factory (__init__.py)]
        API[API Blueprint (routes.py)]
        Static[Static File Serving]
        Storage[JSON Storage (tasks.json)]
    end

    Client -->|1. Request /| App
    App -->|2. Route /| Static
    Static -->|3. index.html| Client
    
    Client -->|4. Request /api/tasks| App
    App -->|5. Delegate to /api| API
    API -->|6. Read/Write| Storage
    Storage -->|7. Return Data| API
    API -->|8. JSON Response| Client
```

## Endpoints de la API

La API expone una interfaz RESTful para la manipulación de recursos de tipo "Tarea". Todas las respuestas, salvo en casos de error o eliminación exitosa, se devuelven en formato JSON.

| Método HTTP | Ruta | Descripción | Payload (Body) | Respuesta Exitosa |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/tasks` | Obtiene la lista completa de todas las tareas almacenadas. | Ninguno | `200 OK` (Array JSON de tareas) |
| **POST** | `/api/tasks` | Crea una nueva tarea. Requiere 'content'. | `{"content": string, "state": string}` (opcional) | `201 Created` (Objeto Tarea JSON) |
| **PUT** | `/api/tasks/<id>` | Actualiza una tarea existente por su ID. Permite modificar 'content' y 'state'. | `{"content": string, "state": string}` (parcial) | `200 OK` (Objeto Tarea actualizado) |
| **DELETE** | `/api/tasks/<id>` | Elimina una tarea existente por su ID. | Ninguno | `204 No Content` |

### Códigos de Error
*   **400 Bad Request:** Si falta el campo 'content' al crear una tarea.
*   **404 Not Found:** Si el ID proporcionado no corresponde a ninguna tarea existente en las operaciones PUT o DELETE.

## Instrucciones de Instalación y Ejecución

Para poner en marcha el proyecto en un entorno de desarrollo local, sigue estos pasos:

1.  **Crear y activar un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows usa: venv\Scripts\activate
    ```

2.  **Instalar las dependencias:**
    El proyecto requiere Flask. Asegúrate de instalarlo:
    ```bash
    pip install Flask
    ```

3.  **Configurar la estructura de directorios:**
    Asegúrate de que la carpeta del frontend esté ubicada correctamente. Según el código en `__init__.py`, el backend espera la siguiente estructura relativa:
    ```text
    /proyecto
      ├── backend/
      │   ├── __init__.py
      │   └── routes.py
      ├── frontend/
      │   └── index.html
      └── venv/
    ```

4.  **Ejecutar la aplicación:**
    Desde el directorio raíz (o donde esté `__init__.py`), define la variable de entorno de la aplicación Flask y ejecuta:
    ```bash
    export FLASK_APP=backend  # Ajusta según tu ubicación exacta
    flask run
    ```
    La aplicación estará disponible por defecto en `http://127.0.0.1:5000`.

## Flujo de Datos Clave

El flujo de operación de la aplicación gira en torno a la manipulación sincrónica del archivo `tasks.json`. Cuando se inicia una solicitud, el servidor no mantiene datos en memoria caché entre solicitudes diferentes; en su lugar, lee el estado actual del disco en cada operación para garantizar la coherencia, aunque esto implica un costo de rendimiento I/O.

Por ejemplo, al crear una nueva tarea mediante `POST`, el sistema primero deserializa el contenido actual del archivo JSON en una lista de Python. Luego, calcula el siguiente ID disponible buscando el valor máximo existente e incrementándolo en uno. El nuevo objeto de tarea se construye y se agrega a la lista en memoria. Inmediatamente después, esta lista se sobrescribe en el archivo de disco. Finalmente, el nuevo objeto se serializa de nuevo a JSON y se devuelve al cliente con el código de estado 201, confirmando que la persistencia ha sido exitosa.

## Extensiones Futuras

Basándonos en la arquitectura actual y el manejo de datos, se identifican las siguientes extensiones lógicas para evolucionar el proyecto:

*   **Migración a Base de Datos:** Reemplazar la persistencia en archivo JSON por una base de datos real (como SQLite o PostgreSQL) utilizando un ORM como SQLAlchemy. Esto mejoraría drásticamente el rendimiento, la concurrencia y la integridad de datos.
*   **Gestión de IDs Robusta:** Actualmente, la generación de IDs (`max_id + 1`) puede presentar problemas en entornos de alta concurrencia o si se eliminan tareas. Una extensión futura debería implementar un sistema de identificadores únicos más seguros (UUIDs).
*   **Validación de Datos:** Implementar una librería de validación (como Marshmallow o Pydantic) para asegurar que los datos entrantes cumplan con esquemas estrictos, más allá de la simple verificación de existencia de 'content'.
*   **Autenticación y Autorización:** Dado que la API es actualmente pública, añadir capas de seguridad para proteger los endpoints y asegurar que los usuarios solo gestionen sus propias tareas sería el siguiente paso natural para un entorno de producción.