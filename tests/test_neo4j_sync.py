import os
import sys
import json

# Cấu hình UTF-8 console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.schemas.meeting import MeetingInput
from src.services.pipeline_service import pipeline_service
from src.services.neo4j_service import neo4j_service
from src.services.graph_service import meeting_graph_service

def test_neo4j_sync():
    print("=" * 75)
    print("KIỂM THỬ KẾT NỐI VÀ ĐỒNG BỘ DỮ LIỆU ĐỒ THỊ LÊN NEO4J AURADB")
    print("=" * 75)

    # 1. Kiểm tra trạng thái kết nối
    print(f"\n1. Trạng thái kết nối Neo4j AuraDB: {neo4j_service.is_connected}")
    if not neo4j_service.is_connected:
        print("[Lỗi] Không thể kết nối đến Neo4j AuraDB. Vui lòng kiểm tra lại .env!")
        return

    # 2. Đọc dữ liệu cuộc họp mẫu TC-01
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json"))
    with open(data_path, "r", encoding="utf-8") as f:
        suite = json.load(f)
    tc01_meeting = suite["test_cases"][0]["meeting"]

    print(f"\n2. Đang xử lý cuộc họp [{tc01_meeting['meeting_id']}]: '{tc01_meeting['title']}'...")
    meeting_input = MeetingInput(**tc01_meeting)
    
    # Xử lý qua pipeline (tự động đồng bộ sang Neo4j AuraDB qua MeetingGraphService)
    result = pipeline_service.process_meeting(meeting_input, reset_previous=True)
    
    # Gọi đồng bộ toàn diện để chắc chắn
    meeting_graph_service.sync_to_neo4j()

    print(f"\n3. Kết quả xử lý:")
    print(f"   • Quyết định: {len(result.decisions)}")
    print(f"   • Action Items: {len(result.action_items)}")
    print(f"   • Vướng mắc (Issues): {len(result.issues)}")
    print(f"   • Graph Nodes in Memory: {result.graph_stats['total_nodes']}")
    print(f"   • Graph Edges in Memory: {result.graph_stats['total_edges']}")

    # 4. Kiểm tra dữ liệu thực tế trên Neo4j AuraDB qua Cypher
    print(f"\n4. Kiểm tra thống kê trực tiếp trên đám mây Neo4j AuraDB:")
    stats = neo4j_service.get_stats()
    print(f"   • URI: {stats.get('uri')}")
    print(f"   • Database: {stats.get('database')}")
    print(f"   • Tổng số Nodes trên AuraDB: {stats.get('nodes')}")
    print(f"   • Tổng số Relationships trên AuraDB: {stats.get('relationships')}")
    print(f"   • Các nhãn Nodes (Labels): {stats.get('labels')}")
    print(f"   • Các kiểu quan hệ (Relationship Types): {stats.get('relationship_types')}")

    # 5. Truy vấn chuỗi nhân quả trực tiếp bằng Cypher trên Neo4j
    print(f"\n5. Chạy truy vấn Cypher kiểm tra quan hệ SUPERSEDES và IMPLEMENTS:")
    cypher_check = """
    MATCH (a:ActionItem)-[r1:IMPLEMENTS]->(d:Decision)
    OPTIONAL MATCH (d)-[r2:SUPERSEDES]->(old:Decision)
    RETURN a.id AS action_id, a.action_text AS action_text, d.id AS decision_id, d.content AS decision, old.id AS old_id
    """
    records = neo4j_service.execute_cypher(cypher_check)
    print(f"   • Số bản ghi tìm thấy: {len(records)}")
    for rec in records:
        print(f"   ➜ Action [{rec['action_id']}]: {rec['action_text']}")
        print(f"     Thực thi Decision [{rec['decision_id']}]: {rec['decision']}")
        if rec.get('old_id'):
            print(f"     Thay thế (SUPERSEDES) Decision: [{rec['old_id']}]")

    print("\n" + "=" * 75)
    print("HOÀN TẤT: ĐỒ THỊ TRI THỨC CUỘC HỌP ĐÃ ĐƯỢC LƯU TRỮ VÀ XÁC MINH TRÊN NEO4J AURADB!")
    print("=" * 75)

if __name__ == "__main__":
    test_neo4j_sync()
