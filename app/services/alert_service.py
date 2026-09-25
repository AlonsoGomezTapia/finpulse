from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException
from app.models.alert import AlertRule, AlertStatus
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_alert(self, payload: AlertCreate) -> AlertRule:
        alert = AlertRule(
            symbol=payload.symbol,
            condition=payload.condition,
            threshold_price=payload.threshold_price,
            notification_email=payload.notification_email,
            status=AlertStatus.ACTIVE,
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_by_id(self, alert_id: UUID) -> AlertRule:
        query = select(AlertRule).where(
            AlertRule.id == alert_id,
            AlertRule.is_deleted.is_(False),
        )
        result = await self.db.execute(query)
        alert = result.scalar_one_or_none()
        if alert is None:
            raise EntityNotFoundException(
                entity_name="AlertRule", identifier=str(alert_id)
            )
        return alert

    async def list_alerts(
        self,
        symbol: str | None = None,
        status: AlertStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[AlertRule]:
        query = select(AlertRule).where(AlertRule.is_deleted.is_(False))
        if symbol:
            query = query.where(AlertRule.symbol == symbol.strip().upper())
        if status:
            query = query.where(AlertRule.status == status)

        safe_limit = min(limit, 100)
        query = (
            query.offset(skip).limit(safe_limit).order_by(AlertRule.created_at.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_alert(self, alert_id: UUID, payload: AlertUpdate) -> AlertRule:
        alert = await self.get_by_id(alert_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def soft_delete(self, alert_id: UUID) -> None:
        alert = await self.get_by_id(alert_id)
        alert.is_deleted = True
        alert.status = AlertStatus.DISABLED
        await self.db.commit()
