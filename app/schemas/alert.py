import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.alert import AlertStatus, ConditionType

TICKER_REGEX = re.compile(r"^[A-Z0-9]{1,10}(-[A-Z0-9]{1,5})?$")


class AlertBase(BaseModel):
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=16,
        description="Ticker financiero (ej. AAPL, BTC-USD)",
    )
    condition: ConditionType = Field(
        ...,
        description="Condición: GREATER_THAN o LESS_THAN",
    )
    threshold_price: Decimal = Field(
        ...,
        gt=Decimal("0.0"),
        description="Precio umbral financiero positivo",
    )
    notification_email: EmailStr = Field(
        ...,
        description="Correo destino para notificaciones",
    )

    @field_validator("symbol")
    @classmethod
    def validate_and_normalize_symbol(cls, v: str) -> str:
        normalized = v.strip().upper()
        if not TICKER_REGEX.match(normalized):
            raise ValueError("El ticker contiene caracteres inválidos.")
        return normalized

    @field_validator("threshold_price")
    @classmethod
    def round_threshold(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.0001"))


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    threshold_price: Decimal | None = Field(default=None, gt=Decimal("0.0"))
    condition: ConditionType | None = None
    status: AlertStatus | None = None
    notification_email: EmailStr | None = None

    @field_validator("threshold_price")
    @classmethod
    def round_optional_threshold(cls, v: Decimal | None) -> Decimal | None:
        if v is not None:
            return v.quantize(Decimal("0.0001"))
        return v


class AlertResponse(AlertBase):
    id: UUID
    status: AlertStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
