import os
import sys
import json
from starlette.testclient import TestClient

# Cấu hình UTF-8 console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from src.schemas.graph import MultiHopQueryResponse, ClaimVerificationResponse

def test_phase4():
    client = TestClient(app)

    print("=" * 80)
    print("KIỂM THỬ GIAI ĐOẠN 4: MULTI-HOP QUERYING & MULTI-AGENT FACT-CHECKING")
    print("=" * 80)

    # 1. Nạp dữ liệu cuộc họp TC-01 để có đồ thị liên kết đa chặng
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json"))
    with open(data_path, "r", encoding="utf-8") as f:
        suite = json.load(f)
    tc01_meeting = suite["test_cases"][0]["meeting"]

    res_init = client.post("/api/meetings/process", json=tc01_meeting)
    assert res_init.status_code == 200
    print("\n✔ [1. Graph Setup] Đã nạp thành công dữ liệu cuộc họp TC-01 vào Knowledge Graph.")

    # 2. Kiểm thử Multi-Hop Querying (Truy vấn đa chặng)
    # Câu hỏi đòi hỏi xâu chuỗi: Action (An) -> Decision (PostgreSQL) -> Superseded (MongoDB) -> Issue (ACID)
    question = "Ai là người chịu trách nhiệm nhiệm vụ liên quan đến quyết định thay thế MongoDB do vướng mắc ACID?"
    req_payload = {
        "query": question,
        "k_hops": 2
    }
    res_query = client.post("/api/graph/multi-hop-query", json=req_payload)
    assert res_query.status_code == 200
    query_resp = res_query.json()
    
    print(f"\n✔ [2. Multi-hop Graph Traversal (k-hop={query_resp['k_hops']})]")
    print(f"   • Câu hỏi: '{question}'")
    print(f"   • Nút hạt giống (Seed Entities): {query_resp['seed_entities']}")
    print(f"   • Số bộ ba (Triples) trích xuất được: {len(query_resp['traversal_path_triples'])}")
    for t in query_resp['traversal_path_triples'][:4]:
        print(f"     - Triple: {t}")
    print(f"   • Số trích dẫn cạnh (Edge Citations): {len(query_resp['edge_citations'])}")
    print(f"   • Câu trả lời Grounded:\n{query_resp['answer']}")

    # Kiểm tra tính toàn vẹn của MultiHopQueryResponse
    validated_query = MultiHopQueryResponse.model_validate(query_resp)
    assert len(validated_query.seed_entities) >= 1
    assert len(validated_query.traversal_path_triples) >= 1
    assert validated_query.answer

    # 3. Kiểm thử Fact-Checking Layer cho Multi-Agent Evaluator–Optimizer
    print("\n✔ [3. Multi-Agent Fact-Checking Layer (Evaluator–Optimizer Loop)]")

    # Case A: Khẳng định sai (REFUTED) - Nói rằng An được giao tích hợp MongoDB (trong khi đã bị PostgreSQL thay thế)
    claim_false = {
        "claim": "An được giao nhiệm vụ tích hợp MongoDB vào source code dự án.",
        "subject": "An",
        "predicate": "ASSIGNED_TO",
        "object": "MongoDB"
    }
    res_verify_false = client.post("/api/graph/verify-claim", json=claim_false)
    assert res_verify_false.status_code == 200
    data_false = res_verify_false.json()
    print(f"\n   [Case A: Khẳng định mâu thuẫn]")
    print(f"   • Claim: '{data_false['claim']}'")
    print(f"   • Verdict: {data_false['verdict']} (is_verified={data_false['is_verified']})")
    print(f"   • Bằng chứng mâu thuẫn (Refuting Edges): {data_false['refuting_edges']}")
    print(f"   • Lý giải phản biện: {data_false['reasoning']}")
    assert data_false["verdict"] == "REFUTED"
    assert data_false["is_verified"] is False
    assert len(data_false["refuting_edges"]) >= 1

    # Case B: Khẳng định đúng (CONFIRMED) - An được giao tích hợp PostgreSQL
    claim_true = {
        "claim": "An được giao nhiệm vụ tích hợp PostgreSQL vào source code.",
        "subject": "An",
        "predicate": "ASSIGNED_TO",
        "object": "PostgreSQL"
    }
    res_verify_true = client.post("/api/graph/verify-claim", json=claim_true)
    assert res_verify_true.status_code == 200
    data_true = res_verify_true.json()
    print(f"\n   [Case B: Khẳng định chuẩn xác]")
    print(f"   • Claim: '{data_true['claim']}'")
    print(f"   • Verdict: {data_true['verdict']} (is_verified={data_true['is_verified']})")
    print(f"   • Bằng chứng hỗ trợ: {data_true['supporting_edges'][:2]}")
    print(f"   • Lý giải: {data_true['reasoning']}")
    assert data_true["verdict"] == "CONFIRMED"
    assert data_true["is_verified"] is True

    # Case C: Khẳng định không có bằng chứng (INSUFFICIENT_EVIDENCE)
    claim_unknown = {
        "claim": "Bình chịu trách nhiệm cấu hình Kubernetes cluster cho production.",
        "subject": "Bình",
        "predicate": "ASSIGNED_TO",
        "object": "Kubernetes"
    }
    res_verify_unknown = client.post("/api/graph/verify-claim", json=claim_unknown)
    assert res_verify_unknown.status_code == 200
    data_unknown = res_verify_unknown.json()
    print(f"\n   [Case C: Khẳng định ngoài phạm vi]")
    print(f"   • Claim: '{data_unknown['claim']}'")
    print(f"   • Verdict: {data_unknown['verdict']} (is_verified={data_unknown['is_verified']})")
    print(f"   • Lý giải: {data_unknown['reasoning']}")
    assert data_unknown["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert data_unknown["is_verified"] is False

    print("\n" + "=" * 80)
    print("HOÀN TẤT KIỂM THỬ GIAI ĐOẠN 4: MULTI-HOP QUERYING & MULTI-AGENT HOẠT ĐỘNG 100%!")
    print("=" * 80)

if __name__ == "__main__":
    test_phase4()
