from pydantic import BaseModel, Field
from typing import Optional

class Evidence(BaseModel):
    evidence_id: str = Field(description="Định danh bằng chứng")
    utterance_id: Optional[str] = Field(default=None, description="ID của lượt phát ngôn gốc (ví dụ: UTT-001)")
    speaker: str = Field(description="Tên người phát ngôn")
    speaker_role: Optional[str] = Field(default=None, description="Vai trò của người nói (Host, Lead, Dev)")
    timestamp: str = Field(description="Mốc thời gian phát ngôn (ví dụ: 10:32:05 hoặc 00:09:18)")
    quote_text: str = Field(description="Trích dẫn câu phát ngôn gốc nguyên văn")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Độ tin cậy trích xuất")

class Person(BaseModel):
    person_id: Optional[str] = None
    name: str
    role: Optional[str] = None

class DeadlineInfo(BaseModel):
    raw_text: str = Field(description="Cụm từ chỉ thời gian nguyên văn trong lời nói (ví dụ: 'trước thứ Sáu')")
    normalized_iso: Optional[str] = Field(default=None, description="Thời gian đã chuẩn hóa ISO-8601 nếu đã tính toán được")
    resolution_status: str = Field(default="NEEDS_DATE_RESOLUTION", description="Trạng thái phân giải ngày tháng")
