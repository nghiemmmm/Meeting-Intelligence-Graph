import React, { useState } from 'react';
import { X, Copy, Check, Download, FileText } from 'lucide-react';

export default function ExportModal({ isOpen, onClose, results, meetingMeta }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !results) return null;

  const generateMarkdown = () => {
    const decisions = results.decisions || [];
    const actions = results.action_items || [];
    const issues = results.issues || [];
    const reqs = results.requirements_feedbacks || [];
    const unresolved = results.unresolved_topics || [];

    let md = `# 📝 BIÊN BẢN CUỘC HỌP: ${meetingMeta.title || 'Cuộc họp'}\n\n`;
    md += `- **Ngày họp:** ${meetingMeta.date || 'Hôm nay'}\n`;
    md += `- **Thành viên tham dự:** ${meetingMeta.participants || 'N/A'}\n\n`;
    md += `---\n\n`;

    md += `## 🎯 1. CÁC QUYẾT ĐỊNH ĐÃ THỐNG NHẤT\n\n`;
    if (decisions.length === 0) {
      md += `*Không có quyết định nào.*\n\n`;
    } else {
      decisions.forEach((d) => {
        if (d.is_final_active) {
          md += `### ✅ [CHỐT CÓ HIỆU LỰC] ${d.decision_text}\n`;
          if (d.supersedes_decision_id) {
            md += `> *(Thay thế phương án trước đó: ${d.supersedes_decision_id})*\n`;
          }
          if (d.rationale) md += `- **Căn cứ / Lý do:** ${d.rationale}\n`;
          md += `\n`;
        } else {
          md += `### 🔄 [ĐÃ THAY THẾ] ~~${d.decision_text}~~\n`;
          if (d.superseded_by) {
            md += `> *(Đã bị thay thế bởi ${d.superseded_by})*\n`;
          }
          md += `\n`;
        }
      });
    }

    md += `## 📌 2. DANH MỤC CÔNG VIỆC CẦN LÀM (ACTION ITEMS)\n\n`;
    if (actions.length === 0) {
      md += `*Không có công việc nào.*\n\n`;
    } else {
      actions.forEach((a) => {
        const assignee = a.assignee?.name || 'Chưa phân công';
        const deadline = a.deadline?.raw_text || a.deadline_raw || 'Chưa ấn định';
        md += `- [ ] **${a.description}**\n`;
        md += `  - **Người phụ trách:** ${assignee}\n`;
        md += `  - **Hạn chót:** ${deadline}\n`;
        md += `  - **Mức ưu tiên:** ${a.priority || 'MEDIUM'}\n`;
        if (a.decontextualized_text) {
          md += `  - **Ngữ cảnh độc lập (DUR):** ${a.decontextualized_text}\n`;
        }
        md += `\n`;
      });
    }

    md += `## ⚠️ 3. VƯỚNG MẮC / RỦI RO (ISSUES & BLOCKERS)\n\n`;
    if (issues.length === 0) {
      md += `*Không có rủi ro nào ghi nhận.*\n\n`;
    } else {
      issues.forEach((i) => {
        md += `- **[${i.severity || 'WARNING'}] ${i.description}**\n`;
        if (i.impact) md += `  - *Tác động:* ${i.impact}\n`;
      });
      md += `\n`;
    }

    md += `## 💬 4. YÊU CẦU & PHẢN HỒI (REQUIREMENTS & FEEDBACKS)\n\n`;
    if (reqs.length === 0) {
      md += `*Không có.*\n\n`;
    } else {
      reqs.forEach((r) => {
        md += `- **[${r.item_type}]** ${r.description} *(Nguồn: ${r.source_entity || 'Khách hàng'})*\n`;
      });
      md += `\n`;
    }

    md += `## ❓ 5. NỘI DUNG CHƯA CHỐT (UNRESOLVED TOPICS)\n\n`;
    if (unresolved.length === 0) {
      md += `*Tất cả nội dung đã được chốt.*\n\n`;
    } else {
      unresolved.forEach((u) => {
        md += `- **${u.topic_name}**: ${u.description || ''}\n`;
        if (u.recommended_action) {
          md += `  - *Đề xuất cho cuộc họp sau:* ${u.recommended_action}\n`;
        }
      });
      md += `\n`;
    }

    md += `---\n*Biên bản được tự động trích xuất và liên kết đồ thị bởi Meeting Intelligence Assistant.*\n`;
    return md;
  };

  const mdContent = generateMarkdown();

  const handleCopy = () => {
    navigator.clipboard.writeText(mdContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadMd = () => {
    const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Bien-Ban-Hop-${meetingMeta.title || 'Meeting'}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadJson = () => {
    const jsonStr = JSON.stringify(results, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Bien-Ban-Hop-${meetingMeta.title || 'Meeting'}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="drawer-overlay" onClick={onClose} style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div
        className="drawer-panel"
        onClick={(e) => e.stopPropagation()}
        style={{ width: '800px', height: '85vh', borderRadius: '16px', margin: 'auto' }}
      >
        <div className="drawer-header">
          <div className="drawer-title">
            <FileText size={20} color="#38bdf8" />
            <span>Xuất Biên Bản Cuộc Họp Cấu Trúc</span>
          </div>
          <button type="button" className="btn-secondary" onClick={onClose} style={{ padding: '6px', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        <div className="drawer-body" style={{ flex: 1 }}>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn-secondary" onClick={handleCopy}>
              {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
              <span>{copied ? 'Đã sao chép!' : 'Sao chép Markdown'}</span>
            </button>
            <button type="button" className="btn-secondary" onClick={handleDownloadMd}>
              <Download size={14} />
              <span>Tải .MD</span>
            </button>
            <button type="button" className="btn-secondary" onClick={handleDownloadJson}>
              <Download size={14} />
              <span>Tải .JSON</span>
            </button>
          </div>

          <pre style={{
            background: 'rgba(0, 0, 0, 0.4)',
            padding: '16px',
            borderRadius: '8px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem',
            color: '#e2e8f0',
            overflowY: 'auto',
            maxHeight: '52vh',
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            border: '1px solid var(--border-subtle)',
          }}>
            {mdContent}
          </pre>
        </div>
      </div>
    </div>
  );
}
