import React from 'react';
import { Send, Loader2, RefreshCw, Calendar, Users, FileText, Sparkles } from 'lucide-react';

export default function TranscriptEditor({
  meetingTitle,
  setMeetingTitle,
  meetingDate,
  setMeetingDate,
  participants,
  setParticipants,
  transcriptText,
  setTranscriptText,
  onProcess,
  loading,
  onReset
}) {
  return (
    <div className="input-panel">
      <div className="panel-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={17} color="#60a5fa" />
          <span>Biên Bản Hội Thoại Đầu Vào</span>
        </span>
        <button
          type="button"
          className="btn-secondary"
          onClick={onReset}
          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
          title="Xóa để nhập mới"
        >
          <RefreshCw size={12} />
          <span>Làm mới</span>
        </button>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Tiêu đề cuộc họp</span>
        </label>
        <input
          type="text"
          className="form-input"
          value={meetingTitle}
          onChange={(e) => setMeetingTitle(e.target.value)}
          placeholder="Ví dụ: Họp Kiến Trúc Backend..."
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div className="form-group">
          <label className="form-label">
            <Calendar size={13} />
            <span>Ngày họp</span>
          </label>
          <input
            type="date"
            className="form-input"
            value={meetingDate}
            onChange={(e) => setMeetingDate(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">
            <Users size={13} />
            <span>Người tham gia</span>
          </label>
          <input
            type="text"
            className="form-input"
            value={participants}
            onChange={(e) => setParticipants(e.target.value)}
            placeholder="An, Bình, Lead..."
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" style={{ justifyContent: 'space-between' }}>
          <span>Nội dung Transcript</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            [hh:mm] Tên: Nội dung
          </span>
        </label>
        <textarea
          className="form-textarea"
          value={transcriptText}
          onChange={(e) => setTranscriptText(e.target.value)}
          placeholder={`[09:00] An: Tôi đề xuất dùng MongoDB...\n[09:05] Bình: Tôi lo ngại MongoDB thiếu ACID transaction...\n[09:15] Team Lead: Chúng ta chốt PostgreSQL...`}
          rows={9}
        />
      </div>

      <button
        type="button"
        className="btn-primary"
        onClick={onProcess}
        disabled={loading || !transcriptText.trim()}
      >
        {loading ? (
          <>
            <Loader2 size={17} className="spinner" />
            <span>Đang phân tích AI & Graph...</span>
          </>
        ) : (
          <>
            <Sparkles size={17} />
            <span>Phân Tích Cuộc Họp</span>
          </>
        )}
      </button>
    </div>
  );
}
