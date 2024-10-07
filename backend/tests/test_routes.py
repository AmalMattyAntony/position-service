from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(name="client")
def setup(monkeypatch: MagicMock):
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("POSTGRES_DB", "test")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("VERSION", "v1")
    from src.main import app
    from src.db.session import add_postgresql_extension

    # TODO: this doesn't seem to be enabling/creating the gist extension in test database (leading to gist index creation failure)
    add_postgresql_extension()
    from src.db.init_db import initialize

    initialize()
    return TestClient(app)


def test_health(client):
    response = client.get("/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}


def test_store_invalid_position(client):
    response = client.post(
        "/v1/storeposition",
        json={"vesselid": "test-01", "timehours": 100, "x": 1, "y": 2, "z": "hello"},
    )
    with pytest.raises(Exception):
        assert response.raise_for_status()


def test_store_valid_position(client):
    position = {"vesselid": "test-01", "timehours": 100, "x": 1, "y": 2, "z": 2}

    response = client.post(
        "/v1/storeposition",
        json=position,
    )
    assert response.status_code == 200, response.json()

    response = client.get(
        "/v1/getposition?timehours=100&vesselid=test-01",
    )
    assert response.status_code == 200
    assert response.json() == position


def test_update_position(client):
    position = {"vesselid": "test-01", "timehours": 100, "x": 9, "y": 9, "z": 9}

    response = client.post(
        "/v1/storeposition",
        json=position,
    )
    assert response.status_code == 200, response.json()

    response = client.get(
        "/v1/getposition?timehours=100&vesselid=test-01",
    )
    assert response.status_code == 200
    assert response.json() == position

    updated_position = {"vesselid": "test-01", "timehours": 100, "x": 0, "y": 0, "z": 0}
    response = client.post(
        "/v1/storeposition",
        json=updated_position,
    )
    response = client.get(
        "/v1/getposition?timehours=100&vesselid=test-01",
    )
    assert response.status_code == 200
    assert response.json() == updated_position


def test_series(client):
    updated_position = {"vesselid": "test-01", "timehours": 100, "x": 0, "y": 0, "z": 0}
    response = client.get(
        "/v1/getseries",
    )
    assert response.status_code == 200
    assert response.json() == [updated_position]


def test_nearest(client):
    response = client.post(
        "/v1/storeposition",
        json={"vesselid": "test-03", "timehours": 101, "x": 0, "y": 0, "z": 0},
    )
    for i in range(10, 100, 10):
        position = {"vesselid": "test-02", "timehours": i, "x": 0, "y": 0, "z": 0}
        response = client.post(
            "/v1/storeposition",
            json=position,
        )
        assert response.status_code == 200

    response = client.get(
        "/v1/getposition?timehours=110&vesselid=test-02",
    )
    assert response.status_code == 200
    assert response.json() == {"vesselid": "test-02", "timehours": 90, "x": 0, "y": 0, "z": 0}

    # nearest without filtering on vessel is still the test-03 entry
    response = client.get(
        "/v1/getposition?timehours=110",
    )
    assert response.status_code == 200
    assert response.json() == {"vesselid": "test-03", "timehours": 101, "x": 0, "y": 0, "z": 0}
