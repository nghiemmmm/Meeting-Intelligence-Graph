from typing import List, Dict, Any, Optional
from src.schemas.decision import Decision, DecisionStatus, DecisionEvent, DecisionEventType
from src.schemas.common import Evidence

class TemporalDecisionTracker:
    def __init__(self):
        self.decisions_store: Dict[str, Decision] = {}
        self.event_history: List[DecisionEvent] = []

    def process_event(self, event_data: Dict[str, Any], topic: str) -> Decision:
        """Xử lý sự kiện theo mô hình Event Sourcing và cập nhật vòng đời trạng thái"""
        event_type = DecisionEventType(event_data["event_type"])
        event = DecisionEvent(
            event_id=f"EVT-{len(self.event_history) + 1:03d}",
            event_type=event_type,
            proposal_name=event_data["proposal_name"],
            reason=event_data.get("reason"),
            timestamp=event_data.get("timestamp", "00:00"),
            evidence_utterance_id=event_data.get("evidence_id", "UTT-001")
        )
        self.event_history.append(event)

        dec_id = f"DEC-{len(self.decisions_store) + 1:03d}"
        supersedes_id = None

        # Nếu là quyết định xác nhận (DECISION_CONFIRMED) và có phương án cũ bị thay thế
        if event_type == DecisionEventType.DECISION_CONFIRMED:
            for existing_id, existing_dec in self.decisions_store.items():
                # Chỉ thay thế phương án khác (tránh trường hợp tự thay thế chính mình)
                if (
                    existing_dec.topic == topic
                    and existing_dec.selected_proposal_id != event.proposal_name
                    and existing_dec.status in [DecisionStatus.CONFIRMED, DecisionStatus.UNDER_DISCUSSION]
                ):
                    existing_dec.status = DecisionStatus.SUPERSEDED
                    existing_dec.is_final_active = False
                    existing_dec.superseded_by_decision_id = dec_id
                    supersedes_id = existing_id
                    break

        content_prefix = "Đề xuất phương án" if event_type == DecisionEventType.PROPOSAL_CREATED else "Chốt lựa chọn phương án"
        quote_content = event_data.get("text") or event_data.get("quote") or event_data.get("reason", "")

        new_decision = Decision(
            decision_id=dec_id,
            topic=topic,
            content=f"{content_prefix}: {event.proposal_name}",
            status=DecisionStatus.CONFIRMED if event_type == DecisionEventType.DECISION_CONFIRMED else DecisionStatus.UNDER_DISCUSSION,
            is_final_active=(event_type == DecisionEventType.DECISION_CONFIRMED),
            version=len(self.decisions_store) + 1,
            selected_proposal_id=event.proposal_name,
            supersedes_decision_id=supersedes_id,
            events=[event],
            evidence_list=[Evidence(
                evidence_id=f"EVD-{len(self.event_history):03d}",
                speaker=event_data.get("speaker", "Team Lead"),
                timestamp=event.timestamp,
                quote_text=quote_content
            )]
        )
        self.decisions_store[dec_id] = new_decision
        return new_decision

    def get_all_decisions(self) -> List[Decision]:
        return list(self.decisions_store.values())

    def get_final_decisions(self) -> List[Decision]:
        """Chỉ lấy các quyết định hiện hành có hiệu lực cuối cùng sau cuộc họp"""
        return [d for d in self.decisions_store.values() if d.is_final_active]

    def reset(self):
        """Reset kho lưu trữ quyết định cho phiên xử lý mới"""
        self.decisions_store.clear()
        self.event_history.clear()

decision_tracker = TemporalDecisionTracker()
