from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_staff_user
from app.services.customer_arrival_tracker import create_arrival_tracker, ArrivalRecord
from pydantic import BaseModel

router = APIRouter()


class RecordArrivalRequest(BaseModel):
    reservation_id: int
    arrival_time: Optional[datetime] = None


class ArrivalRecordResponse(BaseModel):
    reservation_id: int
    arrival_time: str
    reservation_time: str
    arrival_status: str
    minutes_difference: int
    table_id: int
    customer_name: str
    party_size: int


class ArrivalStatistics(BaseModel):
    total_arrivals: int
    early: int
    on_time: int
    late: int
    very_late: int
    no_show: int
    average_difference_minutes: float


@router.post("/record", response_model=ArrivalRecordResponse)
def record_customer_arrival(
    *,
    db: Session = Depends(get_db),
    request: RecordArrivalRequest,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Record customer arrival at restaurant
    Can be called by customer (self check-in) or staff
    """
    tracker = create_arrival_tracker(db)
    
    try:
        arrival_record = tracker.record_arrival(
            reservation_id=request.reservation_id,
            actual_arrival_time=request.arrival_time
        )
        
        return ArrivalRecordResponse(
            reservation_id=arrival_record.reservation_id,
            arrival_time=arrival_record.arrival_time.isoformat(),
            reservation_time=arrival_record.reservation_time.isoformat(),
            arrival_status=arrival_record.arrival_status,
            minutes_difference=arrival_record.minutes_difference,
            table_id=arrival_record.table_id,
            customer_name=arrival_record.customer_name,
            party_size=arrival_record.party_size
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to record arrival")


@router.post("/check-no-shows", response_model=List[dict])
def check_for_no_shows(
    *,
    db: Session = Depends(get_db),
    threshold_minutes: int = Query(60, description="Minutes past reservation time to mark as no-show"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Check for and mark no-show reservations (Staff+ only)
    """
    tracker = create_arrival_tracker(db)
    no_shows = tracker.check_for_no_shows(threshold_minutes=threshold_minutes)
    
    return [
        {
            "reservation_id": res.id,
            "customer_name": res.customer.full_name if res.customer else "Guest",
            "table_number": res.table.table_number if res.table else "N/A",
            "reservation_time": res.reservation_datetime.isoformat(),
            "party_size": res.party_size
        }
        for res in no_shows
    ]


@router.get("/statistics", response_model=ArrivalStatistics)
def get_arrival_statistics(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get arrival statistics for analysis (Staff+ only)
    """
    tracker = create_arrival_tracker(db)
    stats = tracker.get_arrival_statistics(start_date=start_date, end_date=end_date)
    
    return ArrivalStatistics(**stats)


@router.get("/today", response_model=List[dict])
def get_todays_arrivals(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get today's arrival records (Staff+ only)
    """
    tracker = create_arrival_tracker(db)
    arrivals = tracker.get_todays_arrivals()
    return arrivals


@router.get("/upcoming", response_model=List[dict])
def get_upcoming_arrivals(
    *,
    db: Session = Depends(get_db),
    minutes_ahead: int = Query(30, description="Minutes ahead to look for upcoming arrivals"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get upcoming arrivals for notifications (Staff+ only)
    """
    tracker = create_arrival_tracker(db)
    upcoming = tracker.notify_upcoming_arrivals(minutes_ahead=minutes_ahead)
    
    return [
        {
            "reservation_id": res.id,
            "customer_name": res.customer.full_name if res.customer else "Guest",
            "customer_phone": res.customer.phone if res.customer else None,
            "table_number": res.table.table_number if res.table else "N/A",
            "reservation_time": res.reservation_datetime.isoformat(),
            "party_size": res.party_size,
            "minutes_until_arrival": int(
                (res.reservation_datetime - datetime.utcnow()).total_seconds() / 60
            )
        }
        for res in upcoming
    ]