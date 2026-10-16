import React from 'react';
import { AlertTriangle, Quote } from 'lucide-react';

export default function IssuesTab({ issues = [], onOpenEvidence }) {
  if (!issues.length) {
    return <div className="item-card"><p style={{ color: 'var(--text-muted)' }}>Không phát hiện vướng mắc hay rủi ro nghiêm trọng nào.</p></div>;
  }

  return (
    <div className="tab-content">
      {issues.map((item) => {
        const severityClass = item.severity === 'HIGH' 
          ? 'badge-priority-high' 
          : item.severity === 'MEDIUM' 
            ? 'badge-priority-medium' 
            : 'badge-priority-low';

        return (
          <div key={item.issue_id} className="item-card" style={{ borderLeft: '4px solid var(--danger)' }}>
            <div className="item-header">
              <div className="item-title-group">
                <span className="item-id">{item.issue_id} • Danh mục: {item.category || 'Kỹ thuật / Vận hành'}</span>
                <h3 className="item-title" style={{ color: '#fca5a5' }}>{item.description}</h3>
              </div>
              <div className="item-badges">
                <span className={`badge ${severityClass}`}>
                  <AlertTriangle size={13} />
                  Mức độ: {item.severity || 'TRUNG BÌNH'}
                </span>
              </div>
            </div>

            {item.impact && (
              <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                <strong>Ảnh hưởng / Rủi ro:</strong> {item.impact}
              </div>
            )}

            <div className="item-footer">
              <div className="item-meta-group">
                <span>Trạng thái: <strong>{item.status || 'RAISED'}</strong></span>
              </div>

              {item.evidence_list && item.evidence_list.length > 0 && (
                <button
                  type="button"
                  className="evidence-btn"
                  onClick={() => onOpenEvidence(item.description, item.evidence_list)}
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
