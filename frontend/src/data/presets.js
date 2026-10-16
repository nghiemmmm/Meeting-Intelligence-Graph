export const TEST_CASES = [
  {
    id: "TC-01",
    tag: "Đổi phương án (SUPERSEDES)",
    name: "Case 1: Đổi phương án kiến trúc & giữ đúng kết luận cuối",
    badgeType: "success",
    description: "Đầu họp đề xuất MongoDB, giữa họp phản biện về ACID, cuối họp chốt PostgreSQL và giao việc cho An.",
    meeting: {
      meeting_id: "MTG-TC01",
      title: "Lựa chọn cơ sở dữ liệu cho hệ thống thanh toán",
      meeting_date: "2026-10-14",
      participants: ["An", "Bình", "Team Lead"],
      transcript: [
        { utterance_id: "UTT-01", speaker_name: "An", timestamp: "09:00", text: "Chào mọi người. Tôi đề xuất dùng MongoDB vì nó hỗ trợ lưu tài liệu JSON rất linh hoạt và tiện mở rộng." },
        { utterance_id: "UTT-02", speaker_name: "Bình", timestamp: "09:05", text: "Tôi lo ngại phương án này. Hệ thống thanh toán yêu cầu ràng buộc giao dịch chặt chẽ, MongoDB thiếu hỗ trợ ACID transaction mạnh mẽ, có thể dẫn đến rủi ro sai lệch số dư." },
        { utterance_id: "UTT-03", speaker_name: "Team Lead", timestamp: "09:15", text: "Bình nói rất đúng. Để an toàn cho dữ liệu tài chính, chúng ta chốt lựa chọn PostgreSQL cho hệ thống." },
        { utterance_id: "UTT-04", speaker_name: "Team Lead", timestamp: "09:18", text: "Giao cho An tích hợp PostgreSQL vào source code và gửi link test trước thứ Sáu nhé." },
        { utterance_id: "UTT-05", speaker_name: "An", timestamp: "09:20", text: "Vâng, tôi đã rõ và sẽ hoàn thành trước thứ Sáu." }
      ]
    }
  },
  {
    id: "TC-02",
    tag: "Đa nhiệm & DUR",
    name: "Case 2: Giao việc đa nhiệm & Khôi phục ngữ cảnh khuyết DUR",
    badgeType: "primary",
    description: "Sprint planning giao 2 nhiệm vụ độc lập cho Bình và Cường với deadline cụ thể, phục hồi câu văn khuyết ngữ cảnh.",
    meeting: {
      meeting_id: "MTG-TC02",
      title: "Họp phân công công việc Sprint 24",
      meeting_date: "2026-10-14",
      participants: ["Team Lead", "Bình", "Cường"],
      transcript: [
        { utterance_id: "UTT-10", speaker_name: "Team Lead", timestamp: "10:00", text: "Hôm nay chúng ta chốt danh sách công việc quan trọng cho Sprint." },
        { utterance_id: "UTT-11", speaker_name: "Team Lead", timestamp: "10:02", text: "Ai phụ trách viết unit test cho API xác thực người dùng?" },
        { utterance_id: "UTT-12", speaker_name: "Bình", timestamp: "10:04", text: "Tôi sẽ phụ trách viết bộ unit test đó và đẩy lên repo trước ngày mai." },
        { utterance_id: "UTT-13", speaker_name: "Team Lead", timestamp: "10:06", text: "Tốt. Còn phần tối ưu hóa giao diện trang chủ thì sao?" },
        { utterance_id: "UTT-14", speaker_name: "Cường", timestamp: "10:08", text: "Giao cho tôi. Tôi sẽ hoàn thành việc tối ưu hóa giao diện trang chủ trước cuối tuần này." }
      ]
    }
  },
  {
    id: "TC-03",
    tag: "Chưa chốt & Null-Safety",
    name: "Case 3: Dữ liệu không rõ ràng & Null-Safety & Chưa chốt",
    badgeType: "warning",
    description: "Tranh luận gay gắt chưa ngã ngũ, ghi nhận feedback khách hàng và giao việc mơ hồ không người làm (Null-Safety).",
    meeting: {
      meeting_id: "MTG-TC03",
      title: "Họp xử lý sự cố hạ tầng và feedback khách hàng",
      meeting_date: "2026-10-14",
      participants: ["Giám đốc", "Kỹ sư trưởng", "Dũng"],
      transcript: [
        { utterance_id: "UTT-20", speaker_name: "Giám đốc", timestamp: "14:00", text: "Khách hàng phản ánh hệ thống thường xuyên bị timeout lúc 12h trưa giờ cao điểm." },
        { utterance_id: "UTT-21", speaker_name: "Kỹ sư trưởng", timestamp: "14:05", text: "Chúng ta có hai hướng: một là nâng RAM máy chủ hiện tại, hai là chuyển toàn bộ sang cụm Kubernetes đa vùng." },
        { utterance_id: "UTT-22", speaker_name: "Dũng", timestamp: "14:10", text: "Nâng RAM thì nhanh nhưng tạm bợ, còn Kubernetes thì tốn nhiều tháng triển khai." },
        { utterance_id: "UTT-23", speaker_name: "Giám đốc", timestamp: "14:15", text: "Vấn đề này chưa chốt được hôm nay, để họp sau khi có báo giá chi tiết, hiện tại còn phân vân lắm." },
        { utterance_id: "UTT-24", speaker_name: "Kỹ sư trưởng", timestamp: "14:18", text: "Cứ chuẩn bị tài liệu kỹ thuật so sánh trước đi." }
      ]
    }
  },
  {
    id: "TC-04",
    tag: "Lọc câu đùa & Yêu cầu khách",
    name: "Case 4: Ngôn từ không chính thức & Yêu cầu bắt buộc",
    badgeType: "purple",
    description: "Nói đùa đập đi xây lại bằng Rust, đề xuất Vue nhưng khách hàng bắt buộc React, chốt React.",
    meeting: {
      meeting_id: "MTG-TC04",
      title: "Lựa chọn Framework Frontend cho Cổng thông tin",
      meeting_date: "2026-10-14",
      participants: ["Dũng", "An", "Team Lead"],
      transcript: [
        { utterance_id: "UTT-30", speaker_name: "Dũng", timestamp: "15:00", text: "Hay là mình đập đi viết lại toàn bộ bằng Rust đi haha, cho nó chạy siêu nhanh." },
        { utterance_id: "UTT-31", speaker_name: "An", timestamp: "15:02", text: "Đừng đùa nữa Dũng. Tôi đề xuất dùng Vue vì làm rất nhanh." },
        { utterance_id: "UTT-32", speaker_name: "Team Lead", timestamp: "15:05", text: "Không được. Khách hàng yêu cầu bắt buộc giao diện phải dùng React vì đội ngũ của họ chỉ có chuyên gia React." },
        { utterance_id: "UTT-33", speaker_name: "Team Lead", timestamp: "15:08", text: "Vậy chúng ta chốt dùng React nhé. Giao cho Dũng dựng skeleton trước 17h ngày mai." },
        { utterance_id: "UTT-34", speaker_name: "Dũng", timestamp: "15:10", text: "Ok anh, tôi nhận task dựng khung React." }
      ]
    }
  },
  {
    id: "TC-05",
    tag: "Phân mảnh (Failure Analysis)",
    name: "Case 5: Giao tiếp phân mảnh, ngắt lời & code-switching",
    badgeType: "danger",
    description: "Hội thoại ngắt quãng, nói chồng chéo, khuyết tân ngữ nặng nề và thuật ngữ JVM.",
    meeting: {
      meeting_id: "MTG-TC05",
      title: "Khắc phục sự cố tắc nghẽn RPC Shard",
      meeting_date: "2026-10-14",
      participants: ["Tuấn", "Hoa"],
      transcript: [
        { utterance_id: "UTT-40", speaker_name: "Tuấn", timestamp: "16:00", text: "Cái RPC latency đợt này bị spike dữ dội do GC pause bên cụm worker..." },
        { utterance_id: "UTT-41", speaker_name: "Hoa", timestamp: "16:01", text: "Ủa nhưng mà bên shard 3 nó..." },
        { utterance_id: "UTT-42", speaker_name: "Tuấn", timestamp: "16:02", text: "...thế nên chắc là cứ theo hướng tune JVM flag hoặc re-partition lại shard." },
        { utterance_id: "UTT-43", speaker_name: "Hoa", timestamp: "16:03", text: "Uhm thế thì cứ triển khai hướng đấy đi." },
        { utterance_id: "UTT-44", speaker_name: "Tuấn", timestamp: "16:04", text: "Hạn chót thì tầm giữa tháng sau nhé." }
      ]
    }
  }
];
