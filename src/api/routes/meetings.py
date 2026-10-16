import json
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.schemas.meeting import MeetingInput, MeetingProcessResult
from src.services.pipeline_service import pipeline_service
from src.db.database import get_db
from src.db.repository import MeetingRepository

router = APIRouter(prefix="/api/meetings", tags=["Meetings"])

# Lưu trữ cache bộ nhớ tạm thời cho các cuộc họp đã xử lý
processed_meetings_db: Dict[str, MeetingProcessResult] = {}

@router.post("/process", response_model=MeetingProcessResult)
def process_meeting_transcript(meeting_input: MeetingInput, db: Session = Depends(get_db)):
    """
    Xử lý bản ghi transcript cuộc họp qua toàn bộ Pipeline:
    - Context-aware Chunking & DUR Intent Extraction
    - Temporal Decision Tracking (SUPERSEDES)
    - Meeting Knowledge Graph Construction (NetworkX & Neo4j AuraDB)
    - Lưu trữ bền vững vào cơ sở dữ liệu SQLite (data/meetings.db)
    """
    try:
        result = pipeline_service.process_meeting(meeting_input)
        processed_meetings_db[meeting_input.meeting_id] = result
        
        # Lưu vào SQLite Database
        MeetingRepository.save_meeting_result(db, meeting_input, result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý cuộc họp: {str(e)}")

@router.get("", response_model=List[Dict[str, Any]])
def list_all_meetings(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả các cuộc họp đã lưu trong SQLite Database"""
    meetings = MeetingRepository.list_meetings(db)
    return [
        {
            "meeting_id": m.meeting_id,
            "title": m.title,
            "meeting_date": m.meeting_date,
            "participants": json.loads(m.participants) if m.participants else [],
            "total_utterances": m.total_utterances,
            "executive_summary": m.executive_summary,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in meetings
    ]

@router.get("/{meeting_id}", response_model=MeetingProcessResult)
def get_meeting_result(meeting_id: str, db: Session = Depends(get_db)):
    """Lấy thông tin và dữ liệu có cấu trúc của cuộc họp (từ Cache hoặc SQLite)"""
    if meeting_id in processed_meetings_db:
        return processed_meetings_db[meeting_id]
    
    # Nếu chưa có trong cache, truy vấn từ SQLite
    m_db = MeetingRepository.get_meeting(db, meeting_id)
    if not m_db:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc họp này trong hệ thống")
    
    # Tạo đối tượng MeetingProcessResult từ DB
    from src.schemas.decision import Decision, DecisionStatus
    from src.schemas.action import ActionItem, ActionStatus, ActionPriority
    from src.schemas.insight import IssueItem, IssueSeverity, IssueStatus, RequirementFeedbackItem, FeedbackType, UnresolvedTopic
    from src.schemas.common import Person, DeadlineInfo
    from src.services.graph_service import meeting_graph_service

    decisions = [
        Decision(
            decision_id=d.decision_id,
            topic=d.topic,
            content=d.content,
            status=DecisionStatus(d.status),
            is_final_active=d.is_final_active,
            version=d.version,
            supersedes_decision_id=d.supersedes_decision_id,
            superseded_by_decision_id=d.superseded_by_decision_id,
            confidence=d.confidence
        )
        for d in m_db.decisions
    ]

    action_items = [
        ActionItem(
            action_id=a.action_id,
            action_text=a.action_text,
            decontextualized_text=a.decontextualized_text,
            assignee=Person(name=a.assignee_name, role=a.assignee_role) if a.assignee_name else None,
            deadline=DeadlineInfo(raw_text=a.deadline_raw, normalized_iso=a.deadline_iso) if a.deadline_raw else None,
            priority=ActionPriority(a.priority),
            status=ActionStatus(a.status),
            derived_from_decision_id=a.derived_from_decision_id
        )
        for a in m_db.action_items
    ]

    issues = [
        IssueItem(
            issue_id=i.issue_id,
            title=i.title,
            description=i.description,
            severity=IssueSeverity(i.severity),
            status=IssueStatus(i.status),
            raised_by=Person(name=i.raised_by) if i.raised_by else None
        )
        for i in m_db.issues
    ]

    reqs = [
        RequirementFeedbackItem(
            item_id=r.item_id,
            type=FeedbackType(r.type),
            content=r.content,
            stakeholder=Person(name=r.stakeholder) if r.stakeholder else None,
            target_aspect=r.target_aspect
        )
        for r in m_db.requirements
    ]

    unresolved = [
        UnresolvedTopic(
            topic_id=u.topic_id,
            topic_name=u.topic_name,
            pending_question=u.pending_question,
            conflicting_options=json.loads(u.conflicting_options) if u.conflicting_options else [],
            next_step_action=u.next_step_action
        )
        for u in m_db.unresolved_topics
    ]

    res = MeetingProcessResult(
        meeting_id=m_db.meeting_id,
        title=m_db.title,
        total_utterances=m_db.total_utterances,
        topics=[m_db.title],
        decisions=decisions,
        action_items=action_items,
        issues=issues,
        requirements_feedbacks=reqs,
        unresolved_topics=unresolved,
        executive_summary=m_db.executive_summary,
        graph_stats=meeting_graph_service.get_stats(),
        processing_time_sec=m_db.processing_time_sec
    )
    processed_meetings_db[meeting_id] = res
    return res
