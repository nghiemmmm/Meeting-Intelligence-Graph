from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict
import typing_extensions as typing

STRICT_CONFIG = ConfigDict(extra="forbid")

class EntityCluster(BaseModel):
    model_config = STRICT_CONFIG
    canonical: str = Field(description="Tên định danh chuẩn, đầy đủ, trang trọng và rõ ràng nhất của thực thể")
    aliases: List[str] = Field(description="Danh sách tất cả các biến thể tên gọi/cách xưng hô xuất hiện trong các cuộc họp trỏ đến thực thể này")
    entity_type: Literal["PERSON", "SYSTEM_TECH", "DECISION_TOPIC", "ISSUE"] = Field(description="Loại thực thể được gom cụm")
    reasoning: str = Field(description="Giải thích ngắn gọn căn cứ ngữ cảnh (dựa trên descriptions) để gom các biến thể này lại với nhau")

class ResolvedClusters(BaseModel):
    model_config = STRICT_CONFIG
    clusters: List[EntityCluster] = Field(default_factory=list, description="Danh sách các cụm thực thể đã được chuẩn hóa")

# TypedDict hỗ trợ trực tiếp Google Gemini response_schema
class EntityClusterTypedDict(typing.TypedDict):
    canonical: str
    aliases: List[str]
    entity_type: str
    reasoning: str

class ResolvedClustersTypedDict(typing.TypedDict):
    clusters: List[EntityClusterTypedDict]

# --- Giai đoạn 3: Entity Profiling & Summarization Schemas ---
class TimeRange(BaseModel):
    model_config = STRICT_CONFIG
    start: str = Field(description="Định dạng YYYY hoặc YYYY-MM hoặc 'unknown'")
    end: str = Field(description="Định dạng YYYY hoặc YYYY-MM hoặc 'ongoing'")

class EntityProfile(BaseModel):
    model_config = STRICT_CONFIG
    summary: str = Field(description="Tóm tắt chi tiết từ 2-3 đoạn văn tổng hợp từ các trích đoạn văn bản")
    key_facts: List[str] = Field(description="3-5 sự kiện cốt lõi, có thể tra cứu ngược lại nguồn")
    time_range: TimeRange = Field(description="Khoảng thời gian hoạt động/tồn tại")

class TimeRangeTypedDict(typing.TypedDict):
    start: str
    end: str

class EntityProfileTypedDict(typing.TypedDict):
    summary: str
    key_facts: List[str]
    time_range: TimeRangeTypedDict

