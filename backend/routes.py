import json
import os
from flask import Blueprint, request, jsonify, current_app

# Definición del Blueprint para la API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Ruta del archivo de persistencia
TASKS_FILE = 'tasks.json'


def _leer_tareas():
    """
    Lee la lista de tareas desde el archivo JSON.
    Si el archivo no existe o está vacío, devuelve una lista vacía.
    """
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _guardar_tareas(tareas):
    """
    Escribe la lista de tareas en el archivo JSON.
    """
    with open(TASKS_FILE, 'w') as f:
        json.dump(tareas, f, indent=4)


@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Endpoint para obtener todas las tareas.
    """
    tareas = _leer_tareas()
    return jsonify(tareas)


@api_bp.route('/tasks', methods=['POST'])
def create_task():
    """
    Endpoint para crear una nueva tarea.
    Espera un JSON con 'content' y opcionalmente 'state'.
    """
    data = request.get_json()
    contenido = data.get('content', '')
    estado = data.get('state', 'Por Hacer')

    if not contenido:
        return jsonify({'error': 'El contenido es obligatorio'}), 400

    tareas = _leer_tareas()
    # Generar un ID simple (max ID + 1)
    max_id = 0
    if tareas:
        max_id = max(t.get('id', 0) for t in tareas)
    nueva_tarea = {
        'id': max_id + 1,
        'content': contenido,
        'state': estado
    }
    tareas.append(nueva_tarea)
    _guardar_tareas(tareas)

    return jsonify(nueva_tarea), 201


@api_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    """
    Endpoint para actualizar una tarea existente.
    Permite modificar 'content' y 'state'.
    """
    tareas = _leer_tareas()
    data = request.get_json()

    for tarea in tareas:
        if tarea['id'] == id:
            if 'content' in data:
                tarea['content'] = data['content']
            if 'state' in data:
                tarea['state'] = data['state']
            _guardar_tareas(tareas)
            return jsonify(tarea)

    return jsonify({'error': 'Tarea no encontrada'}), 404


@api_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    """
    Endpoint para eliminar una tarea.
    """
    tareas = _leer_tareas()
    nuevas_tareas = [t for t in tareas if t['id'] != id]

    if len(tareas) == len(nuevas_tareas):
        return jsonify({'error': 'Tarea no encontrada'}), 404

    _guardar_tareas(nuevas_tareas)
    return '', 204