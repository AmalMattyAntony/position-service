from typing import Optional, Annotated
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlmodel import SQLModel

from src.api.v1 import health
from pydantic import BaseModel, AfterValidator
from src.models.position import Position
from src.api.v1.position_service import PositionService

api_router = APIRouter()

position_service = PositionService()


@api_router.post("/storeposition", response_description="Store Position")
def store_position(
    payload: Annotated[Position, AfterValidator(Position.model_validate)]
) -> Response:
    response = position_service.store_position(payload)
    return PlainTextResponse(
        response, status_code=status.HTTP_200_OK
    )


@api_router.get("/getposition", response_description="", include_in_schema=False)
def get_position(timehours: int, vesselid: Optional[str] = None) -> Response:
    response = position_service.get_position(timehours=timehours, vessel_id=vesselid)
    if response:
        return PlainTextResponse(
            response, status_code=status.HTTP_200_OK
        )
    raise HTTPException(status_code=404, detail="No positions available")


@api_router.get("/getseries", response_description="", include_in_schema=False)
def get_series(vesselid: Optional[str] = None) -> Response:
    return PlainTextResponse(position_service.get_series(vesselid), status_code=status.HTTP_200_OK)


api_router.include_router(health.router)
