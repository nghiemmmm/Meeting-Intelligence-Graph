import React from 'react';
import { User, Calendar, AlertCircle, Quote, GitBranch, Sparkles } from 'lucide-react';

export default function ActionsTab({ actionItems = [], onOpenEvidence, onViewCausalChain }) {
  if (!actionItems.length) {
    return (
      <div className="item-card">
        <p style={{ color: 'var(--text-muted)' }}>Chưa có công việc nào được giao trong cuộc họp.</p>
      </div>
    );
  }

  return (
    <div className="tab-content">
      {actionItems.map((item) => {
        const assigneeName = item.assignee?.name;
        const hasAssignee = Boolean(assigneeName && assigneeName.trim() !== '' && assigneeName.toLowerCase() !== 'null');
        const deadline = item.deadline?.raw_text || item.deadline_raw;
        const taskTitle = item.action_text || item.description;

        const priorityClass = item.priority === 'HIGH' 
          ? 'badge-priority-high' 
          : item.priority === 'MEDIUM' 
            ? 'badge-priority-medium' 
            : 'badge-priority-low';

        return (
          <div key={item.action_id} className="item-card">
            <div className="item-header">
              <div className="item-title-group">
                <span className="item-id">{item.action_id} • Trạng thái: {item.status || 'CONFIRMED'}</span>
                <h3 className="item-title">{taskTitle}</h3>
              </div>
              <div className="item-badges">
                {hasAssignee ? (
                  <span className="badge badge-assigned">
                    <User size={13} />
                    {assigneeName}
                  </span>
                ) : (
                  <span className="badge badge-unassigned" title="Null-Safety: Không tự bịa người làm khi transcript nói chung chung">
                    <AlertCircle size={13} />
                    Chưa phân công (Null-Safety)
                  </span>
                )}

                {item.priority && (
                  <span className={`badge ${priorityClass}`}>
                    Ưu tiên: {item.priority}
                  </span>
                )}
              </div>
            </div>

            {/* DUR: De-contextualized Sentence Box */}
            {item.decontextualized_text && (
              <div className="dur-box">
                <div className="dur-label">
                  <Sparkles size={11} />
                  <span>Khôi phục ngữ cảnh độc lập (DUR):</span>
                </div>
                <div>{item.decontextualized_text}</div>
              </div>
            )}

            <div className="item-footer">
              <div className="item-meta-group">
                {deadline ? (
                  <span className="meta-item">
                    <Calendar size={13} color="#f59e0b" />
                    <span>Hạn chót: <strong style={{ color: '#fff' }}>{deadline}</strong></span>
                  </span>
                ) : (
                  <span className="meta-item" style={{ color: 'var(--text-dim)' }}>
                    <Calendar size={13} />
                    <span>Hạn chót: <em>Chưa ấn định</em></span>
                  </span>
                )}
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="evidence-btn"
                  style={{ color: '#c084fc', borderColor: 'rgba(192, 132, 252, 0.35)' }}
                  onClick={() => onViewCausalChain(item.action_id)}
                  title="Xem sơ đồ đồ thị giải trình tại sao giao việc này"
                >
                  <GitBranch size={13} />
                  <span>Chuỗi nhân quả</span>
                </button>

                {item.evidence_list && item.evidence_list.length > 0 && (
                  <button
                    type="button"
                    className="evidence-btn"
                    onClick={() => onOpenEvidence(taskTitle, item.evidence_list)}
                  >
                    <Quote size={13} />
                    <span>Bằng chứng ({item.evidence_list.length})</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
