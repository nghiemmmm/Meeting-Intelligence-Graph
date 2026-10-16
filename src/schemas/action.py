from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from src.schemas.common import Evidence, Person, DeadlineInfo

class ActionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    SUPERSEDED = "SUPERSEDED"

class ActionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ActionItem(BaseModel):
    action_id: str = Field(description="Mã định danh công việc (ví dụ: ACT-001)")
    action_text: str = Field(description="Mô tả hành động cần thực hiện")
    decontextualized_text: Optional[str] = Field(default=None, description="Câu văn đã được viết lại hoàn chỉnh theo kỹ thuật DUR")
    
    assignee: Optional[Person] = Field(default=None, description="Người chịu trách nhiệm thực thi (Nullable chống ảo giác)")
    assigner: Optional[Person] = Field(default=None, description="Người giao việc / điều phối")
    object_target: Optional[str] = Field(default=None, description="Đối tượng của hành động (báo cáo, repository, database)")
    
    deadline: Optional[DeadlineInfo] = Field(default=None, description="Thời hạn hoàn thành")
    priority: ActionPriority = Field(default=ActionPriority.MEDIUM, description="Mức độ ưu tiên")
    completion_criteria: List[str] = Field(default_factory=list, description="Tiêu chuẩn hoàn thành hoặc điều kiện nghiệm thu")
    
    status: ActionStatus = Field(default=ActionStatus.CONFIRMED, description="Trạng thái của nhiệm vụ")
    evidence_list: List[Evidence] = Field(default_factory=list, description="Danh sách các bằng chứng đối chiếu trong transcript")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Độ tin cậy trích xuất")
    
    derived_from_decision_id: Optional[str] = Field(default=None, description="ID của quyết định sinh ra nhiệm vụ này")
