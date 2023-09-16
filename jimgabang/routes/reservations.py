# 이벤트 생성, 변경, 삭제 등의 처리를 위한 라우팅
from beanie import PydanticObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status
from database.connection import Database
from models.events import Event, EventUpdate
from typing import List
from auth.authenticate import authenticate


event_router = APIRouter(
    tags=["Event"],
)

event_database = Database(Event)

# events = []  # 이벤트 데이터를 관리하기 위한 목적. 데이터를 리스트에 추가하거나 삭제하는 데 사용된다.


# 모든 이벤트를 추출하거나 특정 ID의 이벤트만 추출하는 라우트를 정의한다.
@event_router.get("/", response_model=List[Event])
async def retrieve_all_events() -> List[Event]:
    events = await event_database.get_all()
    return events


# 특정 ID의 이벤트만 추출하는 라우트에서는 해당 ID의 이벤트가 없으면 HTTP_404_NOT_FOUND 예외를 발생시킨다.
@event_router.get("/{id}", response_model=Event)
async def retrieve_event(id: PydanticObjectId) -> Event:
    event = await event_database.get(id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    return event
    # for event in events:
    #     if event.id == id:
    # return event
    # raise HTTPException(
    #     status_code=status.HTTP_404_NOT_FOUND,
    #     detail="Event with supplied ID does not exist",
    # )


# 이벤트 생성 및 삭제 라우트를 정의한다. 마지막은 전체 이벤트 삭제다.
@event_router.post("/new")
async def create_event(
    body: Event, user: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    body.creator = user  # 새로운 이벤트가 생성될 때 creator 필드가 함께 저장되도록 한다.
    await event_database.save(body)
    # events.append(body)
    return {
        "message": "Event created successfully",
    }


@event_router.delete("/{id}")
async def delete_event(
    id: PydanticObjectId, user: str = Depends(authenticate)
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    event = await event_database.get(id)
    if event.creator != user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not allowed",
        )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    await event_database.delete(id)

    return {
        "message": "Event deleted successfully",
    }

    # for event in events:
    #     if event.id == id:
    #         events.remove(event)
    #         return {
    #             "message": "Event deleted successfully",
    #         }
    # raise HTTPException(
    #     status_code=status.HTTP_404_NOT_FOUND,
    #     detail="Event with supplied ID does not exist",
    # )


events = []


@event_router.delete("/")
async def delete_all_events() -> dict:
    events.clear()
    return {
        "message": "All events deleted successfully",
    }


# 변경(update) 라우트는 실제 데이터베이스와 연동할 때 구현한다.
@event_router.put("/{id}", response_model=Event)
async def update_event(
    id: PydanticObjectId,
    body: EventUpdate,
    user: str = Depends(authenticate),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Event:
    event = await event_database.get(id)
    if event.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )
    updated_event = await event_database.update(id, body)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    return updated_event
