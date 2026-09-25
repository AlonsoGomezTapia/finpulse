import asyncio
import logging
from decimal import Decimal

import httpx
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.alert import AlertRule, AlertStatus

logger = logging.getLogger(__name__)


async def fetch_mock_market_price(symbol: str) -> Decimal:
    """Simula la obtencion asincrona de cotizaciones de mercado."""
    mock_prices = {
        "BTC-USD": Decimal("68500.00"),
        "ETH-USD": Decimal("3550.00"),
        "AAPL": Decimal("185.50"),
    }
    await asyncio.sleep(0.01)
    return mock_prices.get(symbol.upper(), Decimal("100.00"))


async def start_market_ticker_worker(interval_seconds: int = 15) -> None:
    """Worker continuo en background que evalua reglas de alertas financieras."""
    logger.info("Iniciando worker de evaluacion de mercado...")
    client = httpx.AsyncClient(timeout=10.0)

    try:
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    symbols = ["BTC-USD", "ETH-USD", "AAPL"]
                    for sym in symbols:
                        current_price = await fetch_mock_market_price(sym)

                        query = select(AlertRule).where(
                            AlertRule.symbol == sym,
                            AlertRule.status == AlertStatus.ACTIVE,
                            AlertRule.is_deleted.is_(False),
                        )
                        result = await session.execute(query)
                        active_alerts = result.scalars().all()

                        for alert in active_alerts:
                            should_trigger = False
                            if (
                                alert.condition == ">="
                                and current_price >= alert.threshold_price
                            ):
                                should_trigger = True
                            elif (
                                alert.condition == "<="
                                and current_price <= alert.threshold_price
                            ):
                                should_trigger = True

                            if should_trigger:
                                alert.status = AlertStatus.TRIGGERED
                                logger.info(
                                    "Alerta disparada para %s a precio %s",
                                    sym,
                                    current_price,
                                )

                        await session.commit()
            except Exception as exc:
                logger.error("Error durante ciclo del worker: %s", exc)

            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("Worker detenido limpiamente.")
        raise
    finally:
        await client.aclose()
