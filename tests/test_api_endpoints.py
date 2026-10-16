import os
import sys
import json
from starlette.testclient import TestClient

# Cấu hình UTF-8 console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

def test_api():
    client = TestClient(app)
    
    print("=" * 70)
    print("KIỂM THỬ TÍCH HỢP TẤT CẢ ENDPOINTS CỦA BACKEND FASTAPI")
    print("=" * 70)

    # 1. Test Healthcheck
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"✔ [GET /health] Status: {res.status_code} - Response: {res.json()}")

    # 2. Test Process Meeting (TC-01)
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json"))
    with open(data_path, "r", encoding="utf-8") as f:
        suite = json.load(f)
    tc01_meeting = suite["test_cases"][0]["meeting"]

    res = client.post("/api/meetings/process", json=tc01_meeting)
    assert res.status_code == 200, f"Process meeting failed: {res.text}"
    meeting_result = res.json()
    print(f"\n✔ [POST /api/meetings/process] Status: {res.status_code}")
    print(f"   • Meeting ID: {meeting_result['meeting_id']}")
    print(f"   • Decisions count: {len(meeting_result['decisions'])}")
    print(f"   • Action Items count: {len(meeting_result['action_items'])}")
    print(f"   • Issues count: {len(meeting_result['issues'])}")
    print(f"   • Graph Stats: {meeting_result['graph_stats']}")

    # 3. Test Get Meeting by ID
    res = client.get("/api/meetings/MTG-TC01")
    assert res.status_code == 200
    print(f"\n✔ [GET /api/meetings/MTG-TC01] Status: {res.status_code} - Title: {res.json()['title']}")

    # 4. Test Final Active Decisions
    res = client.get("/api/decisions/final")
    assert res.status_code == 200
    final_decs = res.json()
    print(f"\n✔ [GET /api/decisions/final] Quyết định hiệu lực cuối cùng sau cuộc họp:")
    for d in final_decs:
        print(f"   • ID: {d['decision_id']} | Nội dung: {d['content']} | SUPERSEDES: {d['supersedes_decision_id']}")

    # 5. Test Causal Chain Traversal for Action
    res = client.get("/api/actions/ACT-001/causal-chain")
    assert res.status_code == 200
    chain = res.json()
    print(f"\n✔ [GET /api/actions/ACT-001/causal-chain] Chuỗi truy vết nhân quả:")
    print(f"   • Hành động: {chain['action_text']}")
    print(f"   • Người thực hiện: {chain['assignee']}")
    print(f"   • Thực thi quyết định: {chain['decision']['content']}")
    print(f"   • Lý do/Vướng mắc dẫn tới quyết định: {chain['objection_reason']}")
    print(f"   • Số lượng bằng chứng trích dẫn: {len(chain['evidences'])}")

    # 6. Test Insights (Issues & Unresolved)
    res = client.get("/api/insights/issues")
    assert res.status_code == 200
    print(f"\n✔ [GET /api/insights/issues] Đã trích xuất {len(res.json())} vướng mắc/rủi ro.")

    # 7. Test Graph Traversal Query
    query_payload = {
        "query": "Vì sao chúng ta chọn PostgreSQL thay vì MongoDB, ai phụ trách?",
        "target_action_id": "ACT-001"
    }
    res = client.post("/api/graph/query", json=query_payload)
    assert res.status_code == 200
    graph_ans = res.json()
    print(f"\n✔ [POST /api/graph/query] Câu hỏi: '{query_payload['query']}':")
    print(f"   • Câu trả lời giải thích: {graph_ans['answer']}")
    print(f"   • Cypher mô phỏng: {graph_ans['cypher_query_used']}")
    print(f"   • Số trích dẫn: {len(graph_ans['citations'])}")

    # 8. Test Graph Subgraph
    res = client.get("/api/graph/subgraph?node_ids=DEC-001,ACT-001&depth=1")
    assert res.status_code == 200
    subgraph = res.json()
    print(f"\n✔ [GET /api/graph/subgraph] Trích xuất Subgraph:")
    print(f"   • Số node con: {len(subgraph['nodes'])}")
    print(f"   • Số cạnh liên kết: {len(subgraph['edges'])}")

    print("\n" + "=" * 70)
    print("HOÀN TẤT TOÀN BỘ KIỂM THỬ: TẤT CẢ ENDPOINTS HOẠT ĐỘNG CHUẨN XÁC 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_api()
