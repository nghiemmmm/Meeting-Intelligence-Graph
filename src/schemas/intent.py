from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class IntentType(str, Enum):
    # Công việc
    CREATE_TASK = "CREATE_TASK"
    UPDATE_TASK = "UPDATE_TASK"
    ASSIGN_TASK = "ASSIGN_TASK"
    
    # Đề xuất
    PROPOSE_OPTION = "PROPOSE_OPTION"
    REQUEST_CHANGE = "REQUEST_CHANGE"
    
    # Lập luận
    SUPPORT_PROPOSAL = "SUPPORT_PROPOSAL"
    OPPOSE_PROPOSAL = "OPPOSE_PROPOSAL"
    
    # Quyết định
    CONFIRM_DECISION = "CONFIRM_DECISION"
    REJECT_PROPOSAL = "REJECT_PROPOSAL"
    SUPERSEDE_DECISION = "SUPERSEDE_DECISION"
    
    # Cam kết
    ACCEPT_RESPONSIBILITY = "ACCEPT_RESPONSIBILITY"
    SET_DEADLINE = "SET_DEADLINE"
    
    # Tra cứu
    REQUEST_INFORMATION = "REQUEST_INFORMATION"
    REFERENCE_RESOURCE = "REFERENCE_RESOURCE"
    
    # Thảo luận & Ngoài lề
    DISCUSS_TOPIC = "DISCUSS_TOPIC"
    CHITCHAT = "CHITCHAT"

class IntentScope(str, Enum):
    HEAD_INTENT = "HEAD_INTENT"
    SUPPLEMENTAL_INTENT = "SUPPLEMENTAL_INTENT"

class IntentClassification(BaseModel):
    name: IntentType = Field(description="Loại Intent được nhận diện")
    scope: IntentScope = Field(default=IntentScope.HEAD_INTENT, description="Ý định chính hay ý định bổ sung")
    confidence: float = Field(ge=0.0, le=1.0, description="Độ tin cậy so khớp Intent")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Các tham số trích xuất thô")
