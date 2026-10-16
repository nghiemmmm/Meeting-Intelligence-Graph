import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.db.models import (
    MeetingModel, DecisionModel, ActionItemModel,
    IssueModel, RequirementFeedbackModel, UnresolvedTopicModel
)
from src.schemas.meeting import MeetingInput, MeetingProcessResult

class MeetingRepository:
    @staticmethod
    def save_meeting_result(db: Session, meeting_input: MeetingInput, result: MeetingProcessResult):
        """Lưu hoặc cập nhật kết quả xử lý cuộc họp vào cơ sở dữ liệu SQLite"""
        # 1. Kiểm tra và cập nhật/tạo mới MeetingModel
        meeting_db = db.query(MeetingModel).filter(MeetingModel.meeting_id == meeting_input.meeting_id).first()
        if not meeting_db:
            meeting_db = MeetingModel(
                meeting_id=meeting_input.meeting_id,
                title=meeting_input.title,
                meeting_date=meeting_input.meeting_date,
                participants=json.dumps(meeting_input.participants, ensure_ascii=False),
                total_utterances=result.total_utterances,
                executive_summary=result.executive_summary,
                processing_time_sec=result.processing_time_sec
            )
            db.add(meeting_db)
        else:
            meeting_db.title = meeting_input.title
            meeting_db.meeting_date = meeting_input.meeting_date
            meeting_db.participants = json.dumps(meeting_input.participants, ensure_ascii=False)
            meeting_db.total_utterances = result.total_utterances
            meeting_db.executive_summary = result.executive_summary
            meeting_db.processing_time_sec = result.processing_time_sec

        # Xóa các con cũ để cập nhật mới sạch sẽ nếu là cập nhật lại
        db.query(DecisionModel).filter(DecisionModel.meeting_id == meeting_input.meeting_id).delete()
        db.query(ActionItemModel).filter(ActionItemModel.meeting_id == meeting_input.meeting_id).delete()
        db.query(IssueModel).filter(IssueModel.meeting_id == meeting_input.meeting_id).delete()
        db.query(RequirementFeedbackModel).filter(RequirementFeedbackModel.meeting_id == meeting_input.meeting_id).delete()
        db.query(UnresolvedTopicModel).filter(UnresolvedTopicModel.meeting_id == meeting_input.meeting_id).delete()

        # 2. Lưu Decisions
        for d in result.decisions:
            db.query(DecisionModel).filter(DecisionModel.decision_id == d.decision_id).delete()
            d_model = DecisionModel(
                decision_id=d.decision_id,
                meeting_id=meeting_input.meeting_id,
                topic=d.topic,
                content=d.content,
                status=d.status.value,
                is_final_active=d.is_final_active,
                version=d.version,
                supersedes_decision_id=d.supersedes_decision_id,
                superseded_by_decision_id=d.superseded_by_decision_id,
                confidence=d.confidence
            )
            db.add(d_model)

        # 3. Lưu Action Items
        for a in result.action_items:
            db.query(ActionItemModel).filter(ActionItemModel.action_id == a.action_id).delete()
            a_model = ActionItemModel(
                action_id=a.action_id,
                meeting_id=meeting_input.meeting_id,
                action_text=a.action_text,
                decontextualized_text=a.decontextualized_text,
                assignee_name=a.assignee.name if a.assignee else None,
                assignee_role=a.assignee.role if a.assignee else None,
                deadline_raw=a.deadline.raw_text if a.deadline else None,
                deadline_iso=a.deadline.normalized_iso if a.deadline else None,
                priority=a.priority.value,
                status=a.status.value,
                derived_from_decision_id=a.derived_from_decision_id
            )
            db.add(a_model)

        # 4. Lưu Issues
        for iss in result.issues:
            db.query(IssueModel).filter(IssueModel.issue_id == iss.issue_id).delete()
            iss_model = IssueModel(
                issue_id=iss.issue_id,
                meeting_id=meeting_input.meeting_id,
                title=iss.title,
                description=iss.description,
                severity=iss.severity.value,
                status=iss.status.value,
                raised_by=iss.raised_by.name if iss.raised_by else None
            )
            db.add(iss_model)

        # 5. Lưu Requirements / Feedbacks
        for rf in result.requirements_feedbacks:
            db.query(RequirementFeedbackModel).filter(RequirementFeedbackModel.item_id == rf.item_id).delete()
            rf_model = RequirementFeedbackModel(
                item_id=rf.item_id,
                meeting_id=meeting_input.meeting_id,
                type=rf.type.value,
                content=rf.content,
                stakeholder=rf.stakeholder.name if rf.stakeholder else None,
                target_aspect=rf.target_aspect
            )
            db.add(rf_model)

        # 6. Lưu Unresolved Topics
        for un in result.unresolved_topics:
            db.query(UnresolvedTopicModel).filter(UnresolvedTopicModel.topic_id == un.topic_id).delete()
            un_model = UnresolvedTopicModel(
                topic_id=un.topic_id,
                meeting_id=meeting_input.meeting_id,
                topic_name=un.topic_name,
                pending_question=un.pending_question,
                conflicting_options=json.dumps(un.conflicting_options, ensure_ascii=False),
                next_step_action=un.next_step_action
            )
            db.add(un_model)

        db.commit()
        db.refresh(meeting_db)
        return meeting_db

    @staticmethod
    def get_meeting(db: Session, meeting_id: str) -> Optional[MeetingModel]:
        return db.query(MeetingModel).filter(MeetingModel.meeting_id == meeting_id).first()

    @staticmethod
    def list_meetings(db: Session) -> List[MeetingModel]:
        return db.query(MeetingModel).order_by(MeetingModel.created_at.desc()).all()

    @staticmethod
    def list_decisions(db: Session, only_final: bool = False) -> List[DecisionModel]:
        query = db.query(DecisionModel)
        if only_final:
            query = query.filter(DecisionModel.is_final_active == True)
        return query.all()

    @staticmethod
    def list_actions(db: Session) -> List[ActionItemModel]:
        return db.query(ActionItemModel).all()

    @staticmethod
    def list_issues(db: Session) -> List[IssueModel]:
        return db.query(IssueModel).all()

    @staticmethod
    def list_unresolved(db: Session) -> List[UnresolvedTopicModel]:
        return db.query(UnresolvedTopicModel).all()
