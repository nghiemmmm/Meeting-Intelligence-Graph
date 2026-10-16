# HỆ THỐNG PROMPT ENGINE — TRÍ TUỆ CUỘC HỌP
Thư mục: `d:\GENTALENT\promt`

Hệ thống prompt được thiết kế chuyên biệt theo tiêu chuẩn **OpenAI Structured Outputs** (`strict: true`) và **Google Gemini Structured Schemas** (`response_schema`), tuân thủ các nguyên lý cốt lõi trong tài liệu nghiên cứu [Ref-OpenAI-Structured-Outputs.md](file:///d:/GENTALENT/Ref-OpenAI-Structured-Outputs.md).

---

## 1. NGUYÊN LÝ THIẾT KẾ: GIẢI PHÓNG CÂU PROMPT

Khi sử dụng tính năng Structured Outputs mới của OpenAI (`client.beta.chat.completions.parse`) hoặc Google Gemini (`response_schema`), mô hình AI được cưỡng bức ngữ pháp ($100\%$ Grammar-Constrained Sampling) bởi JSON Schema ở cấp engine.

Do đó:
* **KHÔNG CẦN:** Tốn token viết các câu dài dòng ép mô hình trả về đúng JSON, không cần nhắc nhở "Hãy trả về JSON hợp lệ" hoặc lặp lại cấu trúc các trường trong prompt.
* **TẬP TRUNG TOÀN BỘ:** Vào **năng lực suy luận ngữ nghĩa (Reasoning & Business Logic)**:
  1. **Quy tắc DUR (De-contextualization Utterance Restoration):** Tái tạo câu giao việc cụt ngủn thành câu tự thân hoàn chỉnh.
  2. **Quy tắc Temporal Shift (`SUPERSEDES`):** Nhận diện tiến trình thay đổi quyết định và phương án cũ bị thay thế.
  3. **Quy tắc Null-Safety:** Ép giá trị `null` khi câu nói bâng quơ, không có người làm hoặc hạn chót cụ thể.
  4. **Quy tắc Evidence-Grounding:** Ép buộc trích xuất nguyên văn `quote_text`, `speaker`, `timestamp`.
  5. **Quy tắc Lọc nhiễu & Tiếng cười:** Bỏ qua câu đùa cợt, nói giỡn và phân biệt rõ với Requirement bắt buộc của khách hàng.

---

## 2. CẤU TRÚC THƯ MỤC

| Tên tệp | Vai trò & Mục đích |
| :--- | :--- |
| `meeting_extraction_system.txt` | System prompt bóc tách 5 nhóm dữ liệu cốt lõi (Events, Decisions, Actions, Issues, Requirements, Unresolved Topics) |
| `dur_restoration.txt` | Prompt phục hồi phát ngôn khuyết ngữ cảnh (Incomplete Utterance Restoration - DUR) |
| `text_to_cypher.txt` | Prompt biên dịch câu hỏi tiếng Việt sang câu lệnh Cypher chuẩn trên Neo4j Graph Schema |
| `graph_grounded_qa.txt` | Prompt tổng hợp câu trả lời dựa trên đồ thị tri thức kèm cơ chế Abstention và trích dẫn bằng chứng |
| `prompts.py` | Python Module `PromptManager` nạp, cache và format template động |
| `README.md` | Tài liệu hướng dẫn sử dụng và đặc tả kỹ thuật |

---

## 3. CÁCH SỬ DỤNG TRONG CODE PYTHON

```python
from promt.prompts import prompt_manager

# 1. Lấy system prompt cho bóc tách cuộc họp
system_prompt = prompt_manager.get_meeting_extraction_system()

# 2. Tạo prompt khôi phục ngữ cảnh khuyết
dur_prompt = prompt_manager.get_dur_restoration_prompt(
    context_history="[09:10] An: Chúng ta cần điều chỉnh JVM flag -XX:+UseG1GC.",
    current_utterance="[09:12] Bình: Uhm thế thì cứ triển khai hướng đấy đi."
)

# 3. Tạo prompt Text-to-Cypher
cypher_prompt = prompt_manager.get_text_to_cypher_prompt(
    question="Vì sao nhóm quyết định chọn Giải pháp B thay vì PostgreSQL?"
)

# 4. Tạo prompt Graph-grounded QA
qa_prompt = prompt_manager.get_graph_grounded_qa_prompt(
    question="Ai chịu trách nhiệm nhiệm vụ ACT-001?",
    subgraph_context="(:ActionItem {id: 'ACT-001', assignee_name: 'An'})-[:IMPLEMENTS]->(:Decision {content: 'Giải pháp B'})"
)
```
