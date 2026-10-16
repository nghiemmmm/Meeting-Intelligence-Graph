import React from 'react';
import { CheckCircle2, ListTodo, AlertTriangle, FileCheck, HelpCircle } from 'lucide-react';

export default function MetricsBanner({ results }) {
  if (!results) return null;

  const decisions = results.decisions || [];
  const activeDecisions = decisions.filter((d) => d.is_final_active);
  const supersededDecisions = decisions.filter((d) => !d.is_final_active || d.status === 'SUPERSEDED');
  const actionItems = results.action_items || [];
  const issues = results.issues || [];
  const requirements = results.requirements_feedbacks || [];
  const unresolved = results.unresolved_topics || [];

  return (
    <div className="metrics-grid">
      <div className="metric-card decisions">
        <div className="metric-header-row">
          <div className="metric-icon-wrap">
            <CheckCircle2 size={14} />
          </div>
          {supersededDecisions.length > 0 && (
            <span className="metric-subbadge">
              +{supersededDecisions.length} thay đổi
            </span>
          )}
        </div>
        <div className="metric-number-row">
          <span className="metric-number">{activeDecisions.length}</span>
        </div>
        <div className="metric-label">Quyết định chốt</div>
      </div>

      <div className="metric-card actions">
        <div className="metric-header-row">
          <div className="metric-icon-wrap">
            <ListTodo size={14} />
          </div>
        </div>
        <div className="metric-number-row">
          <span className="metric-number">{actionItems.length}</span>
        </div>
        <div className="metric-label">Công việc cần làm</div>
      </div>

      <div className="metric-card issues">
        <div className="metric-header-row">
          <div className="metric-icon-wrap">
            <AlertTriangle size={14} />
          </div>
        </div>
        <div className="metric-number-row">
          <span className="metric-number">{issues.length}</span>
        </div>
        <div className="metric-label">Vướng mắc / Rủi ro</div>
      </div>

      <div className="metric-card requirements">
        <div className="metric-header-row">
          <div className="metric-icon-wrap">
            <FileCheck size={14} />
          </div>
        </div>
        <div className="metric-number-row">
          <span className="metric-number">{requirements.length}</span>
        </div>
        <div className="metric-label">Yêu cầu & Phản hồi</div>
      </div>

      <div className="metric-card unresolved">
        <div className="metric-header-row">
          <div className="metric-icon-wrap">
            <HelpCircle size={14} />
          </div>
        </div>
        <div className="metric-number-row">
          <span className="metric-number">{unresolved.length}</span>
        </div>
        <div className="metric-label">Nội dung chưa chốt</div>
      </div>
    </div>
  );
}
