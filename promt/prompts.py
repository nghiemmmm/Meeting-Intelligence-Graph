import os
from typing import Dict, Any, Optional

class PromptManager:
    """
    Quản lý tập trung các template prompt trong thư mục promt/.
    Hỗ trợ caching, nạp động từ file và format tham số.
    """
    def __init__(self, prompt_dir: Optional[str] = None):
        if prompt_dir is None:
            prompt_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompt_dir = prompt_dir
        self._cache: Dict[str, str] = {}

    def load_prompt_file(self, filename: str) -> str:
        """Đọc và cache file prompt từ ổ đĩa"""
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = os.path.join(self.prompt_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file prompt tại: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        self._cache[filename] = content
        return content

    def get_meeting_extraction_system(self) -> str:
        """Trả về system prompt bóc tách 5 nhóm dữ liệu theo chuẩn Structured Outputs"""
        return self.load_prompt_file("meeting_extraction_system.txt")

    def get_dur_restoration_prompt(self, context_history: str, current_utterance: str) -> str:
        """Trả về prompt khôi phục phát ngôn khuyết ngữ cảnh (DUR)"""
        template = self.load_prompt_file("dur_restoration.txt")
        return f"""{template}

[LỊCH SỬ PHÁT NGÔN LIỀN TRƯỚC]:
{context_history}

[CÂU PHÁT NGÔN HIỆN TẠI CẦN KHÔI PHỤC]:
{current_utterance}

Hãy tái tạo câu phát ngôn hiện tại thành câu tự thân hoàn chỉnh (Self-Contained Utterance) và trả về kết quả."""

    def get_text_to_cypher_prompt(self, question: str) -> str:
        """Trả về prompt chuyển đổi câu hỏi tự nhiên sang Cypher cho Neo4j"""
        template = self.load_prompt_file("text_to_cypher.txt")
        return f"""{template}

[CÂU HỎI CỦA NGƯỜI DÙNG]:
"{question}"

Hãy sinh câu lệnh Cypher duy nhất để truy vấn Neo4j trả lời câu hỏi trên. Chỉ trả về câu lệnh Cypher thuần túy, không kèm giải thích hoặc markdown block."""

    def get_graph_grounded_qa_prompt(self, question: str, subgraph_context: str) -> str:
        """Trả về prompt trả lời câu hỏi dựa trên bằng chứng đồ thị và trích dẫn"""
        template = self.load_prompt_file("graph_grounded_qa.txt")
        return f"""{template}

[CÂU HỎI CỦA NGƯỜI DÙNG]:
"{question}"

[DỮ LIỆU ĐỒ THỊ TRI THỨC (SUBGRAPH & RECORDS)]:
{subgraph_context}

Hãy tổng hợp câu trả lời theo đúng các nguyên tắc trên, nêu rõ chuỗi nhân quả và trích dẫn bằng chứng xác thực."""

    def get_entity_resolution_prompt(self, entity_type: str, entity_list: str) -> str:
        """Trả về prompt gom cụm và chuẩn hóa thực thể xuyên cuộc họp"""
        template = self.load_prompt_file("entity_resolution.txt")
        return template.format(entity_type=entity_type, entity_list=entity_list)

    def get_hub_node_profiling_prompt(self, name: str, etype: str, excerpts: str, relations: str) -> str:
        """Trả về prompt tổng hợp hồ sơ tri thức cho Hub Node (Giai đoạn 3)"""
        template = self.load_prompt_file("hub_node_profiling.txt")
        return template.format(name=name, etype=etype, excerpts=excerpts, relations=relations)

    def get_multihop_graph_qa_prompt(self, question: str, triples_and_citations: str) -> str:
        """Trả về prompt suy luận đa chặng trên Subgraph (Giai đoạn 4)"""
        template = self.load_prompt_file("multihop_graph_qa.txt")
        return template.format(question=question, triples_and_citations=triples_and_citations)

# Khởi tạo singleton instance
prompt_manager = PromptManager()


