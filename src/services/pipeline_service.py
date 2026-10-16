import time
from typing import List, Dict, Any
from src.schemas.meeting import MeetingInput, MeetingProcessResult
from src.schemas.action import ActionItem, ActionStatus, ActionPriority
from src.schemas.decision import Decision, DecisionStatus
from src.schemas.insight import IssueItem, IssueSeverity, IssueStatus, RequirementFeedbackItem, FeedbackType, UnresolvedTopic
from src.schemas.common import Evidence, Person, DeadlineInfo
from src.services.llm_service import llm_service
from src.services.tracker_service import decision_tracker
from src.services.graph_service import meeting_graph_service

class MeetingProcessingPipeline:
    def process_meeting(self, meeting: MeetingInput, reset_previous: bool = True) -> MeetingProcessResult:
        start_time = time.time()
        
        if reset_previous:
            decision_tracker.reset()
            meeting_graph_service.graph.clear()

        # 1. Khởi tạo Node Meeting và Participants trong Graph
        meeting_graph_service.add_node(meeting.meeting_id, "Meeting", {
            "title": meeting.title,
            "date": meeting.meeting_date or "2026-10-14"
        })

        for p_name in meeting.participants:
            p_id = f"USR-{p_name.upper().replace(' ', '_')}"
            meeting_graph_service.add_node(p_id, "Participant", {"name": p_name})
            meeting_graph_service.add_edge(p_id, meeting.meeting_id, "ATTENDED")

        # 2. Chuẩn bị nội dung transcript
        full_text = "\n".join([f"[{u.timestamp}] {u.speaker_name}: {u.text}" for u in meeting.transcript])
        
        context_state = {
            "meeting_id": meeting.meeting_id,
            "title": meeting.title,
            "participants": meeting.participants,
            "total_turns": len(meeting.transcript)
        }

        # 3. Trích xuất qua LLM / Heuristic Parser
        extracted_data = llm_service.extract_chunk_structured(full_text, context_state)

        # 4. Xử lý các sự kiện quyết định qua Temporal Tracker & Nạp vào Graph
        created_decisions: List[Decision] = []
        events_to_process = list(extracted_data.get("events", []))
        if not events_to_process and extracted_data.get("decisions"):
            for d in extracted_data["decisions"]:
                events_to_process.append({
                    "event_type": "DECISION_CONFIRMED",
                    "proposal_name": d.get("content", d.get("topic", "Quyết định")),
                    "reason": d.get("content", ""),
                    "speaker": d.get("speaker", "Team Lead"),
                    "timestamp": d.get("timestamp", "00:00"),
                    "text": d.get("quote", d.get("content", ""))
                })
        for ev in events_to_process:
            decision = decision_tracker.process_event(ev, topic=meeting.title)
            created_decisions.append(decision)
            
            # Thêm Node Decision vào Graph
            meeting_graph_service.add_node(decision.decision_id, "Decision", {
                "content": decision.content,
                "status": decision.status.value,
                "is_final_active": decision.is_final_active,
                "version": decision.version
            })
            meeting_graph_service.add_edge(decision.decision_id, meeting.meeting_id, "DECIDED_IN")

            # Nếu có quyết định cũ bị SUPERSEDES -> Tạo cạnh đồ thị SUPERSEDES
            if decision.supersedes_decision_id:
                meeting_graph_service.add_edge(decision.decision_id, decision.supersedes_decision_id, "SUPERSEDES")

            # Lưu Node Evidence cho Decision
            for ev_item in decision.evidence_list:
                meeting_graph_service.add_node(ev_item.evidence_id, "Evidence", {
                    "quote_text": ev_item.quote_text,
                    "timestamp": ev_item.timestamp,
                    "speaker": ev_item.speaker
                })
                meeting_graph_service.add_edge(decision.decision_id, ev_item.evidence_id, "SUPPORTED_BY")

        # 5. Xử lý Vướng mắc / Vấn đề (Issues)
        created_issues: List[IssueItem] = []
        for idx, iss in enumerate(extracted_data.get("issues", []), start=1):
            iss_id = f"ISS-{idx:03d}"
            ev_id = f"EV-ISS-{idx}"
            evidence = Evidence(
                evidence_id=ev_id,
                speaker=iss.get("speaker", "Participant"),
                timestamp=iss.get("timestamp", "00:00"),
                quote_text=iss.get("quote", iss.get("description", ""))
            )
            issue_item = IssueItem(
                issue_id=iss_id,
                title=iss.get("title", "Vướng mắc kỹ thuật"),
                description=iss.get("description", ""),
                severity=IssueSeverity(iss.get("severity", "MEDIUM")),
                status=IssueStatus(iss.get("status", "OPEN")),
                raised_by=Person(name=iss.get("speaker")) if iss.get("speaker") else None,
                evidence_list=[evidence]
            )
            created_issues.append(issue_item)

            # Nạp Node Issue vào Graph
            meeting_graph_service.add_node(iss_id, "Issue", {
                "title": issue_item.title,
                "severity": issue_item.severity.value,
                "status": issue_item.status.value,
                "description": issue_item.description
            })
            meeting_graph_service.add_edge(iss_id, meeting.meeting_id, "DISCUSSED_IN")

            # Liên kết SUPPORTED_BY với Evidence
            meeting_graph_service.add_node(ev_id, "Evidence", {
                "quote_text": evidence.quote_text,
                "timestamp": evidence.timestamp,
                "speaker": evidence.speaker
            })
            meeting_graph_service.add_edge(iss_id, ev_id, "SUPPORTED_BY")

            # Nếu có Decision tương ứng, nối MOTIVATED_BY (Quyết định được thúc đẩy bởi vấn đề này)
            if created_decisions:
                meeting_graph_service.add_edge(created_decisions[-1].decision_id, iss_id, "MOTIVATED_BY")

        # 6. Xử lý Yêu cầu / Phản hồi (Requirements & Feedbacks)
        created_reqs: List[RequirementFeedbackItem] = []
        for idx, rf in enumerate(extracted_data.get("requirements_feedbacks", []), start=1):
            rf_id = f"RF-{idx:03d}"
            ev_id = f"EV-RF-{idx}"
            evidence = Evidence(
                evidence_id=ev_id,
                speaker=rf.get("stakeholder", "Stakeholder"),
                timestamp=rf.get("timestamp", "00:00"),
                quote_text=rf.get("quote", rf.get("content", ""))
            )
            rf_item = RequirementFeedbackItem(
                item_id=rf_id,
                type=FeedbackType(rf.get("type", "REQUIREMENT")),
                content=rf.get("content", ""),
                stakeholder=Person(name=rf.get("stakeholder")) if rf.get("stakeholder") else None,
                target_aspect=rf.get("target_aspect", "Hệ thống"),
                evidence_list=[evidence]
            )
            created_reqs.append(rf_item)

            meeting_graph_service.add_node(rf_id, rf_item.type.value, {
                "content": rf_item.content,
                "target_aspect": rf_item.target_aspect
            })
            meeting_graph_service.add_edge(rf_id, meeting.meeting_id, "SUBMITTED_IN")

            meeting_graph_service.add_node(ev_id, "Evidence", {
                "quote_text": evidence.quote_text,
                "timestamp": evidence.timestamp,
                "speaker": evidence.speaker
            })
            meeting_graph_service.add_edge(rf_id, ev_id, "SUPPORTED_BY")

        # 7. Xử lý Nội dung chưa được chốt (Unresolved Topics)
        created_unresolved: List[UnresolvedTopic] = []
        for idx, un in enumerate(extracted_data.get("unresolved_topics", []), start=1):
            un_id = f"UNR-{idx:03d}"
            ev_id = f"EV-UNR-{idx}"
            evidence = Evidence(
                evidence_id=ev_id,
                speaker="Nhóm họp",
                timestamp=un.get("timestamp", "00:00"),
                quote_text=un.get("quote", un.get("pending_question", ""))
            )
            un_item = UnresolvedTopic(
                topic_id=un_id,
                topic_name=un.get("topic_name", "Nội dung mở"),
                pending_question=un.get("pending_question", ""),
                conflicting_options=un.get("conflicting_options", []),
                next_step_action=un.get("next_step_action"),
                evidence_list=[evidence]
            )
            created_unresolved.append(un_item)

            meeting_graph_service.add_node(un_id, "UnresolvedTopic", {
                "topic_name": un_item.topic_name,
                "pending_question": un_item.pending_question
            })
            meeting_graph_service.add_edge(un_id, meeting.meeting_id, "LEFT_OPEN_IN")

            meeting_graph_service.add_node(ev_id, "Evidence", {
                "quote_text": evidence.quote_text,
                "timestamp": evidence.timestamp,
                "speaker": evidence.speaker
            })
            meeting_graph_service.add_edge(un_id, ev_id, "SUPPORTED_BY")

        # 8. Xử lý Action Items & Nạp vào Graph
        created_actions: List[ActionItem] = []
        for idx, act in enumerate(extracted_data.get("actions", []), start=1):
            act_id = f"ACT-{idx:03d}"
            # Null-Safety: Chỉ khởi tạo khi có tên hoặc raw_text cụ thể
            assignee = Person(name=act["assignee"]["name"], role=act["assignee"].get("role")) if (act.get("assignee") and act["assignee"].get("name")) else None
            deadline = DeadlineInfo(raw_text=act["deadline"]["raw_text"]) if (act.get("deadline") and act["deadline"].get("raw_text")) else None

            # Tìm decision đang active cuối cùng để liên kết
            active_dec = next((d for d in reversed(created_decisions) if d.is_final_active), None)

            action_item = ActionItem(
                action_id=act_id,
                action_text=act["action_text"],
                decontextualized_text=act.get("decontextualized_text"),
                assignee=assignee,
                deadline=deadline,
                priority=ActionPriority(act.get("priority", "MEDIUM")),
                status=ActionStatus.CONFIRMED,
                evidence_list=[Evidence(
                    evidence_id=f"EV-ACT-{idx}",
                    speaker=act.get("speaker") or (assignee.name if assignee else "Speaker"),
                    timestamp=act.get("timestamp", "00:00"),
                    quote_text=act.get("quote", act["action_text"])
                )],
                derived_from_decision_id=active_dec.decision_id if active_dec else None
            )
            created_actions.append(action_item)

            # Nạp Node ActionItem vào Graph
            meeting_graph_service.add_node(act_id, "ActionItem", {
                "action_text": action_item.action_text,
                "status": action_item.status.value,
                "deadline": deadline.raw_text if deadline else "Chưa xác định"
            })

            # Liên kết IMPLEMENTS với Active Decision
            if active_dec:
                meeting_graph_service.add_edge(act_id, active_dec.decision_id, "IMPLEMENTS")

            # Liên kết ASSIGNED_TO với Participant
            if assignee:
                p_id = f"USR-{assignee.name.upper().replace(' ', '_')}"
                if p_id not in meeting_graph_service.graph:
                    meeting_graph_service.add_node(p_id, "Participant", {"name": assignee.name})
                meeting_graph_service.add_edge(act_id, p_id, "ASSIGNED_TO")

            # Liên kết SUPPORTED_BY với Evidence
            for ev_act in action_item.evidence_list:
                meeting_graph_service.add_node(ev_act.evidence_id, "Evidence", {
                    "quote_text": ev_act.quote_text,
                    "timestamp": ev_act.timestamp,
                    "speaker": ev_act.speaker
                })
                meeting_graph_service.add_edge(act_id, ev_act.evidence_id, "SUPPORTED_BY")

        duration = round(time.time() - start_time, 2)
        
        return MeetingProcessResult(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            total_utterances=len(meeting.transcript),
            topics=[meeting.title],
            decisions=created_decisions,
            action_items=created_actions,
            issues=created_issues,
            requirements_feedbacks=created_reqs,
            unresolved_topics=created_unresolved,
            executive_summary=extracted_data.get("executive_summary"),
            graph_stats=meeting_graph_service.get_stats(),
            processing_time_sec=duration
        )

pipeline_service = MeetingProcessingPipeline()
