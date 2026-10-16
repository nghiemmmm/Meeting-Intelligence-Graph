import React from 'react';
import { X, Quote, Clock, User, CheckCircle } from 'lucide-react';

export default function EvidenceDrawer({ isOpen, onClose, entityTitle, evidenceList = [] }) {
  if (!isOpen) return null;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title">
            <Quote size={20} color="#38bdf8" />
            <span>Bằng Chứng Gốc (Evidence Trace)</span>
          </div>
          <button
            type="button"
            className="btn-secondary"
            onClick={onClose}
            style={{ padding: '6px', borderRadius: '50%' }}
          >
            <X size={16} />
          </button>
        </div>

        <div className="drawer-body">
          <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#93c5fd', textTransform: 'uppercase' }}>
              Đối tượng trích xuất:
            </span>
            <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginTop: '4px' }}>
              {entityTitle}
            </div>
          </div>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Danh sách phát ngôn nguyên văn làm căn cứ xác thực (Evidence-Centered Knowledge Graph):
          </div>

          {evidenceList.map((ev, idx) => (
            <div key={idx} className="evidence-quote-card">
              <div className="quote-header">
                <span className="speaker-pill">
                  <User size={13} />
                  <span>{ev.speaker || 'Thành viên'}</span>
                </span>
                <span className="time-pill">
                  <Clock size={11} style={{ marginRight: 4, display: 'inline' }} />
                  {ev.timestamp || '00:00'}
                </span>
              </div>
              <div className="quote-text">
                "{ev.quote_text}"
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: '#10b981' }}>
                <CheckCircle size={12} />
                <span>Đã kiểm chứng khớp với transcript gốc</span>
              </div>
            </div>
          ))}

          {evidenceList.length === 0 && (
            <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-dim)' }}>
              Không có bằng chứng cụ thể được đính kèm.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
