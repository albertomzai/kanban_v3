import pytest
import json
from pathlib import Path
from backend import create_app
import backend.routes


@pytest.fixture
def app():
    """
    Fixture que proporciona la instancia de la aplicación para testing.
    """
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    """
    Fixture que proporciona el cliente de prueba de Flask.
    """
    return app.test_client()


@pytest.fixture
def temp_file(tmp_path, monkeypatch):
    """
    Fixture que redirige la escritura del archivo tasks.json a un archivo temporal.
    Usa monkeypatch para aislar los tests del sistema de archivos real.
    """
    # Crear un archivo temporal en el directorio proporcionado por pytest
    file_path = tmp_path / "tasks.json"
    # Inicializar el archivo temporal con una lista vacía
    file_path.write_text("[]")
    
    # Parchear la variable DATA_FILE en el módulo backend.routes
    monkeypatch.setattr("backend.routes.DATA_FILE", file_path)
    
    yield file_path


def test_get_tasks_empty(client, temp_file):
    """Prueba obtener tareas cuando no hay ninguna."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json == []


def test_create_task(client, temp_file):
    """Prueba la creación de una nueva tarea."""
    payload = {"content": "Nueva tarea de prueba", "state": "Por Hacer"}
    response = client.post("/api/tasks", json=payload)
    
    assert response.status_code == 201
    data = response.json
    assert data['id'] == 1
    assert data['content'] == "Nueva tarea de prueba"
    assert data['state'] == "Por Hacer"


def test_get_tasks_after_create(client, temp_file):
    """Prueba obtener la lista después de crear una tarea."""
    payload = {"content": "Tarea para listar"}
    client.post("/api/tasks", json=payload)
    
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['content'] == "Tarea para listar"


def test_update_task(client, temp_file):
    """Prueba actualizar el contenido y estado de una tarea."""
    # 1. Crear tarea
    create_res = client.post("/api/tasks", json={"content": "Tarea original"})
    task_id = create_res.json['id']
    
    # 2. Actualizar tarea
    update_payload = {"content": "Tarea modificada", "state": "En Progreso"}
    update_res = client.put(f"/api/tasks/{task_id}", json=update_payload)
    
    assert update_res.status_code == 200
    data = update_res.json
    assert data['content'] == "Tarea modificada"
    assert data['state'] == "En Progreso"


def test_delete_task(client, temp_file):
    """Prueba eliminar una tarea existente."""
    # 1. Crear tarea
    create_res = client.post("/api/tasks", json={"content": "Tarea a borrar"})
    task_id = create_res.json['id']
    
    # 2. Eliminar tarea
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 204
    
    # 3. Verificar que ya no existe
    get_res = client.get("/api/tasks")
    assert len(get_res.json) == 0


def test_delete_nonexistent_task(client, temp_file):
    """Prueba intentar eliminar una tarea que no existe."""
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404
    assert 'error' in response.json