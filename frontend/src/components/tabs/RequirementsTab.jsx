import React from 'react';
import { MessageSquare, Quote, FileCheck } from 'lucide-react';

export default function RequirementsTab({ requirementsFeedbacks = [], onOpenEvidence }) {
  if (!requirementsFeedbacks.length) {
    return <div className="item-card"><p style={{ color: 'var(--text-muted)' }}>Chưa có yêu cầu hoặc phản hồi sản phẩm nào được ghi nhận.</p></div>;
  }

  return (
    <div className="tab-content">
      {requirementsFeedbacks.map((item) => {
        const isReq = item.item_type === 'REQUIREMENT';

        return (
          <div key={item.item_id} className="item-card" style={{ borderLeft: '4px solid var(--purple)' }}>
            <div className="item-header">
              <div className="item-title-group">
                <span className="item-id">{item.item_id} • Nguồn: {item.source_entity || 'Khách hàng / Stakeholder'}</span>
                <h3 className="item-title" style={{ color: '#d8b4fe' }}>{item.description}</h3>
              </div>
              <div className="item-badges">
                <span className="badge" style={{ background: isReq ? 'rgba(139, 92, 246, 0.2)' : 'rgba(59, 130, 246, 0.2)', color: isReq ? '#c084fc' : '#93c5fd', border: '1px solid rgba(139, 92, 246, 0.4)' }}>
                  {isReq ? <FileCheck size={13} /> : <MessageSquare size={13} />}
                  {isReq ? 'YÊU CẦU BẮT BUỘC' : 'PHẢN HỒI / FEEDBACK'}
                </span>
              </div>
            </div>

            {item.context && (
              <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                <strong>Bối cảnh:</strong> {item.context}
              </div>
            )}

            <div className="item-footer">
              <div className="item-meta-group">
                <span>Trạng thái: <strong>{item.status || 'LOGGED'}</strong></span>
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
