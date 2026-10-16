from pydantic import BaseModel, Field
from typing import List, Optional
from src.schemas.action import ActionItem
from src.schemas.decision import Decision
from src.schemas.insight import IssueItem, RequirementFeedbackItem, UnresolvedTopic

class Utterance(BaseModel):
    utterance_id: str
    speaker_id: Optional[str] = None
    speaker_name: str
    speaker_role: Optional[str] = None
    timestamp: str
    text: str

import uuid

class MeetingInput(BaseModel):
    meeting_id: Optional[str] = Field(
        default_factory=lambda: f"MTG-{uuid.uuid4().hex[:8].upper()}",
        description="Mã cuộc họp (tự sinh nếu không truyền)"
    )
    title: str
    meeting_date: Optional[str] = Field(default=None, description="Ngày họp định dạng YYYY-MM-DD")
    participants: List[str] = Field(default_factory=list)
    transcript: List[Utterance] = Field(description="Danh sách các lượt phát ngôn theo thứ tự thời gian")

class TopicChunk(BaseModel):
    chunk_id: str
    topic_name: str
    start_time: str
    end_time: str
    utterances: List[Utterance]
    local_summary: Optional[str] = None

class MeetingProcessResult(BaseModel):
    meeting_id: str
    title: str
    total_utterances: int
    topics: List[str] = Field(default_factory=list)
    
    # 5 Nhóm dữ liệu cấu trúc cốt lõi của Mission 2
    decisions: List[Decision] = Field(default_factory=list, description="Quyết định (kèm theo dõi SUPERSEDES)")
    action_items: List[ActionItem] = Field(default_factory=list, description="Công việc cần làm (kèm assignee, deadline)")
    issues: List[IssueItem] = Field(default_factory=list, description="Vướng mắc / vấn đề / phản biện")
    requirements_feedbacks: List[RequirementFeedbackItem] = Field(default_factory=list, description="Yêu cầu hoặc phản hồi")
    unresolved_topics: List[UnresolvedTopic] = Field(default_factory=list, description="Nội dung thảo luận chưa được chốt")
    
    # Thông tin tóm tắt & đồ thị tri thức
    executive_summary: Optional[str] = Field(default=None, description="Bản tóm tắt điều hành ngắn gọn")
    graph_stats: dict = Field(default_factory=dict)
    processing_time_sec: float = Field(default=0.0)
