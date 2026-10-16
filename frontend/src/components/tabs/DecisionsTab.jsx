import React from 'react';
import { CheckCircle2, RotateCcw, Quote, ArrowRight, Lightbulb } from 'lucide-react';

export default function DecisionsTab({ decisions = [], onOpenEvidence }) {
  if (!decisions.length) {
    return (
      <div className="item-card">
        <p style={{ color: 'var(--text-muted)' }}>Chưa có quyết định nào được ghi nhận.</p>
      </div>
    );
  }

  // Sort: Active final decisions first, superseded ones below
  const sorted = [...decisions].sort((a, b) => {
    if (a.is_final_active === b.is_final_active) return 0;
    return a.is_final_active ? -1 : 1;
  });

  return (
    <div className="tab-content">
      {sorted.map((item) => {
        const isFinal = item.is_final_active;
        const isSuperseded = item.status === 'SUPERSEDED' || !isFinal;

        return (
          <div
            key={item.decision_id}
            className={`item-card ${isFinal ? 'final-active' : 'superseded'}`}
          >
            <div className="item-header">
              <div className="item-title-group">
                <span className="item-id">{item.decision_id} • Chủ đề: {item.topic || 'Chung'}</span>
                <h3 className="item-title">{item.decision_text}</h3>
              </div>
              <div className="item-badges">
                {isFinal ? (
                  <span className="badge badge-success">
                    <CheckCircle2 size={13} />
                    Chốt có hiệu lực (Final Active)
                  </span>
                ) : (
                  <span className="badge badge-superseded">
                    <RotateCcw size={13} />
                    Đã bị thay thế (SUPERSEDED)
                  </span>
                )}
              </div>
            </div>

            {/* If this decision was superseded by another */}
            {isSuperseded && item.superseded_by && (
              <div className="supersede-callout">
                <ArrowRight size={14} />
                <span>
                  Đã bị thay thế bởi quyết định <strong>{item.superseded_by}</strong> theo diễn biến thảo luận cuối cuộc họp.
                </span>
              </div>
            )}

            {/* If this active decision supersedes an older one */}
            {isFinal && item.supersedes_decision_id && (
              <div className="supersede-callout" style={{ background: 'rgba(16, 185, 129, 0.1)', borderColor: 'rgba(16, 185, 129, 0.35)', color: '#6ee7b7' }}>
                <ArrowRight size={14} />
                <span>
                  Thay thế phương án trước đó (<strong>{item.supersedes_decision_id}</strong>) sau khi phản biện & thống nhất.
                </span>
              </div>
            )}

            {item.rationale && (
              <div style={{ fontSize: '0.86rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <Lightbulb size={13} color="#fbbf24" style={{ flexShrink: 0, transform: 'translateY(2px)' }} />
                <span>
                  <strong style={{ color: '#e2e8f0' }}>Lý do / Căn cứ:</strong> {item.rationale}
                </span>
              </div>
            )}

            <div className="item-footer">
              <div className="item-meta-group">
                <span>Trạng thái: <strong style={{ color: '#fff' }}>{item.status}</strong></span>
                {item.confidence_score && (
                  <span>Độ tin cậy: <strong style={{ color: '#34d399' }}>{Math.round(item.confidence_score * 100)}%</strong></span>
                )}
              </div>

              {item.evidence_list && item.evidence_list.length > 0 && (
                <button
                  type="button"
                  className="evidence-btn"
                  onClick={() => onOpenEvidence(item.decision_text, item.evidence_list)}
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
