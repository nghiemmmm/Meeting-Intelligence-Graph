from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GraphNode(BaseModel):
    id: str
    label: str  # Meeting, Participant, Decision, ActionItem, Evidence, Issue, Entity
    properties: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str  # ASSIGNED_TO, IMPLEMENTS, SUPPORTED_BY, SUPERSEDES, MOTIVATED_BY, SPOKE
    properties: Dict[str, Any] = Field(default_factory=dict)

class Subgraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)

class GraphQueryRequest(BaseModel):
    query: str = Field(description="Câu hỏi bằng ngôn ngữ tự nhiên (ví dụ: 'Vì sao chọn PostgreSQL?')")
    meeting_id: Optional[str] = None
    target_action_id: Optional[str] = None
    target_decision_id: Optional[str] = None

class EvidenceCitation(BaseModel):
    evidence_id: str
    speaker: str
    timestamp: str
    quote: str
    quote_text: Optional[str] = None

class GraphQueryResponse(BaseModel):
    query: str
    answer: str = Field(description="Câu trả lời giải thích đầy đủ logic nhân quả")
    citations: List[EvidenceCitation] = Field(default_factory=list, description="Danh sách bằng chứng gốc")
    subgraph: Optional[Subgraph] = None
    cypher_query_used: Optional[str] = None

# --- Giai đoạn 3: Graph Diagnostics Schemas ---
class NodeDegreeInfo(BaseModel):
    node_id: str
    name: str
    label: str
    degree: int
    in_degree: int
    out_degree: int

class GraphDiagnostics(BaseModel):
    total_nodes: int
    total_edges: int
    connected_components_count: int
    is_single_connected_component: bool
    isolated_nodes: List[str] = Field(default_factory=list)
    hub_nodes: List[NodeDegreeInfo] = Field(default_factory=list)
    degree_distribution: Dict[str, int] = Field(default_factory=dict)

# --- Giai đoạn 4: Multi-hop Querying & Multi-Agent Verification Schemas ---
class MultiHopQueryRequest(BaseModel):
    query: str = Field(description="Câu hỏi phức tạp đòi hỏi xâu chuỗi thông tin đa chặng (ví dụ: 'Ai phụ trách nhiệm vụ liên quan đến quyết định thay thế MongoDB do vướng mắc ACID?')")
    k_hops: int = Field(default=2, description="Khoảng cách duyệt láng giềng k-hop (mặc định k=2)")
    seed_entity_ids: Optional[List[str]] = Field(default=None, description="Danh sách nút hạt giống chỉ định trước (nếu để trống hệ thống sẽ tự động nhận diện từ câu hỏi)")

class EdgeCitation(BaseModel):
    source: str
    relation: str
    target: str
    provenance: Optional[str] = None
    speaker: Optional[str] = None
    timestamp: Optional[str] = None
    quote: Optional[str] = None

class MultiHopQueryResponse(BaseModel):
    query: str
    seed_entities: List[str] = Field(default_factory=list, description="Các nút hạt giống được xác định")
    k_hops: int = 2
    traversal_path_triples: List[str] = Field(default_factory=list, description="Danh sách các bộ ba quan hệ (Triples) tuần tự hóa từ Subgraph")
    answer: str = Field(description="Câu trả lời tự nhiên có căn cứ (Grounded Answer) xâu chuỗi logic đa chặng")
    edge_citations: List[EdgeCitation] = Field(default_factory=list, description="Danh sách các trích dẫn xuất xứ từng cạnh")
    subgraph: Optional[Subgraph] = None

class ClaimVerificationRequest(BaseModel):
    claim: str = Field(description="Khẳng định cần kiểm chứng thực tế từ Agent (ví dụ: 'An được giao nhiệm vụ tích hợp MongoDB')")
    subject: Optional[str] = Field(default=None, description="Chủ thể trong câu (ví dụ: 'An')")
    predicate: Optional[str] = Field(default=None, description="Quan hệ kiểm chứng (ví dụ: 'ASSIGNED_TO')")
    object: Optional[str] = Field(default=None, description="Đối tượng (ví dụ: 'MongoDB')")

class ClaimVerificationResponse(BaseModel):
    claim: str
    is_verified: bool = Field(description="Khẳng định có được đồ thị tri thức chứng minh là đúng hay không")
    verdict: str = Field(description="Kết luận kiểm chứng: CONFIRMED (Xác nhận đúng), REFUTED (Bác bỏ do mâu thuẫn), hoặc INSUFFICIENT_EVIDENCE (Không đủ dữ liệu)")
    reasoning: str = Field(description="Giải thích đối soát cụ thể dựa trên các cạnh quan hệ thực tế trong đồ thị")
    supporting_edges: List[str] = Field(default_factory=list, description="Các cạnh ủng hộ khẳng định")
    refuting_edges: List[str] = Field(default_factory=list, description="Các cạnh mâu thuẫn/bác bỏ (ví dụ: SUPERSEDES, OPPOSES)")


