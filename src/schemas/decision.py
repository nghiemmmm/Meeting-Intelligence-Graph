from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from src.schemas.common import Evidence

class DecisionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    UNDER_DISCUSSION = "UNDER_DISCUSSION"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    COMPLETED = "COMPLETED"

class DecisionEventType(str, Enum):
    PROPOSAL_CREATED = "PROPOSAL_CREATED"
    OBJECTION_RAISED = "OBJECTION_RAISED"
    PROPOSAL_REFINED = "PROPOSAL_REFINED"
    DECISION_CONFIRMED = "DECISION_CONFIRMED"
    DECISION_SUPERSEDED = "DECISION_SUPERSEDED"

class DecisionEvent(BaseModel):
    event_id: str
    event_type: DecisionEventType
    proposal_name: str
    reason: Optional[str] = None
    target_proposal_id: Optional[str] = None
    timestamp: str
    evidence_utterance_id: str

class Decision(BaseModel):
    decision_id: str = Field(description="Mã định danh quyết định (ví dụ: DEC-001)")
    topic: str = Field(description="Chủ đề liên quan")
    content: str = Field(description="Nội dung quyết định chính thức")
    status: DecisionStatus = Field(default=DecisionStatus.CONFIRMED)
    is_final_active: bool = Field(default=True, description="Đánh dấu đây có phải là quyết định hiệu lực cuối cùng sau cuộc họp hay không")
    version: int = Field(default=1, description="Phiên bản quyết định")
    
    selected_proposal_id: Optional[str] = None
    supersedes_decision_id: Optional[str] = Field(default=None, description="ID của quyết định cũ bị thay thế")
    superseded_by_decision_id: Optional[str] = Field(default=None, description="ID của quyết định mới thay thế quyết định này")
    
    events: List[DecisionEvent] = Field(default_factory=list, description="Chuỗi sự kiện dẫn đến quyết định (Event Sourcing)")
    evidence_list: List[Evidence] = Field(default_factory=list, description="Danh sách bằng chứng hỗ trợ quyết định")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
