import pytest
from fastapi.testclient import TestClient
from fastapi_server import app  # Импортируем FastAPI приложение

# Создаем тест-клиент для взаимодействия с сервером
client = TestClient(app)

# Правильные данные авторизации
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

# Неправильные данные авторизации
INVALID_USERNAME = "wronguser"
INVALID_PASSWORD = "wrongpassword"

# Функция для генерации заголовка с базовой авторизацией
def get_auth_headers(username, password):
    return {
        "Authorization": f"Basic {username}:{password}"
    }

@pytest.fixture
def auth_headers():
    return {
        "valid": (VALID_USERNAME, VALID_PASSWORD),
        "invalid": (INVALID_USERNAME, INVALID_PASSWORD)
    }

def test_authorization_success(auth_headers):
    response = client.get("/cpu", auth=auth_headers['valid'])
    assert response.status_code == 200  # Убедимся, что запрос успешен

def test_authorization_failure(auth_headers):
    response = client.get("/cpu", auth=auth_headers['invalid'])
    assert response.status_code == 401  # Ожидаем ошибку авторизации

def test_get_cpu_info(auth_headers):
    response = client.get("/cpu", auth=auth_headers['valid'])
    assert response.status_code == 200
    assert "cpu_percent" in response.json()  # Проверим, что данные о CPU содержатся в ответе

def test_get_memory_info(auth_headers):
    response = client.get("/memory", auth=auth_headers['valid'])
    assert response.status_code == 200
    assert "total" in response.json()  # Проверим, что данные о памяти содержатся в ответе

def test_get_disk_info(auth_headers):
    response = client.get("/disk", auth=auth_headers['valid'])
    assert response.status_code == 200
    assert len(response.json()) > 0  # Проверим, что данные о дисках содержатся в ответе

def test_get_network_info(auth_headers):
    response = client.get("/network", auth=auth_headers['valid'])
    assert response.status_code == 200
    assert "bytes_sent" in response.json()  # Проверим, что данные о сети содержатся в ответе

def test_get_system_summary(auth_headers):
    response = client.get("/summary", auth=auth_headers['valid'])
    assert response.status_code == 200
    summary = response.json()
    assert "cpu" in summary
    assert "memory" in summary
    assert "disk" in summary
    assert "network" in summary

def test_dashboard_redirect(auth_headers):
    response = client.get("/dashboard", auth=auth_headers['valid'])
    assert response.status_code == 307  # Проверим, что происходит перенаправление (код 307)
    assert response.headers["location"] == "http://127.0.0.1:8050"  # Проверим, что перенаправление идет на дашборд
