import React, { useState } from 'react';
import { HelpCircle, Send, Loader2, Sparkles, Quote, Terminal, CheckCircle2 } from 'lucide-react';
import { queryGraph } from '../api/client';

const SUGGESTED_QUESTIONS = [
  {
    category: 'Nhân quả & Thay đổi (SUPERSEDES)',
    icon: '🎯',
    text: 'Vì sao chúng ta chọn PostgreSQL thay vì MongoDB, ai phụ trách?',
  },
  {
    category: 'Nhiệm vụ & Trách nhiệm (ACT-001)',
    icon: '📌',
    text: 'Nhiệm vụ ACT-001 được giao cho ai và thực thi quyết định nào?',
    targetActionId: 'ACT-001',
  },
  {
    category: 'Vướng mắc & Phản biện',
    icon: '⚠️',
    text: 'Ai là người nêu ra lo ngại về giao dịch ACID và rủi ro gì?',
  },
  {
    category: 'Bằng chứng gốc (Evidence Trace)',
    icon: '🧾',
    text: 'Bằng chứng An đồng ý nhận việc nằm ở phút thứ mấy và nguyên văn là gì?',
    targetActionId: 'ACT-001',
  },
  {
    category: 'Chống ảo giác (Null-Safety)',
    icon: '🛡️',
    text: 'Có công việc nào được giao nhưng chưa có người phụ trách không?',
  },
];

export default function GraphQA({ onHighlightNodes }) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAsk = async (queryText, targetActionId) => {
    const q = queryText || question;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        query: q,
        target_action_id: targetActionId || (q.toLowerCase().includes('act-') ? 'ACT-001' : null),
      };
      const res = await queryGraph(payload);
      setResult(res);

      // If citations or nodes exist, highlight in parent graph if callback provided
      if (onHighlightNodes && res.citations) {
        onHighlightNodes(res);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'Lỗi khi truy vấn đồ thị');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectChip = (item) => {
    setQuestion(item.text);
    handleAsk(item.text, item.targetActionId);
  };

  return (
    <div className="item-card" style={{ marginTop: '16px', border: '1px solid rgba(59, 130, 246, 0.3)', background: 'rgba(15, 23, 42, 0.85)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#93c5fd', fontWeight: 700, fontSize: '0.95rem' }}>
        <Sparkles size={18} color="#60a5fa" />
        <span>Hỏi-Đáp Đồ Thị Tri Thức & Giải Trình Nhân Quả (Graph Retrieval Q&A)</span>
      </div>

      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '4px 0 10px 0' }}>
        Nhấp vào các mẫu câu hỏi gợi ý bên dưới hoặc tự nhập câu hỏi tự nhiên để đồ thị duyệt node, truy vết lý do và dẫn xuất bằng chứng gốc:
      </p>

      {/* Suggested Question Chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '14px' }}>
        {SUGGESTED_QUESTIONS.map((item, idx) => (
          <button
            key={idx}
            type="button"
            className="btn-secondary"
            style={{
              padding: '6px 12px',
              fontSize: '0.78rem',
              borderRadius: '20px',
              background: 'rgba(30, 41, 59, 0.7)',
              borderColor: 'rgba(148, 163, 184, 0.2)',
              color: '#e2e8f0',
              textAlign: 'left',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
            }}
            onClick={() => handleSelectChip(item)}
            disabled={loading}
          >
            <span>{item.icon}</span>
            <span>{item.text}</span>
          </button>
        ))}
      </div>

      {/* Input Field */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          className="form-input"
          style={{ flex: 1, padding: '10px 14px' }}
          placeholder="Nhập câu hỏi: Vì sao chọn phương án này, ai yêu cầu, bằng chứng ở phút mấy?..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
        />
        <button
          type="button"
          className="btn-primary"
          style={{ padding: '0 20px', whiteSpace: 'nowrap' }}
          onClick={() => handleAsk()}
          disabled={loading || !question.trim()}
        >
          {loading ? <Loader2 size={16} className="spinner" /> : <Send size={16} />}
          <span>{loading ? 'Đang duyệt...' : 'Hỏi Graph'}</span>
        </button>
      </div>

      {error && (
        <div style={{ marginTop: '12px', color: '#f87171', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      {/* Result Display Box */}
      {result && (
        <div style={{
          marginTop: '16px',
          background: 'rgba(10, 14, 23, 0.9)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          borderRadius: '12px',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}>
          <div>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              💡 Câu Trả Lời Giải Trình Của Đồ Thị:
            </span>
            <div style={{ fontSize: '0.98rem', fontWeight: 600, color: '#ffffff', marginTop: '4px', lineHeight: 1.5 }}>
              {result.answer}
            </div>
          </div>

          {/* Simulated Cypher Query */}
          {result.cypher_query_used && (
            <div style={{ background: 'rgba(0, 0, 0, 0.4)', padding: '10px 12px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: '#94a3b8', marginBottom: '4px' }}>
                <Terminal size={12} color="#f59e0b" />
                <span>Cypher Query mô phỏng đường đi trên đồ thị (Graph Traversal):</span>
              </div>
              <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: '#fde68a', display: 'block', overflowX: 'auto' }}>
                {result.cypher_query_used}
              </code>
            </div>
          )}

          {/* Citations List */}
          {result.citations && result.citations.length > 0 && (
            <div>
              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                🧾 Bằng Chứng Nguồn Trích Dẫn ({result.citations.length}):
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                {result.citations.map((c, i) => (
                  <div key={i} style={{
                    background: 'rgba(30, 41, 59, 0.5)',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    fontSize: '0.84rem',
                    borderLeft: '3px solid #38bdf8',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                      <span style={{ fontWeight: 700, color: '#93c5fd' }}>{c.speaker || 'Thành viên'}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', fontSize: '0.75rem' }}>[{c.timestamp || '00:00'}]</span>
                    </div>
                    <div style={{ fontStyle: 'italic', color: '#e2e8f0' }}>
                      "{c.quote || c.quote_text || 'Bằng chứng ghi nhận từ cuộc họp'}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
