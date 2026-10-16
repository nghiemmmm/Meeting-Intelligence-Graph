import logging
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase, Driver
from src.config import settings

logger = logging.getLogger("neo4j_service")

class Neo4jService:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
        self._driver: Optional[Driver] = None
        self._is_connected = False
        
        self.connect()

    def connect(self) -> bool:
        """Khởi tạo kết nối đến Neo4j AuraDB và thiết lập ràng buộc schema"""
        if not self.uri or not self.password:
            logger.warning("[Neo4j] Chưa cấu hình NEO4J_URI hoặc NEO4J_PASSWORD trong .env.")
            self._is_connected = False
            return False

        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_lifetime=30 * 60,
                max_connection_pool_size=50
            )
            self._driver.verify_connectivity()
            self._is_connected = True
            logger.info(f"[Neo4j] Kết nối thành công đến AuraDB: {self.uri}")
            self.init_schema_constraints()
            return True
        except Exception as e:
            logger.error(f"[Neo4j Error] Không thể kết nối đến Neo4j AuraDB: {e}")
            self._is_connected = False
            return False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def close(self):
        if self._driver:
            self._driver.close()

    def init_schema_constraints(self):
        """Khởi tạo các Unique Constraint trên thuộc tính id cho các nhãn node chính"""
        labels = [
            "Meeting", "Participant", "Decision", "ActionItem", 
            "Issue", "Evidence", "UnresolvedTopic", "Requirement", "Feedback"
        ]
        with self._driver.session(database=self.database) as session:
            for label in labels:
                query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE"
                try:
                    session.run(query)
                except Exception as e:
                    logger.debug(f"[Neo4j] Constraint notice cho {label}: {e}")

    def save_node(self, node_id: str, label: str, properties: Dict[str, Any] = None):
        """Lưu hoặc cập nhật node trên Neo4j AuraDB bằng MERGE"""
        if not self._is_connected:
            return
        
        props = properties.copy() if properties else {}
        props["id"] = node_id
        # Loại bỏ các giá trị None để tránh lỗi Cypher
        clean_props = {k: v for k, v in props.items() if v is not None}

        # Sử dụng tham số Cypher an toàn
        query = f"""
        MERGE (n:{label} {{id: $node_id}})
        SET n += $props
        """
        try:
            with self._driver.session(database=self.database) as session:
                session.run(query, node_id=node_id, props=clean_props)
        except Exception as e:
            logger.error(f"[Neo4j Error] save_node ({label}:{node_id}): {e}")

    def save_edge(self, source_id: str, target_id: str, relation: str, properties: Dict[str, Any] = None):
        """Lưu hoặc cập nhật quan hệ (cạnh) giữa 2 node trên Neo4j AuraDB"""
        if not self._is_connected:
            return

        clean_props = {k: v for k, v in (properties or {}).items() if v is not None}
        
        # Match theo id của bất kỳ nhãn nào
        query = f"""
        MATCH (s {{id: $source_id}})
        MATCH (t {{id: $target_id}})
        MERGE (s)-[r:{relation}]->(t)
        SET r += $props
        """
        try:
            with self._driver.session(database=self.database) as session:
                session.run(query, source_id=source_id, target_id=target_id, props=clean_props)
        except Exception as e:
            logger.error(f"[Neo4j Error] save_edge ({source_id} -[:{relation}]-> {target_id}): {e}")

    def sync_from_networkx(self, nx_graph):
        """Đồng bộ toàn bộ đồ thị NetworkX lên Neo4j AuraDB"""
        if not self._is_connected:
            logger.warning("[Neo4j] Chưa kết nối được AuraDB, bỏ qua bước đồng bộ.")
            return

        logger.info(f"[Neo4j] Bắt đầu đồng bộ {nx_graph.number_of_nodes()} nodes và {nx_graph.number_of_edges()} edges lên AuraDB...")
        
        with self._driver.session(database=self.database) as session:
            # 1. Đồng bộ Nodes
            for node_id, data in nx_graph.nodes(data=True):
                label = data.get("label", "Entity")
                props = {k: v for k, v in data.items() if k != "label" and v is not None}
                props["id"] = node_id
                
                query = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
                session.run(query, id=node_id, props=props)

            # 2. Đồng bộ Edges
            for u, v, k, data in nx_graph.edges(keys=True, data=True):
                relation = data.get("relation", k)
                props = {pk: pv for pk, pv in data.items() if pk != "relation" and pv is not None}
                
                query = f"""
                MATCH (s {{id: $u}})
                MATCH (t {{id: $v}})
                MERGE (s)-[r:{relation}]->(t)
                SET r += $props
                """
                session.run(query, u=u, v=v, props=props)

        logger.info("[Neo4j] Đồng bộ thành công lên Neo4j AuraDB!")

    def execute_cypher(self, cypher: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Thực thi câu truy vấn Cypher tùy ý và trả về danh sách kết quả"""
        if not self._is_connected:
            return []
        
        try:
            with self._driver.session(database=self.database) as session:
                result = session.run(cypher, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"[Neo4j Cypher Error]: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Lấy số lượng node và quan hệ trực tiếp từ Neo4j AuraDB"""
        if not self._is_connected:
            return {"status": "DISCONNECTED", "nodes": 0, "relationships": 0}

        try:
            with self._driver.session(database=self.database) as session:
                node_res = session.run("MATCH (n) RETURN count(n) AS node_count").single()
                rel_res = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count").single()
                labels_res = session.run("CALL db.labels() YIELD label RETURN collect(label) AS labels").single()
                rel_types_res = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types").single()

                return {
                    "status": "CONNECTED",
                    "uri": self.uri,
                    "database": self.database,
                    "nodes": node_res["node_count"] if node_res else 0,
                    "relationships": rel_res["rel_count"] if rel_res else 0,
                    "labels": labels_res["labels"] if labels_res else [],
                    "relationship_types": rel_types_res["types"] if rel_types_res else []
                }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def clear_database(self):
        """Xóa toàn bộ nodes và relationships trên Neo4j AuraDB (Cẩn trọng)"""
        if not self._is_connected:
            return
        with self._driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("[Neo4j] Đã xóa trắng toàn bộ dữ liệu trên AuraDB.")

neo4j_service = Neo4jService()
