import pytest
from aiohttp import web
from app.routes import setup_routes
from app.middlewares import error_middleware

@pytest.fixture
def client(aiohttp_client):
    app = web.Application(middlewares=[error_middleware])
    setup_routes(app)
    return aiohttp_client(app)

@pytest.mark.asyncio
async def test_ping(client):
    test_client = await client  
    resp = await test_client.get("/ping")
    assert resp.status == 200
    data = await resp.json()
    assert data == {"message": "pong"}

@pytest.mark.asyncio
async def test_get_schools(client):
    test_client = await client
    resp = await test_client.get("/schools")
    assert resp.status == 200

    data = await resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert "city" in data[0]

@pytest.mark.asyncio
async def test_create_school(client):
    test_client = await client
    payload = {
        "name": "Escuela de Pruebas",
        "city": "Testópolis"
    }
    resp = await test_client.post("/schools", json=payload)
    assert resp.status == 201

    data = await resp.json()
    assert data["name"] == "Escuela de Pruebas"
    assert data["city"] == "Testópolis"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_school_missing_fields(client):
    test_client = await client
    payload = {"name": "Solo nombre"}
    resp = await test_client.post("/schools", json=payload)
    assert resp.status == 400
    data = await resp.json()
    assert "error" in data
    assert "city" in data["error"]

@pytest.mark.asyncio
async def test_create_school_invalid_type(client):
    test_client = await client
    payload = {"name": 123, "city": "NumCity"}
    resp = await test_client.post("/schools", json=payload)
    assert resp.status == 400
    data = await resp.json()
    assert "error" in data
    assert "'name' must be a string" in data["error"]

@pytest.mark.asyncio
async def test_create_school_unexpected_field(client):
    test_client = await client
    payload = {
        "name": "Inesperada",
        "city": "Ciudad",
        "telefono": "99999999"
    }
    resp = await test_client.post("/schools", json=payload)
    assert resp.status == 400
    data = await resp.json()
    assert "error" in data
    assert "Unexpected fields" in data["error"]


@pytest.mark.asyncio
async def test_update_school(client):
    test_client = await client

    # Creamos una escuela para luego actualizarla
    payload = {"name": "Escuela Original", "city": "Ciudad Original"}
    create_resp = await test_client.post("/schools", json=payload)
    created_school = await create_resp.json()
    school_id = created_school["id"]

    
    update_payload = {"name": "Escuela Actualizada"}
    update_resp = await test_client.put(f"/schools/{school_id}", json=update_payload)
    assert update_resp.status == 200

    updated_data = await update_resp.json()
    assert updated_data["id"] == school_id
    assert updated_data["name"] == "Escuela Actualizada"
    assert updated_data["city"] == "Ciudad Original"

@pytest.mark.asyncio
async def test_delete_school(client):
    test_client = await client

    # Creamos una escuela para luego eliminarla
    payload = {"name": "Escuela Temporal", "city": "Ciudad Temporal"}
    create_resp = await test_client.post("/schools", json=payload)
    created_school = await create_resp.json()
    school_id = created_school["id"]

    # Eliminamos la escuela
    delete_resp = await test_client.delete(f"/schools/{school_id}")
    assert delete_resp.status == 200

    delete_data = await delete_resp.json()
    assert delete_data["message"] == "School deleted"
    assert delete_data["school"]["id"] == school_id

    # Confirmamos que ya no existe
    get_resp = await test_client.get(f"/schools/{school_id}")
    assert get_resp.status == 404
