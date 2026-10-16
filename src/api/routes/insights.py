from fastapi import APIRouter
from typing import List
from src.schemas.insight import IssueItem, RequirementFeedbackItem, UnresolvedTopic
from src.api.routes.meetings import processed_meetings_db

router = APIRouter(prefix="/api/insights", tags=["Insights & Unresolved Topics"])

@router.get("/issues", response_model=List[IssueItem])
def list_meeting_issues():
    """Lấy danh sách các vấn đề / vướng mắc / rủi ro kỹ thuật từ các cuộc họp"""
    issues = []
    for m in processed_meetings_db.values():
        issues.extend(m.issues)
    return issues

@router.get("/requirements-feedbacks", response_model=List[RequirementFeedbackItem])
def list_requirements_feedbacks():
    """Lấy danh sách các yêu cầu của bên liên quan và phản hồi sản phẩm"""
    rf_list = []
    for m in processed_meetings_db.values():
        rf_list.extend(m.requirements_feedbacks)
    return rf_list

@router.get("/unresolved", response_model=List[UnresolvedTopic])
def list_unresolved_topics():
    """Lấy danh sách các vấn đề chưa được chốt hạ, cần thảo luận ở cuộc họp tiếp theo"""
    unresolved = []
    for m in processed_meetings_db.values():
        unresolved.extend(m.unresolved_topics)
    return unresolved
