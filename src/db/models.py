from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.db.database import Base

class MeetingModel(Base):
    __tablename__ = "meetings"

    meeting_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    meeting_date = Column(String, nullable=True)
    participants = Column(Text, default="[]")  # JSON string
    total_utterances = Column(Integer, default=0)
    executive_summary = Column(Text, nullable=True)
    processing_time_sec = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    decisions = relationship("DecisionModel", back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("ActionItemModel", back_populates="meeting", cascade="all, delete-orphan")
    issues = relationship("IssueModel", back_populates="meeting", cascade="all, delete-orphan")
    requirements = relationship("RequirementFeedbackModel", back_populates="meeting", cascade="all, delete-orphan")
    unresolved_topics = relationship("UnresolvedTopicModel", back_populates="meeting", cascade="all, delete-orphan")


class DecisionModel(Base):
    __tablename__ = "decisions"

    decision_id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), index=True)
    topic = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, default="CONFIRMED")
    is_final_active = Column(Boolean, default=True, index=True)
    version = Column(Integer, default=1)
    supersedes_decision_id = Column(String, nullable=True)
    superseded_by_decision_id = Column(String, nullable=True)
    confidence = Column(Float, default=0.9)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("MeetingModel", back_populates="decisions")


class ActionItemModel(Base):
    __tablename__ = "action_items"

    action_id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), index=True)
    action_text = Column(Text, nullable=False)
    decontextualized_text = Column(Text, nullable=True)
    assignee_name = Column(String, nullable=True, index=True)
    assignee_role = Column(String, nullable=True)
    deadline_raw = Column(String, nullable=True)
    deadline_iso = Column(String, nullable=True)
    priority = Column(String, default="MEDIUM")
    status = Column(String, default="CONFIRMED")
    derived_from_decision_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("MeetingModel", back_populates="action_items")


class IssueModel(Base):
    __tablename__ = "issues"

    issue_id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, default="MEDIUM")
    status = Column(String, default="OPEN")
    raised_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("MeetingModel", back_populates="issues")


class RequirementFeedbackModel(Base):
    __tablename__ = "requirements_feedbacks"

    item_id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), index=True)
    type = Column(String, default="REQUIREMENT")
    content = Column(Text, nullable=False)
    stakeholder = Column(String, nullable=True)
    target_aspect = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("MeetingModel", back_populates="requirements")


class UnresolvedTopicModel(Base):
    __tablename__ = "unresolved_topics"

    topic_id = Column(String, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.meeting_id"), index=True)
    topic_name = Column(String, nullable=False)
    pending_question = Column(Text, nullable=False)
    conflicting_options = Column(Text, default="[]")  # JSON string
    next_step_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("MeetingModel", back_populates="unresolved_topics")
