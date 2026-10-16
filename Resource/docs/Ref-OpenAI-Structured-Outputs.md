# Nghiên Cứu Tham Chiếu: OpenAI Structured Model Outputs

Tài liệu này tổng hợp và phân tích chi tiết tính năng **Structured Model Outputs (Đầu ra mô hình có cấu trúc)** của OpenAI, đóng vai trò là cơ sở kỹ thuật bảo đảm an toàn kiểu dữ liệu (*Type-Safety*) và chống ảo giác (*Zero-Hallucination*) cho hệ thống Trợ lý Cuộc họp AI.

---

## 1. Tổng Quan Về Structured Outputs

* **Định nghĩa:** Đây là tính năng đảm bảo mô hình LLM luôn tạo ra phản hồi tuân thủ tuyệt đối $100\%$ theo JSON Schema do lập trình viên định nghĩa trước.
* **Vấn đề giải quyết:** Khắc phục triệt để tình trạng mô hình bỏ quên các trường bắt buộc (*missing required keys*), sinh ra các giá trị enum không hợp lệ, hoặc trả về cú pháp JSON sai lệch.

### Lợi ích cốt lõi:
1. **Độ an toàn kiểu dữ liệu (Type-Safety):** Không cần viết các vòng lặp retry hoặc code validate phức tạp khi phản hồi bị lỗi định dạng.
2. **Từ chối rõ ràng (Explicit Refusals):** Khi gặp nội dung vi phạm chính sách an toàn, mô hình trả về trường `refusal` có thể bắt được bằng lập trình thay vì ngắt đột ngột.
3. **Đơn giản hóa câu lệnh (Prompt Simplification):** Không cần viết prompt quá dài dòng chỉ để "năn nỉ" hay ép mô hình trả về đúng định dạng.

---

## 2. Hai Hình Thức Sử Dụng Chính

| Hình thức | Khi nào nên sử dụng? | Ví dụ điển hình |
| :--- | :--- | :--- |
| **Function Calling** | Khi bạn muốn kết nối mô hình với các công cụ ngoài, cơ sở dữ liệu, API hoặc chức năng hệ thống. | Trợ lý AI tra cứu DB khách hàng, gọi API Jira/Trello để tạo ticket. |
| **Response Format (`json_schema`)** | Khi bạn muốn cấu trúc hóa trực tiếp câu trả lời của mô hình khi nó phản hồi lại người dùng hoặc hệ thống tiếp theo. | Bóc tách Action Item, phân loại Intent, tạo schema JSON từ transcript cuộc họp. |

---

## 3. So Sánh: Structured Outputs vs. JSON Mode Cũ

| Tiêu chí | JSON Mode (Cũ) | Structured Outputs (Mới) |
| :--- | :--- | :--- |
| **Cú pháp JSON** | Đảm bảo là JSON hợp lệ cú pháp. | Đảm bảo là JSON hợp lệ cú pháp. |
| **Tuân thủ Schema** | **Không đảm bảo:** Có thể thiếu key hoặc sai enum. | **Tuyệt đối 100%:** Tuân thủ từng trường, từng kiểu dữ liệu. |
| **Prompt Requirement** | Bắt buộc phải có từ khóa *"JSON"* trong prompt. | Không bắt buộc, định nghĩa thông qua tham số API. |
| **Độ tin cậy cho Production** | Trung bình (vẫn cần Pydantic parse & retry). | **Rất cao (Production-ready).** |

> **Khuyến nghị:** Luôn ưu tiên dùng **Structured Outputs** (`strict: true`) thay cho JSON Mode khi sử dụng các mô hình hỗ trợ (`gpt-4o-mini`, `gpt-4o-2024-08-06` trở lên hoặc Gemini Structured Schema).

---

## 4. Các Quy Tắc & Giới Hạn Kỹ Thuật Quan Trọng

Khi xây dựng JSON Schema cho Structured Outputs, hệ thống áp đặt các ràng buộc khắt khe để bảo đảm tính tất định:
* **Bắt buộc `additionalProperties: false`:** Mọi đối tượng (*object*) phải khóa các thuộc tính phụ không được định nghĩa trước.
* **Tất cả các trường phải nằm trong `required`:** Muốn làm trường tùy chọn (*optional*), phải định nghĩa kiểu hợp (*union*) với `null` (ví dụ: `{"type": ["string", "null"]}`).
* **Cấu trúc gốc (Root object):** Root của schema bắt buộc phải là kiểu `object`, không được dùng `anyOf` ở cấp cao nhất.

### Giới hạn kích thước (Schema Limits):
* Tối đa **5.000 thuộc tính object** và tối đa **10 cấp độ lồng nhau** (*nesting depth*).
* Tổng độ dài chuỗi tên thuộc tính, mô tả, enum không vượt quá **120.000 ký tự**.
* Tối đa **1.000 giá trị enum** trên toàn bộ schema.
* **Hỗ trợ đệ quy (Recursive schemas):** Cho phép mô hình hóa các cấu trúc cây, danh sách liên kết hoặc UI phân cấp thông qua tham chiếu `$ref`.

---

## 5. Xử Lý Ngoại Lệ & Kỹ Thuật Nâng Cao

* **Xử lý từ chối (Refusals):** Kiểm tra `item.type == "refusal"` trong code để hiển thị thông báo thân thiện khi nội dung bị chặn an toàn.
* **Streaming có cấu trúc:** Hỗ trợ parse JSON từng phần ngay trong lúc mô hình đang tạo ra phản hồi (*real-time stream*), giúp tăng tốc trải nghiệm người dùng (UX) trong các ứng dụng thời gian thực.

---

## 6. Ứng Dụng Vào Dự Án Trí Tuệ Cuộc Họp

Trong hệ thống **Meeting Intelligence Assistant**, tính năng này được ứng dụng ở các khâu cốt tử:
1. **Trích xuất Semantic Intent:** Ép LLM trả về đúng 7 nhóm Intent và các tham số `assignee`, `deadline`, `action`.
2. **Bảo toàn Null-safety:** Quy định `deadline.value` và `assignee` là nullable (`type: ["string", "null"]`), ngăn chặn $100\%$ nguy cơ LLM tự bịa thời hạn hoặc người phụ trách khi cuộc họp chưa chốt.
3. **Trích xuất Đồ thị (Graph Nodes & Edges):** Trích xuất trực tiếp danh sách các cạnh quan hệ (`IMPLEMENTS`, `SUPERSEDES`, `MOTIVATED_BY`) nạp vào Neo4j.