from fastapi import APIRouter
from typing import List
from src.schemas.decision import Decision, DecisionEvent
from src.services.tracker_service import decision_tracker

router = APIRouter(prefix="/api/decisions", tags=["Decisions"])

@router.get("", response_model=List[Decision])
def list_decisions():
    """Lấy danh sách tất cả các quyết định cùng trạng thái hiện hành (CONFIRMED, SUPERSEDED)"""
    return decision_tracker.get_all_decisions()

@router.get("/final", response_model=List[Decision])
def get_final_active_decisions():
    """Lấy danh sách các quyết định hiệu lực cuối cùng sau cuộc họp (loại bỏ phương án đã bị SUPERSEDED)"""
    return decision_tracker.get_final_decisions()

@router.get("/timeline", response_model=List[DecisionEvent])
def get_decision_events_timeline():
    """Lấy toàn bộ dòng thời gian các sự kiện quyết định theo chuẩn Event Sourcing"""
    return decision_tracker.event_history
