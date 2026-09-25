import asyncio
import logging
from decimal import Decimal

import httpx

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)


async def fetch_mock_market_price(symbol: str) -> Decimal:
    """Simula la obtención de precios de mercado con httpx."""
    mock_prices = {
        "BTC-USD": Decimal("68500.00"),
        "ETH-USD": Decimal("3550.00"),
        "AAPL": Decimal("185.50"),
    }
    await asyncio.sleep(0.01)
    return mock_prices.get(symbol.upper(), Decimal("100.00"))


async def start_market_ticker_worker() -> None:
    """Worker continuo en background que evalua reglas de mercado."""
    logger.info("Iniciando worker de evaluacion de mercado...")
    client = httpx.AsyncClient(timeout=settings.API_TIMEOUT_SECONDS)
    service = AlertService()

    try:
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    symbols = ["BTC-USD", "ETH-USD", "AAPL"]
                    for sym in symbols:
                        current_price = await fetch_mock_market_price(sym)
                        triggered_count = await service.evaluate_and_trigger(
                            db=session,
                            symbol=sym,
                            current_price=current_price,
                        )
                        if triggered_count > 0:
                            logger.info(
                                "Disparadas %d alertas para %s a un precio de %s",
                                triggered_count,
                                sym,
                                current_price,
                            )
            except Exception as exc:
                logger.error("Error durante ciclo del worker de mercado: %s", exc)

            await asyncio.sleep(settings.MARKET_TICKER_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        logger.info("Worker detenido limpiamente.")
        raise
    finally:
        await client.aclose()
