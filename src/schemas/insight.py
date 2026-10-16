from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from src.schemas.common import Evidence, Person

class IssueSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IssueStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    ACCEPTED_RISK = "ACCEPTED_RISK"

class IssueItem(BaseModel):
    """Vướng mắc, vấn đề hoặc rủi ro xuất hiện trong cuộc họp"""
    issue_id: str = Field(description="Mã định danh vấn đề (ví dụ: ISS-001)")
    title: str = Field(description="Tiêu đề tóm tắt vấn đề/vướng mắc")
    description: str = Field(description="Chi tiết mô tả vướng mắc")
    severity: IssueSeverity = Field(default=IssueSeverity.MEDIUM, description="Mức độ nghiêm trọng")
    status: IssueStatus = Field(default=IssueStatus.OPEN, description="Trạng thái xử lý")
    raised_by: Optional[Person] = Field(default=None, description="Người nêu vấn đề")
    evidence_list: List[Evidence] = Field(default_factory=list, description="Bằng chứng từ transcript")

class FeedbackType(str, Enum):
    REQUIREMENT = "REQUIREMENT"
    FEEDBACK = "FEEDBACK"

class RequirementFeedbackItem(BaseModel):
    """Yêu cầu từ các bên liên quan hoặc phản hồi chất lượng/tính năng"""
    item_id: str = Field(description="Mã định danh (ví dụ: REQ-001 hoặc FDB-001)")
    type: FeedbackType = Field(description="Loại: Yêu cầu mới (REQUIREMENT) hay Phản hồi (FEEDBACK)")
    content: str = Field(description="Nội dung chi tiết của yêu cầu hoặc phản hồi")
    stakeholder: Optional[Person] = Field(default=None, description="Người đưa ra yêu cầu/phản hồi")
    target_aspect: Optional[str] = Field(default=None, description="Khía cạnh áp dụng (UI, Backend, Hiệu năng, Bảo mật)")
    evidence_list: List[Evidence] = Field(default_factory=list, description="Bằng chứng từ transcript")

class UnresolvedTopic(BaseModel):
    """Nội dung thảo luận chưa được chốt hạ sau cuộc họp"""
    topic_id: str = Field(description="Mã định danh nội dung chưa chốt (ví dụ: UNR-001)")
    topic_name: str = Field(description="Chủ đề đang thảo luận dang dở")
    pending_question: str = Field(description="Câu hỏi hoặc vấn đề cốt lõi chưa có sự thống nhất")
    conflicting_options: List[str] = Field(default_factory=list, description="Các phương án đang tranh luận bất đồng")
    next_step_action: Optional[str] = Field(default=None, description="Hướng giải quyết đề xuất cho cuộc họp sau")
    evidence_list: List[Evidence] = Field(default_factory=list, description="Bằng chứng từ transcript")
