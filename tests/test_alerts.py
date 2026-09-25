import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Verifica que el healthcheck responda 200 y status healthy."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "environment": "development"}


@pytest.mark.asyncio
async def test_create_alert_success(client: AsyncClient) -> None:
    """Verifica la creacion de una alerta y normalizacion de ticker."""
    payload = {
        "symbol": "btc-usd",
        "condition": "GREATER_THAN",
        "threshold_price": 70000.50,
        "notification_email": "trader@finpulse.dev",
    }
    response = await client.post("/api/v1/alerts", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["symbol"] == "BTC-USD"
    assert data["status"] == "ACTIVE"
    assert float(data["threshold_price"]) == 70000.5
    assert "id" in data


@pytest.mark.asyncio
async def test_create_alert_invalid_symbol(client: AsyncClient) -> None:
    """Valida rechazo de simbolos invalidos."""
    payload = {
        "symbol": "INVALID$$$SYMBOL",
        "condition": "GREATER_THAN",
        "threshold_price": 100.0,
        "notification_email": "trader@finpulse.dev",
    }
    response = await client.post("/api/v1/alerts", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_and_get_alert(client: AsyncClient) -> None:
    """Prueba el listado y la consulta por ID."""
    # 1. Crear alerta
    create_res = await client.post(
        "/api/v1/alerts",
        json={
            "symbol": "AAPL",
            "condition": "LESS_THAN",
            "threshold_price": 190.0,
            "notification_email": "investor@finpulse.dev",
        },
    )
    alert_id = create_res.json()["id"]

    # 2. Listar
    list_res = await client.get("/api/v1/alerts")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1

    # 3. Obtener por ID
    get_res = await client.get(f"/api/v1/alerts/{alert_id}")
    assert get_res.status_code == 200
    assert get_res.json()["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_get_alert_not_found(client: AsyncClient) -> None:
    """Verifica respuesta 404 bajo formato RFC 7807."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/alerts/{fake_uuid}")
    assert response.status_code == 404
    data = response.json()
    assert data["title"] == "Resource Not Found"
    assert fake_uuid in data["detail"]


@pytest.mark.asyncio
async def test_update_and_delete_alert(client: AsyncClient) -> None:
    """Prueba actualizacion parcial PATCH y borrado logico DELETE."""
    # 1. Crear
    create_res = await client.post(
        "/api/v1/alerts",
        json={
            "symbol": "ETH-USD",
            "condition": "GREATER_THAN",
            "threshold_price": 3000.0,
            "notification_email": "eth@finpulse.dev",
        },
    )
    alert_id = create_res.json()["id"]

    # 2. Modificar umbral
    patch_res = await client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={"threshold_price": 3200.0},
    )
    assert patch_res.status_code == 200
    assert float(patch_res.json()["threshold_price"]) == 3200.0

    # 3. Soft delete
    del_res = await client.delete(f"/api/v1/alerts/{alert_id}")
    assert del_res.status_code == 204

    # 4. Confirmar que ya no existe para busquedas
    verify_res = await client.get(f"/api/v1/alerts/{alert_id}")
    assert verify_res.status_code == 404
