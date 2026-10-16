import React from 'react';
import { HelpCircle, Quote, ArrowRightCircle } from 'lucide-react';

export default function UnresolvedTab({ unresolvedTopics = [], onOpenEvidence }) {
  if (!unresolvedTopics.length) {
    return <div className="item-card"><p style={{ color: 'var(--text-muted)' }}>Tất cả các nội dung thảo luận đã được thống nhất, không có vấn đề bỏ ngỏ.</p></div>;
  }

  return (
    <div className="tab-content">
      {unresolvedTopics.map((item) => {
        return (
          <div key={item.topic_id} className="item-card" style={{ borderLeft: '4px solid var(--cyan)' }}>
            <div className="item-header">
              <div className="item-title-group">
                <span className="item-id">{item.topic_id} • Trạng thái: {item.status || 'UNRESOLVED'}</span>
                <h3 className="item-title" style={{ color: '#67e8f9' }}>{item.topic_name}</h3>
              </div>
              <div className="item-badges">
                <span className="badge" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee', border: '1px solid rgba(6, 182, 212, 0.4)' }}>
                  <HelpCircle size={13} />
                  CHƯA CHỐT KẾT LUẬN
                </span>
              </div>
            </div>

            {item.description && (
              <div style={{ fontSize: '0.9rem', color: '#e2e8f0' }}>
                {item.description}
              </div>
            )}

            {item.conflicting_views && item.conflicting_views.length > 0 && (
              <div style={{ background: 'rgba(0, 0, 0, 0.25)', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem' }}>
                <strong style={{ color: '#22d3ee' }}>Các luồng ý kiến xung đột:</strong>
                <ul style={{ paddingLeft: '20px', marginTop: '6px', color: 'var(--text-muted)' }}>
                  {item.conflicting_views.map((view, idx) => (
                    <li key={idx}>{view}</li>
                  ))}
                </ul>
              </div>
            )}

            {item.recommended_action && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem', color: '#a5f3fc' }}>
                <ArrowRightCircle size={15} />
                <span><strong>Đề xuất cho cuộc họp sau:</strong> {item.recommended_action}</span>
              </div>
            )}

            <div className="item-footer">
              <div className="item-meta-group">
                <span>Cần đưa vào Agenda tiếp theo</span>
              </div>

              {item.evidence_list && item.evidence_list.length > 0 && (
                <button
                  type="button"
                  className="evidence-btn"
                  onClick={() => onOpenEvidence(item.topic_name, item.evidence_list)}
                >
                  <Quote size={13} />
                  <span>Bằng chứng ({item.evidence_list.length})</span>
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
