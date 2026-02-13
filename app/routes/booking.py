from datetime import date, datetime, timedelta
import math
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Form, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from streamlit import status
from app.auth.auth_utils import require_scope
from app.crud.booking import generate_booking_invoice, send_email_with_pdf
from app.models.Enum import BookingStatusEnum, PaymentStatusEnum, RefundStatusEnum, RoomStatusEnum
from app.models.reschedule import Reschedules
from app.models.rooms import Rooms
from app.models.bookings import Bookings
from app.models.booking_status_history import BookingStatusHistory
from app.models.room_type import RoomTypeWithSizes
from app.models.payment import Payments
from app.models.refund import Refunds
from app.models.addon import Addons
from app.models.booking_addon import BookingAddons
from app.schemas.payment_schema import PaymentBase
from app.schemas.status_history_schema import BookingStatusHistoryBase
from app.schemas.booking_schema import BookingBase, BookingResponse
from app.core.dependency import get_db
from app.crud.generic_crud import filter_record, get_records, insert_record, get_record, get_record_by_id, insert_record_flush, commit_db, search, update_record
from app.crud.rooms import available_rooms, available_date_of_room, check_availability

router = APIRouter(prefix="/booking", tags=["Bookings"])

@router.post("/add", response_model=dict)
@require_scope(["booking:read"])
async def book_room(
    background_tasks: BackgroundTasks,
    request: Request,
    booking: BookingBase,
    addon_list: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Book a new room record"""
    try:
        room_instance = await get_record_by_id(db=db, model=Rooms, id=booking.room_id)
        if not room_instance:
            raise HTTPException(status_code=404, detail="Room not found")

        root_type_instance = await get_record_by_id(db=db, model=RoomTypeWithSizes, id=room_instance.room_type_id)
        if not root_type_instance:
            raise HTTPException(status_code=404, detail="Room type not found")
        
        if booking.check_in < datetime.now().date():
            raise HTTPException(status_code=404, detail="Choose future date")

        available = check_availability(
            db=db, model=Bookings, check_in=booking.check_in, check_out=booking.check_out, room_id=booking.room_id
        )

        if not available:
            raise HTTPException(status_code=400, detail="The requested room is not available for this date")

        from_date = booking.check_in
        to_date = booking.check_out
        no_of_days = (to_date - from_date).days
        room_amount = no_of_days * root_type_instance.base_price

        booking_instance = await insert_record_flush(
            db=db, model=Bookings, **booking.model_dump(), total_amount=room_amount, user_id=request.state.user.id
        )

        addon_amount = 0
        if addon_list and addon_list != ["string"]:
            for addon in addon_list:
                try:
                    addon_id, quantity = addon.split(':')
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid addon format: {addon}")

                instance = await get_record_by_id(db=db, model=Addons, id=addon_id)
                if not instance:
                    raise HTTPException(status_code=404, detail=f"Addon with ID {addon_id} not found")

                addon_amount += (instance.base_price * int(quantity))

                dicts = {
                    "booking_id": booking_instance.id,
                    "addon_id": addon_id,
                    "quantity": quantity
                }
                await insert_record(db=db, model=BookingAddons, **dicts)
      
        total_amount = room_amount + addon_amount
        payment_data_base = PaymentBase(
            booking_id=booking_instance.id,
            total_amount=total_amount,
            status=PaymentStatusEnum.PAID.value
        )
        booking_instance.total_amount = total_amount
        
        await insert_record(db=db, model=Payments, **payment_data_base.model_dump())
        await commit_db(db)
        result = await get_record_by_id(db=db, model=Bookings, id=booking_instance.id)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to fetch booking after creation")

        booking_data = BookingResponse.model_validate(result)

        pdf_path = await generate_booking_invoice(db=db, booking_instance=result)
        subject = "Booking Invoice"
        message = "Please find your booking invoice attached."
        await send_email_with_pdf(
            background_tasks=background_tasks,
            to_email=result.user.email,
            subject=subject,
            message=message,
            pdf_path=pdf_path
        )
        
        return {
            "message": "Booking created successfully",
            "booking": booking_data.model_dump(),
            "total_amount": total_amount,
            "invoice_sent": True
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/cancel")
@require_scope(["booking:read"])
async def cancel_booking(
    request: Request,
    booking_id: int = Form(...),
    reason: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        existing_booking = db.query(Bookings).filter(Bookings.id == booking_id).first()
        if not existing_booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if existing_booking.booking_status != BookingStatusEnum.CONFIRMED.value:
            raise HTTPException(status_code=400, detail="Only confirmed bookings can be cancelled")

        total_amount = existing_booking.total_amount
        no_days = (existing_booking.check_in - date.today()).days

        refund_amount = 0
        message = ""

        if no_days < 3:
            refund_amount = total_amount * 0.8
            message = f"Refund of {refund_amount} will be processed in 2 days."
        elif 3 <= no_days <= 6:
            refund_amount = total_amount * 0.5
            message = f"Refund of {refund_amount} will be processed in 2 days."
        elif no_days >= 7:
            refund_amount = total_amount
            message = f"Full refund of {refund_amount} will be processed in 2 days."

        existing_booking.booking_status = BookingStatusEnum.CANCELLED.value

        payment = await get_record(db=db, model=Payments, booking_id=booking_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment record not found")

        payment.status = PaymentStatusEnum.REFUNDED.value

        refund_data = {
            "payment_id": payment.id,
            "status": RefundStatusEnum.APPROVED.value,
            "reason": reason,
            "total_amount": total_amount,
            "refund_amount": refund_amount
        }
        refunded_data = await insert_record(db=db, model=Refunds, **refund_data)

        status_history = BookingStatusHistoryBase(
            booking_id=booking_id,
            old_status=BookingStatusEnum.CONFIRMED.value,
            new_status=BookingStatusEnum.CANCELLED.value
        )
        await insert_record(db=db, model=BookingStatusHistory, **status_history.model_dump())

        await commit_db(db)

        booking_data = BookingResponse.model_validate(existing_booking)

        return {
            "booking": booking_data.model_dump(),
            "refund_status": refunded_data.status,
            "total_amount": refunded_data.total_amount,
            "refund_amount": refunded_data.refund_amount,
            "message": message
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/checkAvailability")
@require_scope(["booking:read"])
async def availabile_date_of_room(
    request: Request,
    room_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        available_dates = await available_date_of_room(room_id=room_id, db=db, model=Bookings)
        if not available_dates:
            raise HTTPException(status_code=404, detail="No availability data found")
        return available_dates
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/reschedule")
@require_scope(["booking:read"])
async def reschdule_bookings(
    request: Request,
    booking_id: int = Form(...),
    check_in: date = Form(...),
    check_out: date = Form(...),
    db: Session = Depends(get_db)
):
    try:
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Invalid date range")

        booking_instance = await get_record(id=booking_id, db=db, model=Bookings)
        if not booking_instance:
            raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")

        if booking_instance.booking_status != BookingStatusEnum.CONFIRMED:
            raise HTTPException(status_code=400, detail="Cannot reschedule this booking")

        cutoff_days = 3
        
        if date.today() > booking_instance.check_in - timedelta(days=cutoff_days):
            raise HTTPException(status_code=400, detail="Too late to reschedule this booking")

        already_rescheduled = db.query(Reschedules).filter(
            Reschedules.booking_id == booking_id
        ).first()
        if already_rescheduled:
            raise HTTPException(
                status_code=400, 
                detail="This booking has already been rescheduled once"
            )

        available = check_availability(
            db=db, 
            model=Bookings, 
            check_in=check_in, 
            check_out=check_out, 
            room_id=booking_instance.room_id
        )

        if available:
            paid_amount = booking_instance.total_amount
            
            no_of_days = (check_out - check_in).days
            new_total_amount = no_of_days * booking_instance.room.room_type.base_price
            
            payment = await get_record(db=db, model=Payments, booking_id=booking_instance.id)
            
            if not payment:
                raise HTTPException(status_code=404, detail="Payment record not found")
            
            booking_instance.check_in = check_in
            booking_instance.check_out = check_out
            booking_instance.total_amount = new_total_amount
            
            if paid_amount < new_total_amount:
                amount_to_be_paid = new_total_amount - paid_amount
                
                additional_payment_data = PaymentBase(
                    booking_id=booking_instance.id,
                    total_amount=amount_to_be_paid,
                    status=PaymentStatusEnum.PAID.value
                )
                
                await insert_record(
                    db=db, 
                    model=Payments, 
                    **additional_payment_data.model_dump()
                )
                
            elif paid_amount > new_total_amount:
                
                amount_to_be_refunded = paid_amount - new_total_amount
                
                amount_refunded = amount_to_be_refunded * 0.8
                deduction_amount = amount_to_be_refunded * 0.2
                
                refund_payment_data = PaymentBase(
                    booking_id=booking_instance.id,
                    total_amount=amount_to_be_refunded,  
                    status=PaymentStatusEnum.REFUNDED.value  
                )
                
                refund_payment = await insert_record(
                    db=db, 
                    model=Payments, 
                    **refund_payment_data.model_dump()
                )
                refund_data = {
                    "payment_id": refund_payment.id,
                    "status": RefundStatusEnum.APPROVED.value,
                    "total_amount": amount_to_be_refunded,
                    "refund_amount": amount_refunded,
                    "reason": "rescheduled"
                }

                await insert_record(db=db, model=Refunds, **refund_data)
            
            reschedule_record = await insert_record(
                db=db, 
                model=Reschedules, 
                booking_id=booking_id
            )
            
            await commit_db(db)
            
            booking_data = BookingResponse.model_validate(booking_instance)
            
            return {
                "message": "Booking rescheduled successfully",
                "booking": booking_data.model_dump(),
                "new_total_amount": new_total_amount,
                "paid_amount": paid_amount,
                "payment_difference": new_total_amount - paid_amount,
                "reschedule_id": reschedule_record.get("id") if isinstance(reschedule_record, dict) else reschedule_record.id
            }
        
        else:
            room_instance = await get_record_by_id(
                db=db, 
                model=Rooms, 
                id=booking_instance.room_id
            )
            room_type_instance = await get_record_by_id(
                db=db, 
                model=RoomTypeWithSizes, 
                id=room_instance.room_type_id
            )
            
            alternative_rooms = available_rooms(
                db=db, 
                check_in=check_in, 
                check_out=check_out,
                no_of_adult=room_type_instance.no_of_adult,
                no_of_child=room_type_instance.no_of_child
            )
            
            return {
                "message": "Selected room not available for these dates",
                "available_rooms": alternative_rooms
            }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/search", response_model=dict)
@require_scope(["booking:read"])
def search_bookings(
    request: Request,
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search bookings with pagination and fallback to fuzzy search"""
    try:
        results = search(db=db, model=Bookings, q=q, page=page, per_page=per_page)

        if not isinstance(results, list):
            raise HTTPException(status_code=500, detail="Invalid search result format")

        total = len(results)
        total_pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page

        paginated_results = results[offset: offset + per_page]

        bookings_data = [
            BookingResponse.model_validate(booking).model_dump()
            for booking in paginated_results
        ]

        return {
            "success": True,
            "items": bookings_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/filter", response_model=dict)
@require_scope(["booking:read"])
async def filter_bookings(
    request: Request,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    booking_status: Optional[str] = Query(None, description=f"Filter by booking status"),
    payment_status: Optional[str] = Query(None, description=f"Filter by payment status"),
    check_in_from: Optional[date] = Query(None, description="Filter bookings with check-in on or after this date"),
    check_in_to: Optional[date] = Query(None, description="Filter bookings with check-in on or before this date"),
    check_out_from: Optional[date] = Query(None, description="Filter bookings with check-out on or after this date"),
    check_out_to: Optional[date] = Query(None, description="Filter bookings with check-out on or before this date"),
    min_total_amount: Optional[int] = Query(None, description="Minimum total booking amount"),
    max_total_amount: Optional[int] = Query(None, description="Maximum total booking amount"),
    created_from: Optional[datetime] = Query(None, description="Filter from creation datetime"),
    created_to: Optional[datetime] = Query(None, description="Filter to creation datetime"),
    page: int = Query(1, gt=0, description="Page number"),
    per_page: int = Query(10, gt=0, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Filter bookings with pagination"""
    try:
        dicts = {}
        valid_booking_statuses = [e.value for e in BookingStatusEnum]
        valid_payment_statuses = [e.value for e in PaymentStatusEnum]

        if booking_status and booking_status not in valid_booking_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid booking_status. Must be one of {valid_booking_statuses}."
            )
        if payment_status and payment_status not in valid_payment_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_status. Must be one of {valid_payment_statuses}."
            )

        if user_id is not None:
            dicts["user_id"] = ["==", user_id]
        if room_id is not None:
            dicts["room_id"] = ["==", room_id]
        if booking_status:
            dicts["booking_status"] = ["==", booking_status]
        if payment_status:
            dicts["payment_status"] = ["==", payment_status]
        if check_in_from:
            dicts["check_in"] = [">=", check_in_from]
        if check_in_to:
            dicts["check_in"] = ["<=", check_in_to]
        if check_out_from:
            dicts["check_out"] = [">=", check_out_from]
        if check_out_to:
            dicts["check_out"] = ["<=", check_out_to]
        if min_total_amount is not None:
            dicts["total_amount"] = [">=", min_total_amount]
        if max_total_amount is not None:
            dicts["total_amount"] = ["<=", max_total_amount]
        if created_from:
            dicts["created_at"] = [">=", created_from]
        if created_to:
            dicts["created_at"] = ["<=", created_to]

        if not dicts:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least one filter parameter."
            )

        result = await filter_record(db=db, model=Bookings, **dicts)
        
        if isinstance(result, dict) and "items" in result:
            booking_list = result["items"]
            total = result.get("total", len(booking_list))
        elif isinstance(result, list):
            booking_list = result
            total = len(booking_list)
        else:
            booking_list = []
            total = 0
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = booking_list[start:end]
        
        bookings_data = [
            BookingResponse.model_validate(booking).model_dump() 
            for booking in paginated_items
        ]
        
        return {
            "items": bookings_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
        }
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/list", response_model=dict)
@require_scope(["booking:read"])
async def list_bookings(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """List all bookings with pagination"""
    try:
        instances = await get_records(model=Bookings, db=db)
        
        if isinstance(instances, dict) and "items" in instances:
            booking_list = instances["items"]
        elif isinstance(instances, list):
            booking_list = instances
        else:
            booking_list = []
        
        total = len(booking_list)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = booking_list[start:end]
        bookings_data = [
            BookingResponse.model_validate(booking).model_dump() 
            for booking in paginated_items
        ]
        
        return {
            "items": bookings_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
        }
            
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")