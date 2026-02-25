import pytest
import json
import os
from backend import create_app

# Importamos la variable que vamos a parchear para redirigir el archivo de datos
from backend.routes import TASKS_FILE


@pytest.fixture
def app():
    """Fixture que crea la aplicación para testing."""
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    """Fixture que crea el cliente de test de Flask."""
    return app.test_client()


@pytest.fixture
def temp_file(tmp_path, monkeypatch):
    """
    Fixture que crea un archivo temporal y parchea la ruta global TASKS_FILE.
    Esto asegura que los tests no toquen el archivo real 'tasks.json'.
    """
    # Crear un archivo temporal en el directorio de tmp_path
    file_path = tmp_path / "test_tasks.json"
    # Parchear la variable TASKS_FILE en el módulo routes para usar el temporal
    monkeypatch.setattr('backend.routes.TASKS_FILE', str(file_path))
    yield file_path


def test_get_tasks_empty(client, temp_file):
    """Verifica que GET /api/tasks devuelve una lista vacía si no hay tareas."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert response.json == []


def test_create_task(client, temp_file):
    """Verifica que POST /api/tasks crea una tarea correctamente."""
    payload = {
        'content': 'Nueva tarea de prueba',
        'state': 'Por Hacer'
    }
    response = client.post('/api/tasks', json=payload)
    
    assert response.status_code == 201
    data = response.json
    assert data['content'] == 'Nueva tarea de prueba'
    assert data['state'] == 'Por Hacer'
    assert 'id' in data
    assert data['id'] == 1


def test_get_tasks_after_creation(client, temp_file):
    """Verifica que las tareas persisten tras ser creadas."""
    # Crear tarea
    client.post('/api/tasks', json={'content': 'Tarea 1'})
    # Obtener tareas
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['content'] == 'Tarea 1'


def test_update_task_state(client, temp_file):
    """Verifica que PUT /api/tasks/<id> actualiza el estado de una tarea."""
    # 1. Crear tarea
    create_res = client.post('/api/tasks', json={'content': 'Mover tarea'})
    task_id = create_res.json['id']
    
    # 2. Actualizar estado
    update_payload = {'state': 'Hecho'}
    update_res = client.put(f'/api/tasks/{task_id}', json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json['state'] == 'Hecho'
    assert update_res.json['content'] == 'Mover tarea' # El contenido no cambia


def test_update_task_content(client, temp_file):
    """Verifica que PUT /api/tasks/<id> actualiza el contenido de una tarea."""
    create_res = client.post('/api/tasks', json={'content': 'Texto original'})
    task_id = create_res.json['id']
    
    update_res = client.put(f'/api/tasks/{task_id}', json={'content': 'Texto editado'})
    
    assert update_res.status_code == 200
    assert update_res.json['content'] == 'Texto editado'


def test_delete_task(client, temp_file):
    """Verifica que DELETE /api/tasks/<id> elimina la tarea."""
    # Crear dos tareas
    client.post('/api/tasks', json={'content': 'Tarea a borrar'})
    client.post('/api/tasks', json={'content': 'Tarea que se queda'})
    
    # Obtener IDs (asumimos que son 1 y 2)
    tasks_res = client.get('/api/tasks')
    tasks = tasks_res.json
    id_to_delete = tasks[0]['id']
    
    # Borrar la primera
    del_res = client.delete(f'/api/tasks/{id_to_delete}')
    assert del_res.status_code == 204
    
    # Verificar que solo queda una
    final_res = client.get('/api/tasks')
    assert len(final_res.json) == 1
    assert final_res.json[0]['content'] == 'Tarea que se queda'


def test_update_non_existent_task(client, temp_file):
    """Verifica comportamiento al intentar actualizar una tarea inexistente."""
    res = client.put('/api/tasks/999', json={'state': 'Hecho'})
    assert res.status_code == 404
    assert 'error' in res.json


def test_delete_non_existent_task(client, temp_file):
    """Verifica comportamiento al intentar borrar una tarea inexistente."""
    res = client.delete('/api/tasks/999')
    assert res.status_code == 404