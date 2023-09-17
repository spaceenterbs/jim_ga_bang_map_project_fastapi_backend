# 이벤트 생성, 변경, 삭제 등의 처리를 위한 라우팅
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from database.connections import Database
from models.reservations import (
    Opening,
    OpeningUpdate,
    Booking,
    BookingUpdate,
    BookingConfirmUpdate,
)
from typing import List
from auth.authenticate import authenticate


opening_router = APIRouter(
    tags=["Opening"],
)
booking_router = APIRouter(
    tags=["Booking"],
)

opening_database = Database(Opening)
booking_database = Database(Booking)


# 모든 이벤트를 추출하거나 특정 ID의 이벤트만 추출하는 라우트를 정의한다.
@opening_router.get("/", response_model=List[Opening])
async def retrieve_all_openings() -> List[Opening]:
    openings = await opening_database.get_all()
    return openings


# 특정 ID의 이벤트만 추출하는 라우트에서는 해당 ID의 이벤트가 없으면 HTTP_404_NOT_FOUND 예외를 발생시킨다.
@opening_router.get("/{id}", response_model=Opening)
async def retrieve_opening(id: PydanticObjectId) -> Opening:
    opening = await opening_database.get(id)
    if not opening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opening with supplied ID does not exist",
        )
    return opening


# 이벤트 생성 및 삭제 라우트를 정의한다. 마지막은 전체 이벤트 삭제다.
@opening_router.post("/new")
async def create_opening(
    body: Opening, server: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    body.creator = server  # 새로운 이벤트가 생성될 때 creator 필드가 함께 저장되도록 한다.
    await opening_database.save(body)
    # openings.append(body)
    return {
        "message": "Opening created successfully",
    }


@opening_router.delete("/{id}")
async def delete_opening(
    id: PydanticObjectId, server: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    opening = await opening_database.get(id)
    if opening.creator != server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not allowed",
        )
    if not opening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opening with supplied ID does not exist",
        )
    await opening_database.delete(id)

    return {
        "message": "Opening deleted successfully",
    }


openings = []


@opening_router.delete("/")
async def delete_all_openings() -> dict:
    openings.clear()
    return {
        "message": "All openings deleted successfully",
    }


# 변경(update) 라우트는 실제 데이터베이스와 연동할 때 구현한다.
@opening_router.put("/{id}", response_model=Opening)
async def update_opening(
    id: PydanticObjectId,
    body: OpeningUpdate,
    server: str = Depends(authenticate),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Opening:
    opening = await opening_database.get(id)
    if opening.creator != server:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )
    updated_opening = await opening_database.update(id, body)
    if not updated_opening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opening with supplied ID does not exist",
        )
    return updated_opening


"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""


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


bookings = []


@booking_router.delete("/")
async def delete_all_bookings() -> dict:
    bookings.clear()
    return {
        "message": "All bookings deleted successfully",
    }


# 변경(update) 라우트는 실제 데이터베이스와 연동할 때 구현한다.
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
            detail="Booking with supplied ID does not exist",
        )
    return updated_booking


# confirm 수정
@booking_router.put("/{id}/confirm", response_model=Booking)
async def update_booking_confirm(
    id: PydanticObjectId,
    body: BookingConfirmUpdate,
    server: str = Depends(authenticate),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Booking:
    booking = await booking_database.get(id)
    if booking.creator != server:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )
    updated_booking = await booking_database.update(id, body)
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )
    return updated_booking
