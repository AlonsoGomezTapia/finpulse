from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.alert import AlertStatus
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def get_alert_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AlertService:
    """Fábrica de dependencias para el servicio de alertas."""
    return AlertService(db=db)


# Alias tipado reutilizable para la inyección de dependencias
AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva regla de alerta",
)
async def create_alert(
    payload: AlertCreate,
    service: AlertServiceDep,
) -> AlertResponse:
    alert = await service.create_alert(payload)
    return AlertResponse.model_validate(alert)


@router.get(
    "",
    response_model=list[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar reglas de alerta activas",
)
async def list_alerts(
    service: AlertServiceDep,
    symbol: Annotated[
        str | None,
        Query(description="Filtrar por ticker (ej. BTC-USD)"),
    ] = None,
    status: Annotated[
        AlertStatus | None,
        Query(description="Filtrar por estado"),
    ] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> Sequence[AlertResponse]:
    alerts = await service.list_alerts(
        symbol=symbol, status=status, skip=skip, limit=limit
    )
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una alerta por ID",
)
async def get_alert(
    alert_id: UUID,
    service: AlertServiceDep,
) -> AlertResponse:
    alert = await service.get_by_id(alert_id)
    return AlertResponse.model_validate(alert)


@router.patch(
    "/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente una regla de alerta",
)
async def update_alert(
    alert_id: UUID,
    payload: AlertUpdate,
    service: AlertServiceDep,
) -> AlertResponse:
    alert = await service.update_alert(alert_id, payload)
    return AlertResponse.model_validate(alert)


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminación lógica de una alerta",
)
async def delete_alert(
    alert_id: UUID,
    service: AlertServiceDep,
) -> None:
    await service.soft_delete(alert_id)
