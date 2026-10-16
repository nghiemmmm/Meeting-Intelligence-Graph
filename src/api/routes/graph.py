from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.schemas.graph import (
    Subgraph, GraphQueryRequest, GraphQueryResponse, EvidenceCitation,
    MultiHopQueryRequest, MultiHopQueryResponse,
    ClaimVerificationRequest, ClaimVerificationResponse
)
from src.services.graph_service import meeting_graph_service
from src.services.neo4j_service import neo4j_service
from src.services.llm_service import llm_service


router = APIRouter(prefix="/api/graph", tags=["Graph & Neo4j AuraDB"])

class CypherExecutionRequest(BaseModel):
    query: str = Field(description="Câu lệnh Cypher cần thực thi (ví dụ: 'MATCH (n:Decision) RETURN n LIMIT 10')")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Các tham số truyền vào câu truy vấn")

@router.get("/subgraph", response_model=Subgraph)
def get_subgraph_around_nodes(
    node_ids: Optional[str] = None,
    meeting_id: Optional[str] = None,
    depth: int = 3
):
    """
    Trích xuất đồ thị con (Subgraph) mở rộng từ danh sách node_ids hoặc meeting_id.
    Ví dụ: /api/graph/subgraph?meeting_id=MTG-TC01
           /api/graph/subgraph?node_ids=DEC-001,ACT-001&depth=2
    """
    if node_ids:
        ids = [nid.strip() for nid in node_ids.split(",") if nid.strip()]
        return meeting_graph_service.get_subgraph(ids, depth=depth)
    elif meeting_id:
        return meeting_graph_service.get_subgraph_for_meeting(meeting_id, depth=depth)
    else:
        return meeting_graph_service.get_full_graph()

@router.get("/stats")
def get_graph_statistics():
    """Lấy số lượng Nodes, Edges và trạng thái kết nối Neo4j AuraDB"""
    return meeting_graph_service.get_stats()

@router.get("/neo4j/stats")
def get_neo4j_aura_stats():
    """Lấy số liệu thực tế lưu trữ trực tiếp trên đám mây Neo4j AuraDB"""
    return neo4j_service.get_stats()

@router.post("/neo4j/sync")
def sync_graph_to_neo4j_aura():
    """Đồng bộ toàn bộ đồ thị tri thức hiện tại lên Neo4j AuraDB"""
    if not neo4j_service.is_connected:
        raise HTTPException(status_code=503, detail="Chưa kết nối được với Neo4j AuraDB. Vui lòng kiểm tra lại thông tin cấu hình .env.")
    
    meeting_graph_service.sync_to_neo4j()
    return {
        "status": "SUCCESS",
        "message": "Đã đồng bộ thành công toàn bộ đồ thị lên Neo4j AuraDB!",
        "stats": neo4j_service.get_stats()
    }

@router.post("/neo4j/cypher")
def execute_raw_cypher(req: CypherExecutionRequest):
    """Thực thi câu lệnh Cypher trực tiếp trên đám mây Neo4j AuraDB"""
    if not neo4j_service.is_connected:
        raise HTTPException(status_code=503, detail="Neo4j AuraDB chưa kết nối")
    
    records = neo4j_service.execute_cypher(req.query, req.parameters)
    return {
        "query": req.query,
        "record_count": len(records),
        "records": records
    }

class EntityResolutionApiRequest(BaseModel):
    entity_type: str = Field(default="PERSON", description="Loại thực thể cần gom cụm: PERSON, SYSTEM_TECH, DECISION_TOPIC, ISSUE")
    entities: List[Dict[str, str]] = Field(description="Danh sách thực thể đầu vào gồm name và description")
    apply_to_graph: bool = Field(default=True, description="Tự động áp dụng và nối cạnh SAME_AS trên đồ thị")

@router.post("/resolve-entities")
def resolve_entity_clusters_api(req: EntityResolutionApiRequest):
    """
    Giai đoạn 2: Entity Resolution - Gom cụm và Chuẩn hóa thực thể xuyên cuộc họp.
    Dựa trên description để khử nhập nhằng, chọn tên canonical và nhận diện các alias.
    """
    result = llm_service.resolve_entity_clusters(req.entity_type, req.entities)
    clusters = result.get("clusters", [])
    graph_update = None
    if req.apply_to_graph and clusters:
        graph_update = meeting_graph_service.apply_entity_resolution(clusters)
    return {
        "status": "SUCCESS",
        "entity_type": req.entity_type,
        "clusters": clusters,
        "graph_update": graph_update
    }

@router.post("/query", response_model=GraphQueryResponse)
def query_meeting_graph(req: GraphQueryRequest):
    """
    Graph Retrieval: Trả lời câu hỏi tự nhiên bằng cách duyệt đồ thị tri thức
    Ví dụ câu hỏi: 'Vì sao chọn Giải pháp B thay vì PostgreSQL?' hoặc 'Ai chịu trách nhiệm nhiệm vụ ACT-001?'
    """
    q_lower = req.query.lower()
    citations = []
    cypher_simulated = None
    answer = ""

    if req.target_action_id or "act-" in q_lower or "nhiệm vụ" in q_lower or "task" in q_lower:
        act_id = req.target_action_id or "ACT-001"
        chain = meeting_graph_service.find_causal_chain_for_action(act_id)
        if "error" not in chain:
            assignee = chain.get("assignee") or "Chưa phân công"
            dec_content = chain["decision"]["content"] if chain.get("decision") else "Quyết định chung"
            old_dec = chain["superseded_decision"]["content"] if chain.get("superseded_decision") else None
            reason = chain.get("objection_reason") or "được thống nhất trong phiên thảo luận"
            
            answer = f"Nhiệm vụ [{chain.get('action_text')}] được giao cho {assignee} để thực thi {dec_content}."
            if old_dec and old_dec.strip().lower() != dec_content.strip().lower():
                answer += f" Quyết định này đã thay thế cho {old_dec} do {reason}."

            citations = chain.get("evidences", [])
            cypher_simulated = f"MATCH (a:ActionItem {{id: '{act_id}'}})-[:IMPLEMENTS]->(d:Decision) OPTIONAL MATCH (d)-[:SUPERSEDES]->(old:Decision) RETURN a, d, old"
        else:
            answer = f"Không tìm thấy thông tin cho nhiệm vụ {act_id}."

    elif "vì sao" in q_lower or "tại sao" in q_lower or "lý do" in q_lower:
        # Tìm kiếm động trên đồ thị thực tế:
        action_nodes = [n for n, d in meeting_graph_service.graph.nodes(data=True) if d.get("label") == "ActionItem"]
        if action_nodes:
            first_act = action_nodes[0]
            chain = meeting_graph_service.find_causal_chain_for_action(first_act)
            if "error" not in chain:
                assignee = chain.get("assignee") or "Chưa phân công"
                dec_content = chain["decision"]["content"] if chain.get("decision") else "quyết định đã chốt"
                old_dec = chain["superseded_decision"]["content"] if chain.get("superseded_decision") else None
                reason = chain.get("objection_reason") or "được thống nhất qua các phản biện"
                
                answer = f"Nhiệm vụ [{chain.get('action_text')}] được giao cho {assignee} để thực thi {dec_content}."
                if old_dec and old_dec.strip().lower() != dec_content.strip().lower():
                    answer += f" Quyết định này đã thay thế cho {old_dec} do {reason}."
                citations = chain.get("evidences", [])
                cypher_simulated = f"MATCH (a:ActionItem {{id: '{first_act}'}})-[:IMPLEMENTS]->(d:Decision) OPTIONAL MATCH (d)-[:SUPERSEDES]->(old:Decision) RETURN a, d, old"

        if not answer:
            # Tra cứu cặp Decision có quan hệ SUPERSEDES trên đồ thị
            supersedes_edges = [
                (u, v) for u, v, k, d in meeting_graph_service.graph.edges(keys=True, data=True)
                if d.get("relation") == "SUPERSEDES"
            ]
            if supersedes_edges:
                u, v = supersedes_edges[0]
                u_node = meeting_graph_service.graph.nodes.get(u, {})
                v_node = meeting_graph_service.graph.nodes.get(v, {})
                answer = f"Phương án [{u_node.get('content', u)}] đã được chốt thay thế cho [{v_node.get('content', v)}] dựa trên các phát biểu phản biện được ghi nhận trong cuộc họp."
                cypher_simulated = f"MATCH (d:Decision {{id: '{u}'}})-[:SUPERSEDES]->(old:Decision {{id: '{v}'}}) RETURN d, old"
            else:
                answer = "Đồ thị chưa ghi nhận quyết định nào thay thế (SUPERSEDES) hoặc nhiệm vụ liên quan trực tiếp đến câu hỏi này."
                cypher_simulated = "MATCH (d:Decision) RETURN d"

    else:
        stats = meeting_graph_service.get_stats()
        answer = f"Meeting Graph hiện có {stats['total_nodes']} nodes và {stats['total_edges']} edges. Neo4j AuraDB: {'Đã kết nối' if stats['neo4j_auradb']['connected'] else 'Chưa kết nối'}."
        cypher_simulated = llm_service.translate_question_to_cypher(req.query)

    return GraphQueryResponse(
        query=req.query,
        answer=answer,
        citations=citations,
        cypher_query_used=cypher_simulated
    )

# --- Giai đoạn 3: Graph Assembly & Hub Entity Profiling Endpoints ---

class CanonicalRewiringRequest(BaseModel):
    clusters: List[Dict[str, Any]] = Field(description="Danh sách các cụm đã chuẩn hóa từ Giai đoạn 2")
    merge_alias_nodes: bool = Field(default=False, description="Xóa các alias nodes sau khi đã chuyển cạnh sang Canonical node")

@router.post("/rewire")
def canonical_rewiring_api(req: CanonicalRewiringRequest):
    """
    Giai đoạn 3: Canonical Rewiring.
    Dịch chuyển toàn bộ đầu mút quan hệ (source & target) từ biến thể thô về Canonical Node.
    """
    return meeting_graph_service.canonical_rewiring(req.clusters, merge_alias_nodes=req.merge_alias_nodes)

@router.get("/diagnostics")
def get_graph_diagnostics_api(hub_threshold: int = 3):
    """
    Giai đoạn 3: Graph Diagnostics.
    Chẩn đoán thành phần liên kết (Connected Components) và phân phối bậc (Degree Distribution / Hub Nodes).
    """
    return meeting_graph_service.get_graph_diagnostics(hub_degree_threshold=hub_threshold)

@router.get("/profile/{node_id}")
@router.post("/profile/{node_id}")
def generate_hub_profile_api(node_id: str):
    """
    Giai đoạn 3: Entity Summarization (Tổng hợp hồ sơ thực thể trung tâm).
    Tạo hồ sơ tri thức 360 độ gồm summary 2-3 đoạn văn, key facts và time range.
    """
    res = meeting_graph_service.generate_hub_profile(node_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

# --- Giai đoạn 4: Multi-hop Querying & Multi-Agent Verification Endpoints ---

@router.post("/multi-hop-query", response_model=MultiHopQueryResponse)
def execute_multihop_query_api(req: MultiHopQueryRequest):
    """
    Giai đoạn 4: Multi-hop Querying (Truy vấn đa chặng).
    Xác định Seed Entities -> Trích xuất Subgraph k-hop -> Tuần tự hóa Triples -> Suy luận bám sát cạnh & Trích dẫn.
    """
    return meeting_graph_service.execute_multihop_query(
        query=req.query,
        k=req.k_hops,
        seed_node_ids=req.seed_entity_ids
    )

@router.post("/verify-claim", response_model=ClaimVerificationResponse)
def verify_claim_api(req: ClaimVerificationRequest):
    """
    Giai đoạn 4: Fact-Checking Layer cho vòng lặp Evaluator–Optimizer trong Multi-Agent Systems.
    Kiểm chứng tính xác thực của khẳng định từ Agent dựa trên các cạnh quan hệ trong Knowledge Graph.
    """
    return meeting_graph_service.verify_claim(
        claim=req.claim,
        subject=req.subject,
        predicate=req.predicate,
        target_obj=req.object
    )


