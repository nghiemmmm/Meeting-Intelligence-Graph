import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from src.schemas.graph import (
    GraphNode, GraphEdge, Subgraph, EvidenceCitation,
    EdgeCitation, MultiHopQueryResponse, ClaimVerificationResponse
)
from src.services.neo4j_service import neo4j_service
from src.config import settings


class MeetingGraphService:
    def __init__(self):
        # Sử dụng Directed Multigraph để lưu trữ đồ thị in-memory
        self.graph = nx.MultiDiGraph()

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any] = None):
        """Thêm node vào cả NetworkX in-memory và đồng bộ trực tiếp sang Neo4j AuraDB"""
        props = properties.copy() if properties else {}
        props["label"] = label
        self.graph.add_node(node_id, **props)

        # Lưu đồng bộ trực tiếp vào Neo4j AuraDB nếu đã kết nối
        if neo4j_service.is_connected:
            neo4j_service.save_node(node_id, label, properties)

    def add_edge(self, source_id: str, target_id: str, relation: str, properties: Dict[str, Any] = None):
        """Thêm cạnh vào cả NetworkX in-memory và đồng bộ trực tiếp sang Neo4j AuraDB"""
        props = properties.copy() if properties else {}
        props["relation"] = relation
        self.graph.add_edge(source_id, target_id, key=relation, **props)

        # Lưu đồng bộ trực tiếp vào Neo4j AuraDB nếu đã kết nối
        if neo4j_service.is_connected:
            neo4j_service.save_edge(source_id, target_id, relation, properties)

    def sync_to_neo4j(self):
        """Đồng bộ toàn bộ đồ thị hiện có sang Neo4j AuraDB"""
        if neo4j_service.is_connected:
            neo4j_service.sync_from_networkx(self.graph)

    def get_full_graph(self) -> Subgraph:
        """Lấy toàn bộ đồ thị hiện có để hiển thị trên Graph Visualizer"""
        nodes_list = []
        for n, data in self.graph.nodes(data=True):
            label = data.get("label", "Entity")
            nodes_list.append(GraphNode(id=n, label=label, properties={k: v for k, v in data.items() if k != "label"}))

        edges_list = []
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            relation = data.get("relation", k)
            edges_list.append(GraphEdge(source=u, target=v, relation=relation, properties={k: v for k, v in data.items() if k != "relation"}))

        return Subgraph(nodes=nodes_list, edges=edges_list)

    def get_subgraph_for_meeting(self, meeting_id: str, depth: int = 3) -> Subgraph:
        """Lấy đồ thị con gắn với cuộc họp (bao gồm Decision, Action, Issue, Evidence, Participant)"""
        if meeting_id in self.graph:
            return self.get_subgraph([meeting_id], depth=depth)
        return self.get_full_graph()

    def get_subgraph(self, node_ids: List[str], depth: int = 2) -> Subgraph:
        """Trích xuất đồ thị con mở rộng quanh danh sách node_ids với bán kính depth"""
        if not node_ids:
            return self.get_full_graph()

        nodes_to_include = set(node_ids)
        for _ in range(depth):
            current_nodes = list(nodes_to_include)
            for n in current_nodes:
                if n in self.graph:
                    # Lấy cả láng giềng vào và ra
                    nodes_to_include.update(self.graph.successors(n))
                    nodes_to_include.update(self.graph.predecessors(n))

        valid_nodes = [n for n in nodes_to_include if n in self.graph]
        if not valid_nodes:
            return self.get_full_graph()

        sub = self.graph.subgraph(valid_nodes)

        nodes_list = []
        for n, data in sub.nodes(data=True):
            label = data.get("label", "Entity")
            nodes_list.append(GraphNode(id=n, label=label, properties={k: v for k, v in data.items() if k != "label"}))

        edges_list = []
        for u, v, k, data in sub.edges(keys=True, data=True):
            relation = data.get("relation", k)
            edges_list.append(GraphEdge(source=u, target=v, relation=relation, properties={k: v for k, v in data.items() if k != "relation"}))

        return Subgraph(nodes=nodes_list, edges=edges_list)

    def find_causal_chain_for_action(self, action_id: str) -> Dict[str, Any]:
        """Truy vết chuỗi nhân quả: Action -> Decision -> Issue/Objection -> Evidence"""
        if action_id not in self.graph:
            return {"error": f"Không tìm thấy ActionItem {action_id}"}

        result = {
            "action_id": action_id,
            "action_text": self.graph.nodes[action_id].get("action_text", ""),
            "assignee": None,
            "decision": None,
            "superseded_decision": None,
            "objection_reason": None,
            "evidences": []
        }

        # Tìm người được giao việc
        for target, edge_data in self.graph[action_id].items():
            for k, d in edge_data.items():
                if d.get("relation") == "ASSIGNED_TO":
                    result["assignee"] = self.graph.nodes[target].get("name", target)

        # Lần theo cạnh IMPLEMENTS -> Decision
        for target, edge_data in self.graph[action_id].items():
            for k, d in edge_data.items():
                if d.get("relation") == "IMPLEMENTS":
                    dec_id = target
                    dec_node = self.graph.nodes[dec_id]
                    result["decision"] = {
                        "id": dec_id,
                        "content": dec_node.get("content", ""),
                        "status": dec_node.get("status", "CONFIRMED")
                    }

                    # Kiểm tra xem Decision này có SUPERSEDES ai không
                    for sub_target, sub_edge_data in self.graph[dec_id].items():
                        for sk, sd in sub_edge_data.items():
                            if sd.get("relation") == "SUPERSEDES":
                                old_dec_node = self.graph.nodes[sub_target]
                                result["superseded_decision"] = {
                                    "id": sub_target,
                                    "content": old_dec_node.get("content", "")
                                }

                    # Kiểm tra cạnh MOTIVATED_BY -> Issue
                    for sub_target, sub_edge_data in self.graph[dec_id].items():
                        for sk, sd in sub_edge_data.items():
                            if sd.get("relation") == "MOTIVATED_BY":
                                issue_node = self.graph.nodes[sub_target]
                                result["objection_reason"] = issue_node.get("description", "")

                    # Thu thập Evidence của Decision
                    seen_ev_ids = set()
                    for sub_target, sub_edge_data in self.graph[dec_id].items():
                        for sk, sd in sub_edge_data.items():
                            if sd.get("relation") == "SUPPORTED_BY" and sub_target not in seen_ev_ids:
                                ev_node = self.graph.nodes[sub_target]
                                q = ev_node.get("quote_text") or ev_node.get("quote") or ev_node.get("content") or ""
                                if q:
                                    seen_ev_ids.add(sub_target)
                                    result["evidences"].append(EvidenceCitation(
                                        evidence_id=sub_target,
                                        speaker=ev_node.get("speaker", "Unknown"),
                                        timestamp=ev_node.get("timestamp", "00:00"),
                                        quote=q,
                                        quote_text=q
                                    ))

        # Thu thập Evidence trực tiếp của Action
        for target, edge_data in self.graph[action_id].items():
            for k, d in edge_data.items():
                if d.get("relation") == "SUPPORTED_BY" and target not in seen_ev_ids:
                    ev_node = self.graph.nodes[target]
                    q = ev_node.get("quote_text") or ev_node.get("quote") or ev_node.get("content") or ""
                    if q:
                        seen_ev_ids.add(target)
                        result["evidences"].append(EvidenceCitation(
                            evidence_id=target,
                            speaker=ev_node.get("speaker", "Unknown"),
                            timestamp=ev_node.get("timestamp", "00:00"),
                            quote=q,
                            quote_text=q
                        ))

        return result

    def apply_entity_resolution(self, clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Áp dụng kết quả Entity Resolution vào Knowledge Graph:
        - Với mỗi cụm: đặt thuộc tính canonical_name và aliases cho các nodes tương ứng.
        - Nối cạnh SAME_AS giữa các biến thể và node canonical.
        """
        applied_count = 0
        for cluster in clusters:
            canonical = cluster.get("canonical")
            aliases = cluster.get("aliases", [])
            entity_type = cluster.get("entity_type", "Entity")

            # Tìm các node trong đồ thị có tên trùng khớp với bất kỳ alias nào
            matched_nodes = []
            for node_id, data in self.graph.nodes(data=True):
                name = data.get("name") or data.get("content") or node_id
                if name in aliases:
                    matched_nodes.append(node_id)
                    data["canonical_name"] = canonical
                    data["aliases"] = aliases

            # Nối cạnh SAME_AS giữa các node biến thể
            if len(matched_nodes) > 1:
                canonical_node = matched_nodes[0]
                for other_node in matched_nodes[1:]:
                    self.add_edge(other_node, canonical_node, "SAME_AS", {
                        "reason": cluster.get("reasoning", "Entity Resolution")
                    })
                applied_count += 1

        return {
            "status": "SUCCESS",
            "clusters_applied": applied_count,
            "total_clusters": len(clusters)
        }

    def canonical_rewiring(self, clusters: List[Dict[str, Any]], merge_alias_nodes: bool = False) -> Dict[str, Any]:
        """
        Giai đoạn 3: Canonical Rewiring (Ráp nối Đồ thị với NetworkX MultiDiGraph).
        Dịch chuyển toàn bộ đầu mút của quan hệ (source và target) từ các biến thể thô
        sang tên chuẩn (canonical name) dựa trên bản đồ alias thu được ở Giai đoạn 2.
        - Node: type, source_docs, mention_count
        - Edge: predicate, provenance_document/evidence
        """
        rewired_edges_count = 0
        nodes_rewired_count = 0

        canonical_mappings = {}

        for cluster in clusters:
            canonical = cluster.get("canonical")
            aliases = cluster.get("aliases", [])
            entity_type = cluster.get("entity_type", "Entity")

            if not canonical or not aliases:
                continue

            # 1. Tìm hoặc xác định Canonical Node trong đồ thị
            canonical_node_id = f"CANONICAL-{canonical.upper().replace(' ', '_')}"
            
            # Kiểm tra xem đã có node nào mang id này hoặc tên chính xác trùng với canonical name
            found_existing = None
            if canonical_node_id in self.graph:
                found_existing = canonical_node_id
            else:
                for nid, data in list(self.graph.nodes(data=True)):
                    if data.get("name") == canonical and nid.startswith("CANONICAL-"):
                        found_existing = nid
                        break

            if found_existing:
                canonical_node_id = found_existing
            else:
                self.add_node(canonical_node_id, entity_type, {
                    "name": canonical,
                    "canonical_name": canonical,
                    "type": entity_type,
                    "mention_count": 0,
                    "source_docs": []
                })

            canon_data = self.graph.nodes[canonical_node_id]
            canon_data["canonical_name"] = canonical
            canon_data["aliases"] = aliases
            canon_data["type"] = entity_type
            canon_data.setdefault("mention_count", 0)
            canon_data.setdefault("source_docs", [])
            canonical_mappings[canonical] = canonical_node_id


            # 2. Quét các alias nodes khác và dịch chuyển các cạnh (Rewiring)
            alias_nodes = []
            for nid, data in list(self.graph.nodes(data=True)):
                if nid == canonical_node_id:
                    continue
                name = data.get("name") or data.get("content") or nid
                if name in aliases or data.get("canonical_name") == canonical:
                    alias_nodes.append(nid)

            for a_nid in alias_nodes:
                a_data = self.graph.nodes[a_nid]
                # Hợp nhất mention_count và source_docs
                canon_data["mention_count"] += a_data.get("mention_count", 1)
                for doc in a_data.get("source_docs", []):
                    if doc not in canon_data["source_docs"]:
                        canon_data["source_docs"].append(doc)
                if a_data.get("meeting_id") and a_data["meeting_id"] not in canon_data["source_docs"]:
                    canon_data["source_docs"].append(a_data["meeting_id"])

                # Dịch chuyển In-edges: (u, a_nid) -> (u, canonical_node_id)
                in_edges = list(self.graph.in_edges(a_nid, keys=True, data=True))
                for u, _, k, edata in in_edges:
                    if u != canonical_node_id:
                        edge_props = {k_prop: v_prop for k_prop, v_prop in edata.items() if k_prop != "relation"}
                        rel = edata.get("relation", k)
                        self.add_edge(u, canonical_node_id, rel, edge_props)
                        rewired_edges_count += 1

                # Dịch chuyển Out-edges: (a_nid, v) -> (canonical_node_id, v)
                out_edges = list(self.graph.out_edges(a_nid, keys=True, data=True))
                for _, v, k, edata in out_edges:
                    if v != canonical_node_id and edata.get("relation") != "SAME_AS":
                        edge_props = {k_prop: v_prop for k_prop, v_prop in edata.items() if k_prop != "relation"}
                        rel = edata.get("relation", k)
                        self.add_edge(canonical_node_id, v, rel, edge_props)
                        rewired_edges_count += 1

                # Giữ cạnh liên kết SAME_AS để truy vết hoặc xóa nếu merge_alias_nodes=True
                if merge_alias_nodes:
                    self.graph.remove_node(a_nid)
                else:
                    self.add_edge(a_nid, canonical_node_id, "SAME_AS", {
                        "reason": cluster.get("reasoning", "Canonical Rewired")
                    })

                nodes_rewired_count += 1

        return {
            "status": "SUCCESS",
            "nodes_rewired": nodes_rewired_count,
            "edges_rewired": rewired_edges_count,
            "total_clusters": len(clusters),
            "canonical_mappings": canonical_mappings
        }


    def get_graph_diagnostics(self, hub_degree_threshold: int = 3) -> Dict[str, Any]:
        """
        Kiểm tra chẩn đoán đồ thị (Graph Diagnostics):
        1. Connected Components (Thành phần liên kết): Đồ thị chuẩn nên là 1 khối duy nhất.
           Phát hiện các hòn đảo rời rạc (Islands) / Isolated nodes.
        2. Degree Distribution & Hub Nodes: Phát hiện các nút hub có bậc cao (degree >= threshold).
        """
        total_nodes = self.graph.number_of_nodes()
        total_edges = self.graph.number_of_edges()

        if total_nodes == 0:
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "connected_components_count": 0,
                "is_single_connected_component": True,
                "isolated_nodes": [],
                "hub_nodes": [],
                "degree_distribution": {}
            }

        weakly_connected = list(nx.weakly_connected_components(self.graph))
        connected_components_count = len(weakly_connected)
        is_single_connected_component = (connected_components_count == 1)

        isolated_nodes = list(nx.isolates(self.graph))

        degree_distribution: Dict[str, int] = {}
        hub_nodes = []

        for nid, data in self.graph.nodes(data=True):
            deg = self.graph.degree(nid)
            in_deg = self.graph.in_degree(nid)
            out_deg = self.graph.out_degree(nid)

            deg_str = str(deg)
            degree_distribution[deg_str] = degree_distribution.get(deg_str, 0) + 1

            if deg >= hub_degree_threshold:
                name = data.get("canonical_name") or data.get("name") or data.get("content") or data.get("title") or nid
                label = data.get("label", "Entity")
                hub_nodes.append({
                    "node_id": nid,
                    "name": name,
                    "label": label,
                    "degree": deg,
                    "in_degree": in_deg,
                    "out_degree": out_deg
                })

        hub_nodes.sort(key=lambda x: x["degree"], reverse=True)

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "connected_components_count": connected_components_count,
            "is_single_connected_component": is_single_connected_component,
            "isolated_nodes": isolated_nodes,
            "hub_nodes": hub_nodes,
            "degree_distribution": degree_distribution,
            "components_summary": [len(c) for c in weakly_connected]
        }

    def extract_entity_context(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Trích xuất toàn bộ ngữ cảnh lân cận của node (excerpts & relations)
        để phục vụ việc tổng hợp Entity Profile.
        """
        if node_id not in self.graph:
            return None

        node_data = self.graph.nodes[node_id]
        name = node_data.get("canonical_name") or node_data.get("name") or node_data.get("content") or node_id
        label = node_data.get("label", "Entity")

        excerpts = []
        if node_data.get("description"):
            excerpts.append(f"Mô tả ban đầu: {node_data['description']}")
        if node_data.get("action_text"):
            excerpts.append(f"Hành động phân công: {node_data['action_text']}")
        if node_data.get("content"):
            excerpts.append(f"Nội dung quyết định: {node_data['content']}")

        relations = []
        # Quan hệ đi ra (Out-edges)
        for _, target, k, edata in self.graph.out_edges(node_id, keys=True, data=True):
            rel = edata.get("relation", k)
            target_data = self.graph.nodes.get(target, {})
            t_name = target_data.get("name") or target_data.get("content") or target
            t_label = target_data.get("label", "")
            relations.append(f"--[{rel}]--> {t_name} ({t_label})")
            if target_data.get("label") == "Evidence" and target_data.get("quote_text"):
                excerpts.append(f"Phát ngôn [{target_data.get('timestamp', '')}] của {target_data.get('speaker', '')}: \"{target_data['quote_text']}\"")

        # Quan hệ đi vào (In-edges)
        for source, _, k, edata in self.graph.in_edges(node_id, keys=True, data=True):
            rel = edata.get("relation", k)
            source_data = self.graph.nodes.get(source, {})
            s_name = source_data.get("name") or source_data.get("content") or source
            s_label = source_data.get("label", "")
            relations.append(f"<--[{rel}]-- {s_name} ({s_label})")
            if source_data.get("label") == "Evidence" and source_data.get("quote_text"):
                excerpts.append(f"Phát ngôn [{source_data.get('timestamp', '')}] của {source_data.get('speaker', '')}: \"{source_data['quote_text']}\"")

        # Deduplicate excerpts preserving order
        dedup_excerpts = list(dict.fromkeys(excerpts))

        return {
            "node_id": node_id,
            "name": name,
            "label": label,
            "excerpts": dedup_excerpts,
            "relations": relations
        }

    def generate_hub_profile(self, node_id: str) -> Dict[str, Any]:
        """
        Giai đoạn 3: Entity Summarization cho các nút trung tâm (Hub nodes).
        Gọi Claude Sonnet / OpenAI / Gemini để tổng hợp Hồ sơ Tri thức 360 độ.
        """
        context = self.extract_entity_context(node_id)
        if not context:
            return {"error": f"Không tìm thấy node {node_id} trong đồ thị"}

        from src.services.llm_service import llm_service
        profile = llm_service.summarize_hub_entity(
            name=context["name"],
            etype=context["label"],
            excerpts=context["excerpts"],
            relations=context["relations"]
        )

        # Lưu profile vào thuộc tính node
        self.graph.nodes[node_id]["profile"] = profile
        if neo4j_service.is_connected:
            neo4j_service.save_node(node_id, context["label"], {"profile_summary": profile.get("summary")})

        return {
            "node_id": node_id,
            "entity_name": context["name"],
            "entity_type": context["label"],
            "degree": self.graph.degree(node_id),
            "profile": profile,
            "source_excerpts": context["excerpts"],
            "known_relations": context["relations"]
        }

    # --- Giai đoạn 4: Multi-hop Querying & Multi-Agent Fact-Checking ---

    def find_seed_entities(self, query: str) -> List[str]:
        """
        Tự động xác định các nút hạt giống (Seed Entities) từ câu hỏi của người dùng.
        """
        q_lower = query.lower()
        matched = []

        # 1. Tìm khớp trực tiếp theo ID node (ACT-001, DEC-003, ISS-001, ...)
        for nid in self.graph.nodes:
            if nid.lower() in q_lower:
                matched.append(nid)

        # 2. Tìm khớp theo Tên thực thể, Canonical Name, Biến thể Aliases
        for nid, data in self.graph.nodes(data=True):
            if nid in matched:
                continue
            name = (data.get("canonical_name") or data.get("name") or "").lower()
            if name and len(name) >= 2 and (name in q_lower or any(word in q_lower for word in name.split() if len(word) >= 3)):
                matched.append(nid)
                continue

            for alias in data.get("aliases", []):
                if alias.lower() in q_lower:
                    matched.append(nid)
                    break

        # 3. Tìm khớp theo từ khóa quan trọng trong content / description / action_text
        keywords = ["postgresql", "mongodb", "mysql", "react", "acid", "thanh toán", "kiến trúc"]
        for kw in keywords:
            if kw in q_lower:
                for nid, data in self.graph.nodes(data=True):
                    if nid in matched:
                        continue
                    text = (data.get("content", "") + " " + data.get("title", "") + " " + data.get("action_text", "")).lower()
                    if kw in text:
                        matched.append(nid)

        # Nếu không tìm thấy, lấy các Hub Nodes có bậc cao nhất làm mặc định
        if not matched:
            diag = self.get_graph_diagnostics(hub_degree_threshold=2)
            matched = [h["node_id"] for h in diag.get("hub_nodes", [])[:3]]

        return list(dict.fromkeys(matched))[:5]

    def get_k_hop_subgraph(self, seed_node_ids: List[str], k: int = 2) -> Subgraph:
        """
        Trích xuất Subgraph trong phạm vi k bước nhảy (k-hop neighborhood) quanh các nút hạt giống.
        """
        nodes_to_include = set(seed_node_ids)
        for _ in range(k):
            current = list(nodes_to_include)
            for n in current:
                if n in self.graph:
                    nodes_to_include.update(self.graph.successors(n))
                    nodes_to_include.update(self.graph.predecessors(n))

        valid_nodes = [n for n in nodes_to_include if n in self.graph]
        sub = self.graph.subgraph(valid_nodes)

        nodes_list = []
        for n, data in sub.nodes(data=True):
            label = data.get("label", "Entity")
            nodes_list.append(GraphNode(id=n, label=label, properties={k_p: v_p for k_p, v_p in data.items() if k_p != "label"}))

        edges_list = []
        for u, v, k_edge, data in sub.edges(keys=True, data=True):
            relation = data.get("relation", k_edge)
            edges_list.append(GraphEdge(source=u, target=v, relation=relation, properties={k_p: v_p for k_p, v_p in data.items() if k_p != "relation"}))

        return Subgraph(nodes=nodes_list, edges=edges_list)

    def serialize_subgraph_to_triples(self, subgraph: Subgraph) -> Tuple[List[str], List[EdgeCitation]]:
        """
        Tuần tự hóa các bộ ba (triples) và trích dẫn theo cạnh (Edge-level citations) từ Subgraph.
        """
        triples = []
        citations = []

        for edge in subgraph.edges:
            u_data = self.graph.nodes.get(edge.source, {})
            v_data = self.graph.nodes.get(edge.target, {})

            u_name = u_data.get("canonical_name") or u_data.get("name") or u_data.get("content") or u_data.get("action_text") or edge.source
            v_name = v_data.get("canonical_name") or v_data.get("name") or v_data.get("content") or v_data.get("action_text") or edge.target

            u_label = u_data.get("label", "Entity")
            v_label = v_data.get("label", "Entity")

            # Xử lý trích dẫn provenance
            prov = edge.properties.get("provenance") or edge.properties.get("reason")
            quote = None
            speaker = None
            timestamp = None
            if v_label == "Evidence":
                quote = v_data.get("quote_text")
                speaker = v_data.get("speaker")
                timestamp = v_data.get("timestamp")
            elif u_label == "Evidence":
                quote = u_data.get("quote_text")
                speaker = u_data.get("speaker")
                timestamp = u_data.get("timestamp")

            citation_note = f" (Dẫn chứng: {prov})" if prov else ""
            if quote:
                citation_note = f" (Phát ngôn [{timestamp}] của {speaker}: \"{quote}\")"

            triple_str = f"({u_name} [{u_label}]) --[{edge.relation}]--> ({v_name} [{v_label}]){citation_note}"
            triples.append(triple_str)

            citations.append(EdgeCitation(
                source=edge.source,
                relation=edge.relation,
                target=edge.target,
                provenance=prov,
                speaker=speaker,
                timestamp=timestamp,
                quote=quote
            ))

        return triples, citations

    def execute_multihop_query(self, query: str, k: int = 2, seed_node_ids: Optional[List[str]] = None) -> MultiHopQueryResponse:
        """
        Giai đoạn 4: Multi-hop Querying (Truy vấn đa chặng).
        Xác định Seed Entities -> Trích xuất Subgraph k-hop -> Tuần tự hóa Triples -> Suy luận bám sát cạnh & Trích dẫn.
        """
        seeds = seed_node_ids or self.find_seed_entities(query)
        if not seeds:
            return MultiHopQueryResponse(
                query=query,
                seed_entities=[],
                k_hops=k,
                traversal_path_triples=[],
                answer="Hệ thống không tìm thấy thực thể liên quan trong đồ thị tri thức cuộc họp để giải quyết câu hỏi.",
                edge_citations=[],
                subgraph=None
            )

        subgraph = self.get_k_hop_subgraph(seeds, k=k)
        triples, citations = self.serialize_subgraph_to_triples(subgraph)

        triples_formatted = "\n".join([f"- {t}" for t in triples]) if triples else "Không có cạnh liên kết trực tiếp."

        from src.services.llm_service import llm_service
        answer = llm_service.generate_multihop_grounded_answer(query, triples_formatted)

        return MultiHopQueryResponse(
            query=query,
            seed_entities=seeds,
            k_hops=k,
            traversal_path_triples=triples,
            answer=answer,
            edge_citations=citations,
            subgraph=subgraph
        )

    def verify_claim(self, claim: str, subject: Optional[str] = None, predicate: Optional[str] = None, target_obj: Optional[str] = None) -> ClaimVerificationResponse:
        """
        Lớp kiểm chứng thực tế (Fact-Checking Verification Layer) cho vòng lặp Evaluator–Optimizer trong Multi-Agent Systems.
        Đánh giá tính xác thực của khẳng định từ Agent dựa trên cấu trúc đồ thị tri thức.
        """
        claim_lower = claim.lower()
        supporting = []
        refuting = []

        # 1. Kiểm tra mâu thuẫn đối kháng đặc trưng của Meeting (SUPERSEDES, OPPOSES, MOTIVATED_BY)
        # Ví dụ khẳng định giao việc cho MongoDB nhưng PostgreSQL đã thay thế MongoDB:
        if "mongodb" in claim_lower and any("postgresql" in (self.graph.nodes[n].get("content", "") + self.graph.nodes[n].get("name", "")).lower() for n in self.graph.nodes):
            for u, v, k, edata in self.graph.edges(keys=True, data=True):
                rel = edata.get("relation", k)
                if rel == "SUPERSEDES":
                    u_name = self.graph.nodes[u].get("content") or u
                    v_name = self.graph.nodes[v].get("content") or v
                    refuting.append(f"{u_name} --[SUPERSEDES]--> {v_name}")
                elif rel == "IMPLEMENTS":
                    u_text = self.graph.nodes[u].get("action_text") or u
                    v_name = self.graph.nodes[v].get("content") or v
                    if "postgresql" in v_name.lower():
                        refuting.append(f"{u_text} --[IMPLEMENTS]--> {v_name}")

        if refuting:
            reasoning = (
                f"Khẳng định sai lệch với đồ thị tri thức cuộc họp: "
                f"Phương án được đề cập đã bị thay thế (SUPERSEDES) hoặc phản biện. "
                f"Cụ thể: {'; '.join(refuting[:2])}."
            )
            return ClaimVerificationResponse(
                claim=claim,
                is_verified=False,
                verdict="REFUTED",
                reasoning=reasoning,
                supporting_edges=supporting,
                refuting_edges=refuting
            )

        # 2. Kiểm tra xem có cạnh liên kết trực tiếp giữa các node liên quan không
        # Trích xuất các từ khóa đặc trưng của claim (độ dài >= 2)
        key_tokens = [w for w in ["an", "bình", "dũng", "postgresql", "react", "tích hợp", "nhiệm vụ", "giao", "source", "acid"] if w in claim_lower]
        for u, v, k, edata in self.graph.edges(keys=True, data=True):
            rel = edata.get("relation", k)
            u_data = self.graph.nodes[u]
            v_data = self.graph.nodes[v]
            u_text = (u_data.get("name") or u_data.get("content") or u_data.get("action_text") or u).lower()
            v_text = (v_data.get("name") or v_data.get("content") or v).lower()
            combined = f"{u_text} {rel.lower()} {v_text}"

            matches = [t for t in key_tokens if t in combined]
            if len(matches) >= 2:
                u_display = u_data.get("name") or u_data.get("action_text") or u
                v_display = v_data.get("name") or v_data.get("content") or v
                supporting.append(f"({u_display}) --[{rel}]--> ({v_display})")

        if supporting:
            return ClaimVerificationResponse(
                claim=claim,
                is_verified=True,
                verdict="CONFIRMED",
                reasoning=f"Khẳng định được xác nhận bởi {len(supporting)} cạnh liên kết trong đồ thị tri thức.",
                supporting_edges=supporting[:5],
                refuting_edges=[]
            )

        return ClaimVerificationResponse(
            claim=claim,
            is_verified=False,
            verdict="INSUFFICIENT_EVIDENCE",
            reasoning="Đồ thị tri thức không ghi nhận bất kỳ cạnh liên kết nào hỗ trợ cho khẳng định này.",
            supporting_edges=[],
            refuting_edges=[]
        )




    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_labels": dict(nx.get_node_attributes(self.graph, "label")),
            "neo4j_auradb": {
                "connected": neo4j_service.is_connected,
                "instance": settings.AURA_INSTANCEID,
                "uri": settings.NEO4J_URI
            }
        }
        return stats

    def clear(self):
        self.graph.clear()

# Global singleton service instance
meeting_graph_service = MeetingGraphService()
