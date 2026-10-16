import os
import sys
import json

# Cấu hình UTF-8 console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.database import SessionLocal, init_db, SQLITE_FILE_PATH
from src.db.repository import MeetingRepository
from src.schemas.meeting import MeetingInput
from src.services.pipeline_service import pipeline_service

def test_sqlite_persistence():
    print("=" * 75)
    print("KIỂM THỬ KHỞI TẠO VÀ LƯU TRỮ CƠ SỞ DỮ LIỆU SQLITE")
    print("=" * 75)

    # 1. Khởi tạo DB & kiểm tra file
    init_db()
    print(f"\n1. Vị trí file SQLite: {SQLITE_FILE_PATH}")
    print(f"   • File tồn tại: {os.path.exists(SQLITE_FILE_PATH)}")
    print(f"   • Kích thước: {os.path.getsize(SQLITE_FILE_PATH)} bytes")

    # 2. Xử lý và lưu một cuộc họp vào SQLite
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json"))
    with open(data_path, "r", encoding="utf-8") as f:
        suite = json.load(f)
    tc01_meeting = suite["test_cases"][0]["meeting"]

    print(f"\n2. Đang nạp cuộc họp [{tc01_meeting['meeting_id']}] qua Pipeline & lưu SQLite...")
    meeting_input = MeetingInput(**tc01_meeting)
    result = pipeline_service.process_meeting(meeting_input, reset_previous=True)

    db = SessionLocal()
    try:
        meeting_db = MeetingRepository.save_meeting_result(db, meeting_input, result)
        print(f"   • Đã lưu thành công Meeting: [{meeting_db.meeting_id}] - {meeting_db.title}")

        # 3. Đọc dữ liệu từ SQLite
        print(f"\n3. Truy vấn các bảng trong SQLite Database:")
        
        meetings = MeetingRepository.list_meetings(db)
        print(f"   • Bảng 'meetings': {len(meetings)} dòng")
        for m in meetings:
            print(f"     - ID: {m.meeting_id} | Ngày: {m.meeting_date} | Thành viên: {m.participants}")

        decisions = MeetingRepository.list_decisions(db)
        print(f"   • Bảng 'decisions': {len(decisions)} dòng")
        for d in decisions:
            print(f"     - [{d.decision_id}] {d.content} | Status: {d.status} | Final Active: {d.is_final_active}")

        actions = MeetingRepository.list_actions(db)
        print(f"   • Bảng 'action_items': {len(actions)} dòng")
        for a in actions:
            print(f"     - [{a.action_id}] {a.action_text} | Assignee: {a.assignee_name} | Deadline: {a.deadline_raw}")

        issues = MeetingRepository.list_issues(db)
        print(f"   • Bảng 'issues': {len(issues)} dòng")
        for i in issues:
            print(f"     - [{i.issue_id}] {i.title}: {i.description}")

    finally:
        db.close()

    print("\n" + "=" * 75)
    print("HOÀN TẤT: CƠ SỞ DỮ LIỆU SQLITE ĐÃ ĐƯỢC KHỞI TẠO VÀ LƯU TRỮ THÀNH CÔNG 100%!")
    print("=" * 75)

if __name__ == "__main__":
    test_sqlite_persistence()
