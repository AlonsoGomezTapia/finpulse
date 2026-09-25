import asyncio
import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.alert import AlertRule, AlertStatus, ConditionType

logger = logging.getLogger("finpulse.engine")


class AlertEvaluationEngine:
    """Motor asincrono para evaluar reglas frente a cotizaciones de mercado."""

    async def evaluate_price(
        self,
        db: AsyncSession,
        symbol: str,
        current_price: Decimal,
    ) -> list[AlertRule]:
        query = select(AlertRule).where(
            AlertRule.symbol == symbol,
            AlertRule.status == AlertStatus.ACTIVE,
            AlertRule.is_deleted.is_(False),
        )
        result = await db.execute(query)
        active_rules = result.scalars().all()

        triggered_alerts: list[AlertRule] = []

        for rule in active_rules:
            should_trigger = False
            if (
                rule.condition == ConditionType.GREATER_THAN
                and current_price >= rule.threshold_price
            ):
                should_trigger = True
            elif (
                rule.condition == ConditionType.LESS_THAN
                and current_price <= rule.threshold_price
            ):
                should_trigger = True

            if should_trigger:
                rule.status = AlertStatus.TRIGGERED
                triggered_alerts.append(rule)
                logger.warning(
                    "ALERTA DISPARADA: [%s] Precio: %s %s Umbral: %s (Destino: %s)",
                    rule.symbol,
                    current_price,
                    rule.condition.value,
                    rule.threshold_price,
                    rule.notification_email,
                )

        if triggered_alerts:
            await db.commit()

        return triggered_alerts


async def start_market_ticker_worker(interval_seconds: int = 15) -> None:
    engine = AlertEvaluationEngine()
    logger.info("Iniciando Market Ticker Background Worker...")

    sample_quotes = {
        "BTC-USD": Decimal("67500.0000"),
        "AAPL": Decimal("225.5000"),
        "ETH-USD": Decimal("3500.2500"),
    }

    try:
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    for symbol, base_price in sample_quotes.items():
                        await engine.evaluate_price(session, symbol, base_price)
            except Exception as e:
                logger.error("Error en ciclo del worker: %s", str(e))

            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("Worker detenido limpiamente.")
        raise