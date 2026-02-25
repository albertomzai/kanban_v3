import json
import os
from pathlib import Path
from flask import Blueprint, request, jsonify

# Definir el Blueprint para las rutas de la API
api_bp = Blueprint('api', __name__)

# Definir la ruta del archivo de persistencia de datos.
# Se ubica en la raíz del proyecto (../ desde backend/)
DATA_FILE = Path(__file__).parent.parent / 'tasks.json'


def _leer_tareas():
    """
    Lee la lista de tareas desde el archivo JSON.
    Retorna una lista vacía si el archivo no existe o hay un error de lectura.
    """
    try:
        if not DATA_FILE.exists():
            return []
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return []


def _guardar_tareas(tareas):
    """
    Escribe la lista de tareas en el archivo JSON.
    """
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tareas, f, indent=4, ensure_ascii=False)
    except IOError as e:
        # En un caso real, aquí se loguearía el error
        print(f"Error guardando tareas: {e}")


@api_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    Endpoint GET: Devuelve todas las tareas existentes.
    """
    tareas = _leer_tareas()
    return jsonify(tareas)


@api_bp.route('/api/tasks', methods=['POST'])
def create_task():
    """
    Endpoint POST: Crea una nueva tarea.
    Espera un JSON con 'content' y opcionalmente 'state'.
    """
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'El campo "content" es obligatorio'}), 400

    tareas = _leer_tareas()
    # Generar un ID simple basado en la longitud actual (no seguro para concurrencia, pero válido para el ejemplo)
    nuevo_id = max([t.get('id', 0) for t in tareas], default=0) + 1

    nueva_tarea = {
        'id': nuevo_id,
        'content': data['content'],
        'state': data.get('state', 'Por Hacer')
    }

    tareas.append(nueva_tarea)
    _guardar_tareas(tareas)

    return jsonify(nueva_tarea), 201


@api_bp.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    """
    Endpoint PUT: Actualiza una tarea existente.
    Permite modificar 'content' y/o 'state'.
    """
    tareas = _leer_tareas()
    tarea_encontrada = None

    for tarea in tareas:
        if tarea['id'] == id:
            tarea_encontrada = tarea
            break

    if not tarea_encontrada:
        return jsonify({'error': 'Tarea no encontrada'}), 404

    data = request.get_json()
    if 'content' in data:
        tarea_encontrada['content'] = data['content']
    if 'state' in data:
        tarea_encontrada['state'] = data['state']

    _guardar_tareas(tareas)
    return jsonify(tarea_encontrada)


@api_bp.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    """
    Endpoint DELETE: Elimina una tarea existente.
    """
    tareas = _leer_tareas()
    tareas_filtradas = [t for t in tareas if t['id'] != id]

    if len(tareas) == len(tareas_filtradas):
        return jsonify({'error': 'Tarea no encontrada'}), 404

    _guardar_tareas(tareas_filtradas)
    return '', 204