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
from src.services.graph_service import meeting_graph_service
from src.services.llm_service import llm_service
from src.schemas.resolution import EntityProfile, TimeRange

def test_phase3():
    client = TestClient(app)
    
    print("=" * 75)
    print("KIỂM THỬ GIAI ĐOẠN 3: GRAPH ASSEMBLY, DIAGNOSTICS & HUB NODE SUMMARIZATION")
    print("=" * 75)

    # 1. Khởi tạo một cuộc họp mẫu để có đồ thị cơ sở
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json"))
    with open(data_path, "r", encoding="utf-8") as f:
        suite = json.load(f)
    tc01_meeting = suite["test_cases"][0]["meeting"]

    res = client.post("/api/meetings/process", json=tc01_meeting)
    assert res.status_code == 200
    print("\n✔ [1. Graph Initialization] Đã nạp dữ liệu cuộc họp TC-01 vào NetworkX MultiDiGraph.")

    # 2. Kiểm thử Graph Diagnostics ban đầu
    res_diag = client.get("/api/graph/diagnostics?hub_threshold=2")
    assert res_diag.status_code == 200
    diag_data = res_diag.json()
    print(f"\n✔ [2. Graph Diagnostics]")
    print(f"   • Tổng số Nodes: {diag_data['total_nodes']}")
    print(f"   • Tổng số Edges: {diag_data['total_edges']}")
    print(f"   • Số Connected Components: {diag_data['connected_components_count']}")
    print(f"   • Đồ thị đơn khối liên kết: {diag_data['is_single_connected_component']}")
    print(f"   • Số Hub Nodes (degree >= 2): {len(diag_data['hub_nodes'])}")
    for hub in diag_data['hub_nodes'][:3]:
        print(f"     - [{hub['node_id']}] {hub['name']} ({hub['label']}) | Degree: {hub['degree']} (In: {hub['in_degree']}, Out: {hub['out_degree']})")

    # 3. Thêm các biến thể thực thể để kiểm thử Canonical Rewiring
    # Giả lập biến thể "Sếp Dũng" và "Anh Dũng" có các cạnh riêng
    meeting_graph_service.add_node("USR-SEP_DUNG", "Participant", {
        "name": "Sếp Dũng",
        "description": "Tech Lead phụ trách phê duyệt kiến trúc",
        "mention_count": 2,
        "source_docs": ["MTG-TC01"]
    })
    meeting_graph_service.add_edge("USR-SEP_DUNG", "DEC-003", "APPROVED", {"provenance": "MTG-TC01:Phút 09:20"})
    
    meeting_graph_service.add_node("USR-ANH_DUNG", "Participant", {
        "name": "Anh Dũng",
        "description": "Tech Lead dự án Core Banking",
        "mention_count": 1,
        "source_docs": ["MTG-TC01"]
    })
    meeting_graph_service.add_edge("ACT-001", "USR-ANH_DUNG", "CONSULTED_WITH", {"provenance": "MTG-TC01:Phút 09:30"})

    clusters = [
        {
            "canonical": "Nguyễn Tiến Dũng",
            "aliases": ["Sếp Dũng", "Anh Dũng", "Nguyễn Tiến Dũng"],
            "entity_type": "PERSON",
            "reasoning": "Cùng là Tech Lead phụ trách phê duyệt kiến trúc hệ thống"
        }
    ]

    # Gọi API Canonical Rewiring
    res_rewire = client.post("/api/graph/rewire", json={"clusters": clusters, "merge_alias_nodes": False})
    assert res_rewire.status_code == 200
    rewire_data = res_rewire.json()
    print(f"\n✔ [3. Canonical Rewiring]")
    print(f"   • Số nodes được chuyển hướng: {rewire_data['nodes_rewired']}")
    print(f"   • Số edges được chuyển hướng: {rewire_data['edges_rewired']}")

    # Kiểm tra Canonical Node đã nhận đủ cạnh rewired chưa
    canon_id = "CANONICAL-NGUYỄN_TIẾN_DŨNG"
    assert canon_id in meeting_graph_service.graph
    canon_node = meeting_graph_service.graph.nodes[canon_id]
    print(f"   • Canonical Node: {canon_id} -> Name: '{canon_node.get('name')}', Mentions: {canon_node.get('mention_count')}")
    
    # Kiểm tra in-edges và out-edges của Canonical Node
    out_edges = list(meeting_graph_service.graph.out_edges(canon_id, data=True))
    in_edges = list(meeting_graph_service.graph.in_edges(canon_id, data=True))
    print(f"   • Các cạnh đi ra từ Canonical Node: {[(v, d.get('relation')) for _, v, d in out_edges]}")
    print(f"   • Các cạnh đi vào Canonical Node: {[(u, d.get('relation')) for u, _, d in in_edges]}")
    assert any(d.get("relation") == "APPROVED" for _, _, d in out_edges)
    assert any(d.get("relation") == "CONSULTED_WITH" for _, _, d in in_edges)

    # 4. Kiểm thử Hub Entity Profiling & Summarization
    # Thử trên Canonical Node hoặc trên DEC-003 / ACT-001 (những hub node có degree cao)
    target_hub = "DEC-003"
    res_profile = client.get(f"/api/graph/profile/{target_hub}")
    assert res_profile.status_code == 200
    profile_data = res_profile.json()
    print(f"\n✔ [4. Hub Entity Profiling (SUMMARIZE_PROMPT)] trên Hub Node: [{target_hub}]")
    print(f"   • Entity Name: {profile_data['entity_name']} ({profile_data['entity_type']})")
    print(f"   • Degree: {profile_data['degree']}")
    print(f"   • Time Range: {profile_data['profile']['time_range']}")
    print(f"   • Key Facts ({len(profile_data['profile']['key_facts'])} facts):")
    for fact in profile_data['profile']['key_facts']:
        print(f"     - {fact}")
    print(f"   • Summary (2-3 đoạn):\n{profile_data['profile']['summary']}")

    # Xác thực Pydantic Schema EntityProfile
    validated_profile = EntityProfile.model_validate(profile_data['profile'])
    assert validated_profile.summary
    assert len(validated_profile.key_facts) >= 1
    assert validated_profile.time_range.start

    # Thử profiling trên chính Canonical Node Nguyễn Tiến Dũng
    res_canon_profile = client.get(f"/api/graph/profile/{canon_id}")
    assert res_canon_profile.status_code == 200
    canon_profile_data = res_canon_profile.json()
    print(f"\n✔ [5. Profiling trên Canonical Node vừa ráp nối: {canon_id}]")
    print(f"   • Name: {canon_profile_data['entity_name']}")
    print(f"   • Key Facts: {canon_profile_data['profile']['key_facts']}")

    print("\n" + "=" * 75)
    print("HOÀN TẤT KIỂM THỬ: TẤT CẢ TÍNH NĂNG GIAI ĐOẠN 3 HOẠT ĐỘNG HOÀN HẢO 100%!")
    print("=" * 75)

if __name__ == "__main__":
    test_phase3()
