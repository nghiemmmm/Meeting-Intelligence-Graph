from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

# Cấu hình chung cho mọi model để tuân thủ 100% OpenAI Structured Outputs
STRICT_CONFIG = ConfigDict(extra="forbid")

class AssigneeInfo(BaseModel):
    model_config = STRICT_CONFIG
    name: Optional[str] = Field(default=None, description="Tên người nhận việc nếu được chỉ định cụ thể, null nếu chưa rõ")
    role: Optional[str] = Field(default=None, description="Vai trò hoặc chức danh của người nhận việc")

class DeadlineExtract(BaseModel):
    model_config = STRICT_CONFIG
    raw_text: Optional[str] = Field(default=None, description="Cụm từ chỉ thời gian nguyên văn (ví dụ: 'trước thứ Sáu', 'ngày mai') hoặc null")
    normalized_iso: Optional[str] = Field(default=None, description="Thời gian chuẩn hóa ISO nếu phân giải được")

class ActionItemExtract(BaseModel):
    model_config = STRICT_CONFIG
    action_text: str = Field(description="Câu phát ngôn gốc chứa hành động")
    decontextualized_text: str = Field(description="Câu hành động tự thân hoàn chỉnh (DUR) đã khôi phục đầy đủ chủ vị tân ngữ")
    assignee: Optional[AssigneeInfo] = Field(default=None, description="Thông tin người nhận việc (áp dụng Null-Safety)")
    deadline: Optional[DeadlineExtract] = Field(default=None, description="Thông tin hạn chót (áp dụng Null-Safety)")
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(default="MEDIUM", description="Độ ưu tiên")
    description: Optional[str] = Field(default=None, description="Mô tả 1 câu tóm tắt ngữ cảnh thực thể để phục vụ Entity Disambiguation và Cross-meeting Resolution")
    speaker: str = Field(description="Người phát ngôn giao hoặc nhận việc")
    timestamp: str = Field(description="Mốc thời gian phát ngôn (ví dụ: '09:20')")
    quote: str = Field(description="Trích dẫn câu phát ngôn nguyên văn")

class DecisionEventExtract(BaseModel):
    model_config = STRICT_CONFIG
    topic: str = Field(description="Chủ đề hoặc phân hệ của quyết định")
    content: str = Field(description="Nội dung quyết định được thống nhất")
    description: Optional[str] = Field(default=None, description="Mô tả 1 câu tóm tắt ngữ cảnh quyết định để phục vụ Entity Disambiguation và Cross-meeting Resolution")
    status: Literal["CONFIRMED", "PROPOSED", "SUPERSEDED"] = Field(default="CONFIRMED", description="Trạng thái quyết định")
    supersedes: Optional[str] = Field(default=None, description="Tên phương án/đề xuất cũ bị thay thế nếu có (Temporal Shift), null nếu không thay thế")
    speaker: str = Field(description="Người chốt hoặc công bố quyết định")
    timestamp: str = Field(description="Mốc thời gian chốt quyết định")
    quote: str = Field(description="Trích dẫn nguyên văn câu chốt quyết định")

class IssueExtract(BaseModel):
    model_config = STRICT_CONFIG
    title: str = Field(description="Tiêu đề vướng mắc / khó khăn kỹ thuật / rủi ro")
    description: str = Field(description="Mô tả chi tiết nội dung vướng mắc")
    severity: Literal["LOW", "MEDIUM", "HIGH"] = Field(default="MEDIUM", description="Mức độ nghiêm trọng của vấn đề")
    status: Literal["OPEN", "RESOLVED"] = Field(default="OPEN", description="Trạng thái hiện tại của vướng mắc")
    speaker: str = Field(description="Người nêu lên vấn đề")
    timestamp: str = Field(description="Mốc thời gian phát biểu")
    quote: str = Field(description="Trích dẫn nguyên văn phản biện / lo ngại")

class RequirementFeedbackExtract(BaseModel):
    model_config = STRICT_CONFIG
    type: Literal["REQUIREMENT", "FEEDBACK"] = Field(description="Yêu cầu bắt buộc hoặc phản hồi đóng góp")
    content: str = Field(description="Nội dung chi tiết của yêu cầu hoặc phản hồi")
    stakeholder: str = Field(description="Khách hàng, đối tác hoặc bên liên quan đưa ra")
    target_aspect: str = Field(description="Khía cạnh hoặc tính năng bị tác động")
    timestamp: str = Field(description="Mốc thời gian phát ngôn")
    quote: str = Field(description="Trích dẫn nguyên văn")

class UnresolvedTopicExtract(BaseModel):
    model_config = STRICT_CONFIG
    topic_name: str = Field(description="Tên chủ đề chưa đạt được đồng thuận")
    pending_question: str = Field(description="Câu hỏi mở hoặc khúc mắc cần thảo luận thêm")
    conflicting_options: List[str] = Field(default_factory=list, description="Các phương án đang gây tranh luận hoặc thăm dò")
    next_step_action: str = Field(description="Kế hoạch tiếp theo (ví dụ: khảo sát thêm, hoãn sang cuộc họp sau)")
    timestamp: str = Field(description="Mốc thời gian thảo luận")
    quote: str = Field(description="Trích dẫn nguyên văn")

class DiscussionEventExtract(BaseModel):
    model_config = STRICT_CONFIG
    event_type: Literal["PROPOSAL_CREATED", "OBJECTION_RAISED", "DECISION_CONFIRMED"] = Field(description="Loại sự kiện hội thoại")
    proposal_name: str = Field(description="Tên phương án hoặc giải pháp liên quan")
    reason: str = Field(description="Lý do đề xuất, phản biện hoặc chốt quyết định")
    speaker: str = Field(description="Người phát ngôn")
    timestamp: str = Field(description="Mốc thời gian")
    text: str = Field(description="Nội dung phát ngôn")

class MeetingStructuredExtraction(BaseModel):
    """
    Schema gốc (Root Object) đại diện cho toàn bộ dữ liệu bóc tách được từ một phân đoạn hoặc phiên họp.
    Tuân thủ 100% ràng buộc của OpenAI Structured Outputs (extra='forbid').
    """
    model_config = STRICT_CONFIG
    executive_summary: str = Field(description="Tóm tắt ngắn gọn 1-2 câu về nội dung cuộc họp")
    events: List[DiscussionEventExtract] = Field(default_factory=list, description="Danh sách các sự kiện đề xuất, phản biện, chốt hạ")
    decisions: List[DecisionEventExtract] = Field(default_factory=list, description="Danh sách quyết định chính thức (kèm supersedes nếu có)")
    actions: List[ActionItemExtract] = Field(default_factory=list, description="Danh sách nhiệm vụ giao việc (kèm DUR và Null-Safety)")
    issues: List[IssueExtract] = Field(default_factory=list, description="Danh sách vướng mắc, khó khăn kỹ thuật, rủi ro")
    requirements_feedbacks: List[RequirementFeedbackExtract] = Field(default_factory=list, description="Yêu cầu từ khách hàng hoặc feedback")
    unresolved_topics: List[UnresolvedTopicExtract] = Field(default_factory=list, description="Nội dung tranh luận chưa chốt")

# TypedDict tương đương hỗ trợ trực tiếp Google Gemini response_schema
import typing_extensions as typing

class AssigneeTypedDict(typing.TypedDict):
    name: Optional[str]
    role: Optional[str]

class DeadlineTypedDict(typing.TypedDict):
    raw_text: Optional[str]
    normalized_iso: Optional[str]

class ActionTypedDict(typing.TypedDict):
    action_text: str
    decontextualized_text: str
    assignee: Optional[AssigneeTypedDict]
    deadline: Optional[DeadlineTypedDict]
    priority: str
    description: Optional[str]
    speaker: str
    timestamp: str
    quote: str

class DecisionTypedDict(typing.TypedDict):
    topic: str
    content: str
    description: Optional[str]
    status: str
    supersedes: Optional[str]
    speaker: str
    timestamp: str
    quote: str

class IssueTypedDict(typing.TypedDict):
    title: str
    description: str
    severity: str
    status: str
    speaker: str
    timestamp: str
    quote: str

class RequirementTypedDict(typing.TypedDict):
    type: str
    content: str
    stakeholder: str
    target_aspect: str
    timestamp: str
    quote: str

class UnresolvedTypedDict(typing.TypedDict):
    topic_name: str
    pending_question: str
    conflicting_options: List[str]
    next_step_action: str
    timestamp: str
    quote: str

class EventTypedDict(typing.TypedDict):
    event_type: str
    proposal_name: str
    reason: str
    speaker: str
    timestamp: str
    text: str

class MeetingExtractionTypedDict(typing.TypedDict):
    executive_summary: str
    events: List[EventTypedDict]
    decisions: List[DecisionTypedDict]
    actions: List[ActionTypedDict]
    issues: List[IssueTypedDict]
    requirements_feedbacks: List[RequirementTypedDict]
    unresolved_topics: List[UnresolvedTypedDict]

