# 이벤트 생성, 변경, 삭제 등의 처리를 위한 라우팅
from beanie import PydanticObjectId
from models.users import Host, Client
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
from auth.authenticate import authenticate_host, authenticate_client

service_router = APIRouter(
    tags=["Service"],
)
booking_router = APIRouter(
    tags=["Booking"],
)

service_database = Database(Service)
booking_database = Database(Booking)


@service_router.get("/", response_model=List[Service])
async def get_all_services() -> List[Service]:
    """1번\n
    생성 목적: 모든 서비스를 추출한다.
    \n
    지도 상에서 모든 서비스를 보여주기 위해 사용된다.
    """
    services = await service_database.get_all()
    return services


@service_router.get("/host", response_model=List[Service])
async def get_all_services_by_host(
    current_user: Host = Depends(authenticate_host),
) -> List[Service]:
    """
    생성 목적: 호스트 자신이 만든 모든 서비스를 가져온다.

    호스트 admin 페이지에서 호스트 인증된 사용자에게 자신이 만든 서비스를 보여주기 위해 사용된다.
    """

    all_services = await Service.all().to_list()
    services_by_host = [
        service for service in all_services if service.creator == current_user.email
    ]  # service(expression) for item in iterable if condition

    return services_by_host


# @service_router.get("/host/{host_id}", response_model=List[Service])
# async def get_all_services_by_host(
#     host_id: PydanticObjectId,
#     current_user: Host = Depends(authenticate_host),
# ) -> List[Service]:
#     """2번\n
#     생성 목적: 호스트 자신이 만든 모든 서비스를 가져온다.
#     \n
#     호스트 admin 페이지에서 호스트 인증된 사용자에게 자신이 만든 서비스를 보여주기 위해 사용된다.
#     """
#     if current_user.id != host_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to get services",
#         )

#     all_services = await Service.all()
#     services_by_host = [
#         service for service in all_services if service.creator == current_user.email
#     ]  # service(expression) for item in iterable if condition

#     return services_by_host


@service_router.get("/{service_id}", response_model=Service)
async def get_service(service_id: PydanticObjectId) -> Service:
    """3번\n
    생성 목적: 특정 ID의 서비스를 추출한다.
    """
    service = await service_database.get(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="service with supplied ID does not exist",
        )
    return service


@service_router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: PydanticObjectId,
    body: ServiceUpdate,
    current_user: Host = Depends(authenticate_host),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Service:
    """4번\n
    생성 목적: 호스트가 자신의 서비스를 업데이트한다.
    \n
    호스트가 admin 페이지에서 자신의 서비스에 들어온 예약의 확정을 하기 위해 사용된다.
    """
    service = await service_database.get(service_id)

    if service is None:  # 서비스가 존재하지 않으면 예외를 발생시킨다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with the given service_id not found",
        )

    if service.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )

    updated_service = await service_database.update(service_id, body)

    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Service update has been made",
        )
    return updated_service


@service_router.delete("/{service_id}")
async def delete_service(
    service_id: PydanticObjectId,
    current_user: Host = Depends(authenticate_host),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
):
    """5번\n
    생성 목적: 호스트가 자신의 서비스를 삭제한다.
    \n
    호스트 admin 페이지에서 호스트가 자신의 서비스를 삭제하기 위해 사용된다.
    """
    service = await service_database.get(service_id)

    if not service:  # 서비스가 존재하는지 먼저 확인한다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )

    if service.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service deletion not allowed",
        )
    # 서비스를 삭제한다.
    await service_database.delete(service_id)

    return {
        "message": "Service deleted successfully",
    }


"""
------------------------------------------------------------------------------------------
"""


@service_router.get("/host/{service_id}", response_model=Service)
async def get_service_by_id(
    service_id: PydanticObjectId,
    current_user: Host = Depends(authenticate_host),
) -> Service:
    """6번\n
    생성 목적: 호스트 자신이 만든 특정 ID의 서비스를 추출한다.
    \n
    호스트 admin 페이지에서 호스트 인증된 사용자에게 자신이 만든 특정 서비스를 보여주기 위해 사용된다.
    """
    # 호스트가 자신의 서비스 중에서 service_id에 해당하는 서비스를 가져옵니다.
    service = await Service.get(
        service_id,
        creator=current_user.email,
    )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )
    return service


@service_router.get("/{service_id}/bookings", response_model=List[Booking])
async def get_bookings_for_service(
    service_id: PydanticObjectId, current_user: Host = Depends(authenticate_host)
) -> List[Booking]:
    """7번\n
    생성 목적: 호스트가 자신의 서비스에 들어온 모든 예약을 추출한다.
    """
    service = await service_database.get(service_id)  # 하나의 서비스 id로부터 서비스 정보를 가져온다.
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )

    if current_user.email != service.creator:  # 서비스를 생성한 Host만 예약을 추출할 수 있다.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get bookings from this service",
        )

    bookings = []  # 예약을 저장할 리스트를 생성한다.

    for booking_id in service.bookings:
        booking = await booking_database.get(booking_id)

        if not booking:
            continue  # 예약이 존재하지 않으면 건너뛴다.

        bookings.append(booking)

    return bookings


@service_router.post("/new")
async def create_service(
    body: Service,
    current_user: Host = Depends(authenticate_host),
) -> dict:  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
    """8번\n
    생성 목적: 호스트가 새로운 자신의 서비스를 생성한다.
    \n
    호스트 admin 페이지에서 호스트 인증된 사용자에게 자신의 서비스를 생성하기 위해 사용된다.
    """
    body.creator = (
        current_user.email
    )  # Host 객체의 특정 필드를 creator 필드에 할당한다.# 새로운 이벤트가 생성될 때 creator 필드가 함께 저장되도록 한다.

    result = await service_database.save(body)  # 새로운 서비스를 "먼저" 데이터베이스에 result로 저장한다.

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the service",
        )

    return {
        "message": "Service created successfully",
        "service": result.dict(),  # 생성된 서비스를 반환한다.
    }


# @service_router.delete("/delete-all")
# async def delete_all_services():
#     """9번\n
#     생성 목적: 테스트를 위해 모든 서비스를 삭제한다.
#     \n
#     """
#     await service_database.delete_all()
#     return {
#         "message": "All Services deleted successfully",
#     }


"""
==========================================================================================
"""


@booking_router.get("/", response_model=List[Booking])
async def get_all_bookings() -> List[Booking]:
    """1번\n
    생성 목적: 모든 예약을 추출한다.
    """
    bookings = await booking_database.get_all()
    return bookings


@booking_router.get("/client", response_model=List[Booking])
async def get_all_bookings_by_client(
    current_user: Client = Depends(authenticate_client),
) -> List[Booking]:
    """
    생성 목적: 클라이언트 자신이 예약한 모든 예약을 가져온다.

    클라이언트 admin 페이지에서 클라이언트 인증된 사용자에게 자신이 예약한 모든 예약을 보여주기 위해 사용된다.
    """

    all_bookings = await Booking.all().to_list()
    bookings_by_client = [
        booking for booking in all_bookings if booking.creator == current_user.email
    ]  # booking(expression) for item in iterable if condition

    # Fetch the service details for each booking
    for booking in bookings_by_client:
        service = await Service.get(booking.service)
        if service:
            # Add the service details to the booking info
            booking.service_info = {
                "address": service.address,
                "service_name": service.service_name,
                "category": service.category,
            }

    return bookings_by_client


# @booking_router.get("/client/{client_id}", response_model=List[Booking])
# async def get_user_bookings(
#     client_id: PydanticObjectId,
#     current_user: Client = Depends(authenticate_client),
# ):
#     """2번\n
#     생성 목적: 클라이언트 자신의 예약을 추출한다.
#     \n
#     """
#     if current_user.id != client_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to get bookings",
#         )

#     all_bookings = await Booking.all()

#     bookings_by_client = [
#         booking for booking in all_bookings if booking.creator == current_user.email
#     ]  # booking(expression) for item in iterable if condition

#     return bookings_by_client


@booking_router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: PydanticObjectId) -> Booking:
    """3번\n
    생성 목적: 특정 ID의 예약을 추출한다.
    \n

    """
    booking = await booking_database.get(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )
    return booking


@booking_router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: PydanticObjectId,
    body: BookingUpdate,
    current_user: Client = Depends(
        authenticate_client
    ),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
) -> Booking:
    """4번\n
    생성 목적: 클라이언트가 자신의 예약을 업데이트한다.
    """

    # 예약 정보를 가져온다.
    booking = await booking_database.get(booking_id)

    if booking is None:  # 예약이 존재하지 않으면 예외를 발생시킨다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with the given booking_id not found",
        )

    if booking.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )

    # 연관된 서비스 정보를 가져옵니다.
    service = await service_database.get(booking.service)

    # 해당 서비스가 없다면 에러를 발생시킵니다.
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist.",
        )

    # 가방 수의 차이를 계산합니다.
    bag_difference = body.booking_bag - booking.booking_bag

    # 예약 업데이트로 인해 이용 가능한 가방 수 초과 시 에러 메세지 반환
    if bag_difference > 0 and bag_difference > service.available_bag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The update exceeds available bags in the service.",
        )

    # 가방 수 차이에 따라 서비스에서 이용 가능한 가방 수 업데이트
    service.available_bag -= bag_difference

    # 수정된 서비스 레코드 저장
    await service_database.update(service.id, service)

    updated_booking = await booking_database.update(booking_id, body)

    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The booking was not updated.",
        )

    return {
        "message": "Booking has been successfully updated",
        "updated_booking": updated_booking.dict(),
        "service_available_bag": {"available_bag": service.available_bag},
    }


@booking_router.delete("/{booking_id}")
async def delete_booking_bag(
    booking_id: PydanticObjectId,
    current_user: Client = Depends(authenticate_client),
):
    """5번\n
    생성 목적: 클라이언트가 자신의 예약을 삭제함(취소 역할).
    \n

    """
    # 예약 정보를 가져온다.
    booking = await booking_database.get(booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )

    if booking.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking deletion not allowed",
        )

    # 서비스의 가용한 가방 수를 다시 증가시킨다.
    service = await service_database.get(booking.service)

    service.available_bag += booking.booking_bag

    # save(생성) 대신 update(수정)를 사용하여 서비스의 가용한 가방 수를 증가시킨다.
    await service_database.update(service.id, service)

    # 예약을 취소한다.
    await booking_database.delete(booking_id)

    return {
        "message": "Booking deleted successfully",
        "service_available_bag": service.available_bag,
    }


"""
------------------------------------------------------------------------------------------
"""


@booking_router.get("/client/{booking_id}", response_model=Booking)
async def get_booking_by_id(
    booking_id: PydanticObjectId,
    current_user: Client = Depends(authenticate_client),
) -> Booking:
    """6번\n
    생성 목적: 클라이언트 자신의 예약을 id로 추출한다.
    \n

    """
    booking = await Booking.get(
        booking_id,
        creator=current_user.email,
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )
    return booking


@booking_router.get("/{booking_id}/service", response_model=Service)
async def get_service_for_booking(
    booking_id: PydanticObjectId,
    current_user: Client = Depends(authenticate_client),
) -> Service:
    """7번\n
    생성 목적: 클라이언트가 자신의 예약에 대한 서비스를 추출한다.
    """

    booking = await booking_database.get(booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking with supplied ID does not exist",
        )

    if current_user.email != booking.creator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get service from this booking",
        )

    service = await service_database.get(booking.service)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service within booking with supplied ID does not exist",
        )

    return service


"""
=========================================================================================
"""


@booking_router.post("/new")  # , response_model=Booking)
async def create_booking(
    body: Booking,
    current_user: Client = Depends(
        authenticate_client
    ),  # authenticate_client 를 통해 인증된 클라이언트 정보가 current_user 변수에 저장된다.
):
    """8번\n
    생성 목적: 클라이언트가 자신의 예약을 생성한다.
    \n

    """
    body.creator = current_user.email  # 새로운 예약이 생성될 때 creator 필드가 함께 저장되도록 한다.

    # 클라이언트가 예약을 생성할 때, 해당 서비스의 ID(service 필드)로부터 서비스 정보를 가져온다.
    service = await service_database.get(body.service)  # 해당 서비스의 ID로부터 서비스 정보를 가져온다.

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )

    # 예약 가능한 가방 수를 초과하는 예약을 거부한다.
    if body.booking_bag > service.available_bag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exceeds the available bags for this service",
        )

    # 예약을 데이터베이스에 저장한다.
    result = await booking_database.save(body)

    # 서비스의 가용한 가방 수를 감소시킨다.
    service.available_bag -= body.booking_bag

    # if not service.bookings:
    #     service.bookings = []

    # 새로 만든 booking 의 id 를 services 의 bookings 에 추가한다.
    service.bookings.append(result.id)

    # save(생성) 대신 update(수정)를 사용하여 서비스의 가용한 가방 수를 감소시킨다.
    result_service = await service_database.update(service.id, service)
    # print(
    #     type(result_service)
    # )  # result_service의 실제 타입이 딕셔너리인지, Pydantic 모델인지 확인한다. <class 'models.reservations.Service'> 이므로 Pydantic 모델이다.

    return {
        "message": "Booking created successfully",
        # **result.dict(),  # Booking 객체의 각 필드를 직접적으로 결과 딕셔너리의 키로 설정한다.
        "booking": result.dict(),  # dict()는 객체가 Pydantic 모델이거나, Pydantic 모델을 상속받는 클래스의 인스턴스일 때, 해당 객체를 딕셔너리로 변환한다.
        "service_available_bag": result_service.dict(
            include={"available_bag"}
        ),  # result_service["available_bag"], result_service.dict()["available_bag"] 둘 다 가능하다.
    }


@booking_router.put("/{booking_id}/status", response_model=Booking)
async def update_booking_status(
    booking_id: PydanticObjectId,
    body: BookingConfirmUpdate,
    current_user: Host = Depends(authenticate_host),
) -> Booking:
    booking = await booking_database.get(booking_id)

    if booking.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed",
        )

    # 연관된 서비스 정보를 가져온다.
    service = await service_database.get(booking.service)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service with supplied ID does not exist",
        )

    # 예약 상태가 현재 대기 중이고 취소로 수정되는 경우, 이용 가능한 가방 수를 늘린다.
    if booking.confirm == "pending" and body.confirm == "cancelled":
        service.available_bag += booking.booking_bag

    # 수정된 서비스 레코드를 저장한다.
    await service_database.update(service.id, service)

    # 요청 본문에서 받은 값으로 예약 상태를 설정한다.
    booking.confirm = body.confirm

    updated_booking = await booking_database.update(booking_id, body)

    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The booking status was not updated.",
        )

    return {
        "message": f"Booking status updated to {body.confirm}",
        "updated_booking": updated_booking.dict(),
        "service_available_bag": {"available_bag": service.available_bag},
    }


# @booking_router.put("/{booking_id}/confirm", response_model=Booking)
# async def update_booking_confirm(
#     booking_id: PydanticObjectId,
#     body: BookingConfirmUpdate,
#     current_user: Host = Depends(authenticate_host),  # 의존성 주입을 사용하여 사용자가 로그인했는지 확인한다.
# ) -> Booking:
#     """9번\n
#     생성 목적: 호스트가 자신이 생성한 서비스에 예약이 들어온 것을 확정한다.
#     \n

#     """
#     booking = await booking_database.get(booking_id)

#     if booking.creator != current_user.email:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Booking update not allowed",
#         )

#     updated_booking = await booking_database.update(booking_id, body)

#     if not updated_booking:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No Booking update has been made",
#         )
#     return updated_booking


# @booking_router.delete("/delete-all")
# async def delete_all_bookings():
#     """10번\n
#     생성 목적: 테스트를 위해 모든 예약를 삭제한다.
#     \n
#     """
#     await booking_database.delete_all()
#     return {
#         "message": "All bookings deleted successfully",
#     }
