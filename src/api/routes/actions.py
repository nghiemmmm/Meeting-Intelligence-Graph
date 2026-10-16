from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from src.schemas.action import ActionItem
from src.services.graph_service import meeting_graph_service
from src.api.routes.meetings import processed_meetings_db

router = APIRouter(prefix="/api/actions", tags=["Actions"])

@router.get("", response_model=List[ActionItem])
def list_action_items():
    """Lấy toàn bộ danh sách Action Items đã được trích xuất từ tất cả cuộc họp"""
    all_actions = []
    for m in processed_meetings_db.values():
        all_actions.extend(m.action_items)
    return all_actions

@router.get("/{action_id}/causal-chain")
def get_action_causal_chain(action_id: str) -> Dict[str, Any]:
    """
    Truy vết chuỗi nhân quả của một Action Item qua Graph Traversal:
    - Nhiệm vụ này sinh ra từ Quyết định nào?
    - Ai là người phản biện dẫn đến quyết định đó?
    - Bằng chứng trích dẫn nằm ở phút thứ mấy trong transcript?
    """
    chain = meeting_graph_service.find_causal_chain_for_action(action_id)
    if "error" in chain:
        raise HTTPException(status_code=404, detail=chain["error"])
    return chain
