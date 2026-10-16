# BÁO CÁO KẾT QUẢ KIỂM THỬ MISSION 2 — MEETING INTELLIGENCE ASSISTANT

> **Mục tiêu**: Chứng minh phần quan trọng nhất của giải pháp (Core Loop: Transcript → Diễn biến → Cấu trúc 5 nhóm → Bằng chứng Evidence & Quan hệ SUPERSEDES) thực sự hoạt động trên 05 tình huống thực chiến.

| STT | Tình huống kiểm thử | Phân loại | Kết quả |
| :--- | :--- | :--- | :--- |
| **TC-01** | Case 1: Đổi phương án kiến trúc & giữ đúng kết luận cuối (Happy Path & Superseding) | `SUCCESS_STABLE` | **ĐẠT (PASS)** |
| **TC-02** | Case 2: Giao việc đa nhiệm & Khôi phục ngữ cảnh khuyết DUR | `SUCCESS_STABLE` | **ĐẠT (PASS)** |
| **TC-03** | Case 3: Dữ liệu không rõ ràng & Null-Safety & Nội dung chưa chốt | `EDGE_UNRESOLVED` | **ĐẠT (PASS)** |
| **TC-04** | Case 4: Ngôn từ không chính thức, nói đùa và yêu cầu bắt buộc từ khách hàng | `COMPLEX_OBJECTION` | **ĐẠT (PASS)** |
| **TC-05** | Case 5: Giao tiếp phân mảnh, ngắt lời và code-switching kỹ thuật sâu (Failure Case) | `FAILURE_ANALYSIS` | **ĐẠT ĐÚNG GIẢ THUYẾT THẤT BẠI (IDENTIFIED LIMITATION)** |

---

## TC-01: Case 1: Đổi phương án kiến trúc & giữ đúng kết luận cuối (Happy Path & Superseding)

- **Phân loại**: `SUCCESS_STABLE`
- **Kỳ vọng (Expectation)**:
  > Quyết định chốt: PostgreSQL (is_final_active=True). Phương án cũ bị thay thế: MongoDB (SUPERSEDES). Phát hiện vướng mắc ACID và giao An trước thứ Sáu.

- **Kết quả thực tế (Actual Result)**:
  > Chốt: Chốt lựa chọn phương án: PostgreSQL (active=1). SUPERSEDES: 2 phương án. Issues ghi nhận: 1 (Thiếu hỗ trợ ACID transaction). Task: An - trước thứ Sáu.

- **Đánh giá**: **ĐẠT (PASS)**

- **Điều học được (Lesson Learned)**:
  Cơ chế Event Sourcing và cạnh SUPERSEDES trong Knowledge Graph giúp hệ thống loại bỏ phương án MongoDB cũ mà không làm mất lịch sử thảo luận gốc.

---

## TC-02: Case 2: Giao việc đa nhiệm & Khôi phục ngữ cảnh khuyết DUR

- **Phân loại**: `SUCCESS_STABLE`
- **Kỳ vọng (Expectation)**:
  > Trích xuất 2 Action Items: 1 cho Bình (deadline ngày mai), 1 cho Cường (deadline cuối tuần), áp dụng DUR câu hoàn chỉnh.

- **Kết quả thực tế (Actual Result)**:
  > Trích xuất 2 tasks. Người nhận: ['Bình', 'Cường']. Deadlines: ['trước ngày mai', 'trước cuối tuần này'].

- **Đánh giá**: **ĐẠT (PASS)**

- **Điều học được (Lesson Learned)**:
  Kỹ thuật De-contextualization (DUR) giúp tái tạo câu hành động độc lập, không bị lẫn lộn giữa nhiều người nhận việc trong cùng cuộc họp.

---

## TC-03: Case 3: Dữ liệu không rõ ràng & Null-Safety & Nội dung chưa chốt

- **Phân loại**: `EDGE_UNRESOLVED`
- **Kỳ vọng (Expectation)**:
  > Ghi nhận Feedback khách hàng timeout. Không chốt quyết định vội vàng mà lưu vào UnresolvedTopic. Áp dụng Null-Safety cho câu giao việc mơ hồ (assignee=null, deadline=null).

- **Kết quả thực tế (Actual Result)**:
  > Requirements/Feedbacks: 1. Unresolved Topics: 1. Null-Safety đảm bảo: True.

- **Đánh giá**: **ĐẠT (PASS)**

- **Điều học được (Lesson Learned)**:
  Null-Safety ngăn chặn ảo giác (hallucination) nghiêm ngặt khi người nói phát biểu bâng quơ không chỉ định người làm hoặc thời hạn cụ thể.

---

## TC-04: Case 4: Ngôn từ không chính thức, nói đùa và yêu cầu bắt buộc từ khách hàng

- **Phân loại**: `COMPLEX_OBJECTION`
- **Kỳ vọng (Expectation)**:
  > Bỏ qua câu nói đùa Rust, nhận diện Requirement bắt buộc của khách hàng về React, chốt quyết định React và giao Dũng hoàn thành trước 17h.

- **Kết quả thực tế (Actual Result)**:
  > Chốt: Chốt lựa chọn phương án: React. Ghi nhận Requirement: True. Phân công: Dũng - trước 17h ngày mai.

- **Đánh giá**: **ĐẠT (PASS)**

- **Điều học được (Lesson Learned)**:
  Phân biệt giữa ý kiến cá nhân/nói đùa và ràng buộc bắt buộc từ khách hàng (Requirement) là yếu tố sống còn để trích xuất dữ liệu chuẩn.

---

## TC-05: Case 5: Giao tiếp phân mảnh, ngắt lời và code-switching kỹ thuật sâu (Failure Case)

- **Phân loại**: `FAILURE_ANALYSIS`
- **Kỳ vọng (Expectation)**:
  > Hệ thống cần hiểu câu 'cứ triển khai hướng đấy đi' là giao việc tune JVM flag cho ai đó. Tuy nhiên, do ngữ cảnh ngắt vụn và overlapping speech, dự kiến trích xuất sẽ gặp khó khăn hoặc thiếu trọn vẹn thông tin.

- **Kết quả thực tế (Actual Result)**:
  > Trích xuất được 1 action item ('Uhm thế thì cứ triển khai hướng đấy đi.' - thiếu chủ ngữ rõ ràng và deadline 'giữa tháng sau' chưa chuẩn hóa ISO).

- **Đánh giá**: **ĐẠT ĐÚNG GIẢ THUYẾT THẤT BẠI (IDENTIFIED LIMITATION)**

- **Điều học được (Lesson Learned)**:
  Hạn chế thực tế: Với hội thoại ngắt lời (overlapping) và câu khuyết tân ngữ nặng, chỉ dùng Text Heuristic/Rule hoặc LLM không đủ ngữ cảnh âm thanh sẽ không khôi phục được đầy đủ nghĩa. Cần tích hợp Audio Speaker Diarization và mô hình Incomplete Utterance Restoration chuyên biệt.

---

