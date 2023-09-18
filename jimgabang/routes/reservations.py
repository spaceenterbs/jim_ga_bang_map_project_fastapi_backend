# 이벤트 생성, 변경, 삭제 등의 처리를 위한 라우팅
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from database.connections import Database
from models.reservations import (
    Service,
    ServiceUpdate,
    Booking,
    BookingUpdate,
    BookingConfirmUpdate,
)
from typing import List
from auth.authenticate import authenticate


service_router = APIRouter(
    tags=["Service"],
)
booking_router = APIRouter(
    tags=["Booking"],
)

service_database = Database(Service)
booking_database = Database(Booking)

# services = []


# 모든 이벤트를 추출하거나 특정 ID의 이벤트만 추출하는 라우트를 정의한다.
@service_router.get("/", response_model=List[Service])
async def retrieve_all_services() -> List[Service]:
    services = await service_database.get_all()
    return services


# 특정 ID의 이벤트만 추출하는 라우트에서는 해당 ID의 이벤트가 없으면 HTTP_404_NOT_FOUND 예외를 발생시킨다.
@service_router.get("/{id}", response_model=Service)
async def retrieve_service(id: PydanticObjectId) -> Service:
    service = await service_database.get(id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )
    return service


# 이벤트 생성 및 삭제 라우트를 정의한다. 마지막은 전체 이벤트 삭제다.
@service_router.post("/new")
async def create_service(
    body: Service, host: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    body.creator = host  # 새로운 이벤트가 생성될 때 creator 필드가 함께 저장되도록 한다.
    await service_database.save(body)
    # services.append(body)
    return {
        "message": "Service created successfully",
    }


@service_router.delete("/{id}")
async def delete_service(
    id: PydanticObjectId, host: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    service = await service_database.get(id)
    if service.creator != host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not allowed",
        )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )
    await service_database.delete(id)

    return {
        "message": "Service deleted successfully",
    }


# 변경(update) 라우트는 실제 데이터베이스와 연동할 때 구현한다.
@service_router.put("/{id}", response_model=Service)
async def update_service(
    id: PydanticObjectId,
    body: ServiceUpdate,
    host: str = Depends(authenticate),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Service:
    service = await service_database.get(id)
    if service.creator != host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )
    updated_service = await service_database.update(id, body)
    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Service update has been made",
        )
    return updated_service


"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""

# bookings = []


# 모든 이벤트를 추출하거나 특정 ID의 이벤트만 추출하는 라우트를 정의한다.
@booking_router.get("/", response_model=List[Booking])
async def retrieve_all_bookings() -> List[Booking]:
    bookings = await booking_database.get_all()
    return bookings


# 특정 ID의 이벤트만 추출하는 라우트에서는 해당 ID의 이벤트가 없으면 HTTP_404_NOT_FOUND 예외를 발생시킨다.
@booking_router.get("/{id}", response_model=Booking)
async def retrieve_booking(id: PydanticObjectId) -> Booking:
    booking = await booking_database.get(id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )
    return booking


# 이벤트 생성 및 삭제 라우트를 정의한다. 마지막은 전체 이벤트 삭제다.
@booking_router.post("/new")
async def create_booking(
    body: Booking, client: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    body.creator = client  # 새로운 이벤트가 생성될 때 creator 필드가 함께 저장되도록 한다.
    await booking_database.save(body)
    # bookings.append(body)
    return {
        "message": "Booking created successfully",
    }


@booking_router.delete("/{id}")
async def delete_booking(
    id: PydanticObjectId, client: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    booking = await booking_database.get(id)
    if booking.creator != client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not allowed",
        )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )
    await booking_database.delete(id)

    return {
        "message": "Booking deleted successfully",
    }


@booking_router.put("/{id}", response_model=Booking)
async def update_booking(
    id: PydanticObjectId,
    body: BookingUpdate,
    client: str = Depends(authenticate),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Booking:
    booking = await booking_database.get(id)
    if booking.creator != client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )
    updated_booking = await booking_database.update(id, body)
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Booking update has been made",
        )
    return updated_booking


# confirm 수정
@booking_router.put("/{id}/confirm", response_model=Booking)
async def update_booking_confirm(
    id: PydanticObjectId,
    body: BookingConfirmUpdate,
    host: str = Depends(authenticate),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Booking:
    booking = await booking_database.get(id)
    if booking.creator != host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )
    updated_booking = await booking_database.update(id, body)
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Booking update has been made",
        )
    return updated_booking
