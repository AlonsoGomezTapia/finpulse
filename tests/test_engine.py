import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.alert import AlertRule, AlertStatus
from app.tasks.engine import fetch_mock_market_price, start_market_ticker_worker


@pytest.mark.asyncio
async def test_fetch_mock_market_price():
    """Valida que el mock devuelva precios correctos para diferentes simbolos."""
    btc_price = await fetch_mock_market_price("BTC-USD")
    eth_price = await fetch_mock_market_price("eth-usd")
    unknown_price = await fetch_mock_market_price("UNKNOWN-COIN")

    assert btc_price == Decimal("68500.00")
    assert eth_price == Decimal("3550.00")
    assert unknown_price == Decimal("100.00")


@pytest.mark.asyncio
async def test_start_market_ticker_worker_cycle():
    """Ejecuta una iteracion simulada del worker para probar la evaluacion de alertas."""
    mock_alert = AlertRule(
        symbol="BTC-USD",
        condition=">=",
        threshold_price=Decimal("60000.00"),
        notification_email="trader@finpulse.io",
        status=AlertStatus.ACTIVE,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_alert]

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()

    mock_session_context = MagicMock()
    mock_session_context.__aenter__.return_value = mock_session
    mock_session_context.__aexit__.return_value = None

    with (
        patch("app.tasks.engine.AsyncSessionLocal", return_value=mock_session_context),
        patch("asyncio.sleep", side_effect=[None, asyncio.CancelledError()]),
    ):
        with pytest.raises(asyncio.CancelledError):
            await start_market_ticker_worker(interval_seconds=1)

    assert mock_alert.status == AlertStatus.TRIGGERED
