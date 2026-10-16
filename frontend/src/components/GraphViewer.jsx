import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import { Share2, RefreshCw, ZoomIn, ZoomOut, Info, ArrowRight, Sparkles } from 'lucide-react';
import GraphQA from './GraphQA';

export default function GraphViewer({ subgraph, causalChain, onNodeClick, onResetCausalChain }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [selectedNodeInfo, setSelectedNodeInfo] = useState(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Convert backend graph nodes and edges to Vis.js format
    const nodes = [];
    const edges = [];

    // Helper for node coloring and icons
    const getNodeStyle = (type, label, props = {}) => {
      switch (type) {
        case 'Meeting':
          return { background: '#4f46e5', border: '#4338ca', shape: 'box', font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true } };
        case 'Decision':
          if (props.is_final_active) {
            return { background: '#10b981', border: '#059669', shape: 'ellipse', font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true } };
          }
          return { background: '#475569', border: '#334155', shape: 'ellipse', font: { color: '#cbd5e1', face: 'Plus Jakarta Sans' } };
        case 'ActionItem':
          return { background: '#2563eb', border: '#1d4ed8', shape: 'box', font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true } };
        case 'Issue':
          return { background: '#dc2626', border: '#b91c1c', shape: 'diamond', font: { color: '#ffffff', face: 'Plus Jakarta Sans' } };
        case 'Evidence':
          return { background: '#0e7490', border: '#0891b2', shape: 'box', font: { color: '#cffafe', face: 'JetBrains Mono', size: 10 } };
        case 'Person':
        case 'Participant':
          return { background: '#d97706', border: '#b45309', shape: 'circle', font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true } };
        case 'REQUIREMENT':
        case 'FEEDBACK':
        case 'RequirementFeedback':
          return { background: '#7c3aed', border: '#6d28d9', shape: 'box', font: { color: '#ffffff', face: 'Plus Jakarta Sans' } };
        case 'UnresolvedTopic':
          return { background: '#0891b2', border: '#06b6d4', shape: 'box', font: { color: '#ffffff', face: 'Plus Jakarta Sans' } };
        default:
          return { background: '#64748b', border: '#475569', shape: 'dot', font: { color: '#ffffff' } };
      }
    };

    // If viewing a specific causal chain from /api/actions/{id}/causal-chain
    if (causalChain) {
      const actId = causalChain.action_id || 'ACT-001';
      const actLabel = causalChain.action_text || actId;

      // 1. Node ActionItem
      nodes.push({
        id: actId,
        label: `Nhiệm vụ (Task)\n${actLabel.slice(0, 36)}${actLabel.length > 36 ? '...' : ''}`,
        title: `<b>ActionItem [${actId}]</b>: ${actLabel}`,
        color: { background: '#2563eb', border: '#1d4ed8', highlight: { background: '#3b82f6', border: '#60a5fa' } },
        shape: 'box',
        font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true, size: 12 },
        margin: 12,
        raw: { id: actId, type: 'ActionItem', label: actLabel, properties: { action_id: actId } },
      });

      // 2. Node Assignee (Person)
      if (causalChain.assignee) {
        const pId = `USR-${causalChain.assignee}`;
        nodes.push({
          id: pId,
          label: `Người thực hiện\n${causalChain.assignee}`,
          title: `<b>Người phụ trách</b>: ${causalChain.assignee}`,
          color: { background: '#d97706', border: '#b45309', highlight: { background: '#f59e0b', border: '#d97706' } },
          shape: 'circle',
          font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true, size: 11 },
          margin: 12,
          raw: { id: pId, type: 'Person', label: causalChain.assignee },
        });
        edges.push({
          id: 'chain-assigned',
          from: actId,
          to: pId,
          label: 'ASSIGNED_TO',
          arrows: 'to',
          color: { color: '#f59e0b', highlight: '#fbbf24' },
          width: 2.5,
          font: { color: '#fbbf24', size: 10, background: '#080d18' },
        });
      }

      // 3. Node Decision (Active Final)
      if (causalChain.decision) {
        const decId = causalChain.decision.id || 'DEC-FINAL';
        const decContent = causalChain.decision.content || 'Quyết định chốt';
        nodes.push({
          id: decId,
          label: `Quyết định chốt\n${decContent.slice(0, 32)}${decContent.length > 32 ? '...' : ''}`,
          title: `<b>Quyết định thực thi</b>: ${decContent}`,
          color: { background: '#059669', border: '#047857', highlight: { background: '#10b981', border: '#34d399' } },
          shape: 'ellipse',
          font: { color: '#ffffff', face: 'Plus Jakarta Sans', bold: true, size: 12 },
          margin: 14,
          raw: { id: decId, type: 'Decision', label: decContent, properties: { is_final_active: true } },
        });
        edges.push({
          id: 'chain-implements',
          from: actId,
          to: decId,
          label: 'IMPLEMENTS',
          arrows: 'to',
          color: { color: '#38bdf8', highlight: '#7dd3fc' },
          width: 3,
          font: { color: '#38bdf8', size: 11, bold: true, background: '#080d18' },
        });

        // 4. Node Superseded Decision (Old Proposal)
        if (causalChain.superseded_decision) {
          const oldId = causalChain.superseded_decision.id || 'DEC-OLD';
          const oldContent = causalChain.superseded_decision.content || 'Phương án cũ bị thay thế';
          nodes.push({
            id: oldId,
            label: `Bị thay thế\n${oldContent.slice(0, 30)}${oldContent.length > 30 ? '...' : ''}`,
            title: `<b>Phương án đã bị thay thế</b>: ${oldContent}`,
            color: { background: '#475569', border: '#334155', highlight: { background: '#64748b', border: '#475569' } },
            shape: 'ellipse',
            font: { color: '#cbd5e1', face: 'Plus Jakarta Sans', size: 11 },
            margin: 12,
            raw: { id: oldId, type: 'Decision', label: oldContent, properties: { is_final_active: false } },
          });
          edges.push({
            id: 'chain-supersedes',
            from: decId,
            to: oldId,
            label: 'SUPERSEDES',
            arrows: 'to',
            color: { color: '#fbbf24', highlight: '#fde68a' },
            width: 2.5,
            dashes: [6, 4],
            font: { color: '#fbbf24', size: 10, bold: true, background: '#080d18' },
          });
        }

        // 5. Node Issue / Objection Reason
        if (causalChain.objection_reason) {
          const issId = `ISSUE-${actId}`;
          const issLabel = causalChain.objection_reason;
          nodes.push({
            id: issId,
            label: `Rủi ro / Phản biện\n${issLabel.slice(0, 34)}${issLabel.length > 34 ? '...' : ''}`,
            title: `<b>Lý do / Phản biện</b>: ${issLabel}`,
            color: { background: '#dc2626', border: '#991b1b', highlight: { background: '#ef4444', border: '#f87171' } },
            shape: 'diamond',
            font: { color: '#ffffff', face: 'Plus Jakarta Sans', size: 11 },
            margin: 12,
            raw: { id: issId, type: 'Issue', label: issLabel },
          });
          edges.push({
            id: 'chain-motivated',
            from: decId,
            to: issId,
            label: 'MOTIVATED_BY',
            arrows: 'to',
            color: { color: '#f87171', highlight: '#fca5a5' },
            width: 2.5,
            font: { color: '#f87171', size: 10, background: '#080d18' },
          });
        }
      }

      // 6. Evidences
      (causalChain.evidences || []).forEach((ev, idx) => {
        const evId = ev.evidence_id || `EV-CHAIN-${idx}`;
        const evQuote = ev.quote || ev.quote_text || '';
        const evSpeaker = ev.speaker || 'Thành viên';
        const evTime = ev.timestamp || '00:00';
        nodes.push({
          id: evId,
          label: `Bằng chứng [${evTime}]\n${evSpeaker}: "${evQuote.slice(0, 32)}${evQuote.length > 32 ? '...' : ''}"`,
          title: `<b>Bằng chứng nguồn:</b> "${evQuote}" (${evSpeaker} - ${evTime})`,
          color: { background: '#0e7490', border: '#0891b2', highlight: { background: '#06b6d4', border: '#22d3ee' } },
          shape: 'box',
          font: { color: '#cffafe', face: 'JetBrains Mono', size: 9 },
          margin: 8,
          raw: { id: evId, type: 'Evidence', label: evQuote },
        });
        edges.push({
          id: `chain-ev-${idx}`,
          from: actId,
          to: evId,
          label: 'SUPPORTED_BY',
          arrows: 'to',
          color: { color: '#0891b2', highlight: '#06b6d4' },
          width: 1.5,
          font: { color: '#67e8f9', size: 9, background: '#080d18' },
        });
      });
    } else if (subgraph && subgraph.nodes) {
      // General Subgraph from meeting
      subgraph.nodes.forEach((n) => {
        const type = n.label || n.type || 'Entity';
        const props = n.properties || {};
        const contentText = props.content || props.action_text || props.name || props.title || props.topic_name || props.quote_text || n.id;
        const style = getNodeStyle(type, contentText, props);
        const shortText = contentText.length > 28 ? contentText.slice(0, 28) + '...' : contentText;
        nodes.push({
          id: n.id,
          label: `${type}\n${shortText}`,
          title: `<b>${type} [${n.id}]</b>: ${contentText}`,
          color: { background: style.background, border: style.border, highlight: { background: '#38bdf8', border: '#0284c7' } },
          shape: style.shape,
          font: style.font,
          margin: 10,
          raw: { id: n.id, type, label: contentText, properties: props },
        });
      });

      (subgraph.edges || []).forEach((e, idx) => {
        const isSupersede = e.relation === 'SUPERSEDES';
        const isImplements = e.relation === 'IMPLEMENTS';
        const isAssigned = e.relation === 'ASSIGNED_TO';
        const isSupported = e.relation === 'SUPPORTED_BY';
        const edgeColor = isSupersede ? '#fbbf24' : isImplements ? '#38bdf8' : isAssigned ? '#f59e0b' : isSupported ? '#0891b2' : '#64748b';
        edges.push({
          id: `edge-${idx}`,
          from: e.source,
          to: e.target,
          label: e.relation,
          arrows: 'to',
          color: { color: edgeColor, highlight: '#ffffff' },
          font: { color: '#94a3b8', size: 10, align: 'middle', background: '#080d18' },
          width: isSupersede || isImplements ? 2.5 : 1.5,
          dashes: isSupersede ? [6, 4] : false,
        });
      });
    }

    const data = { nodes, edges };
    const options = {
      physics: {
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -130,
          centralGravity: 0.01,
          springLength: 170,
          springConstant: 0.05,
          damping: 0.7,
          avoidOverlap: 0.6,
        },
        maxVelocity: 40,
        minVelocity: 0.1,
        stabilization: { iterations: 180 },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        navigationButtons: false,
        zoomView: true,
        dragView: true,
      },
    };

    const network = new Network(containerRef.current, data, options);
    networkRef.current = network;

    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const clickedId = params.nodes[0];
        const found = nodes.find((n) => n.id === clickedId);
        if (found) {
          setSelectedNodeInfo(found.raw);
          if (onNodeClick) onNodeClick(found.raw);
        }
      } else {
        setSelectedNodeInfo(null);
      }
    });

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [subgraph, causalChain]);

  const handleResetZoom = () => {
    if (networkRef.current) {
      networkRef.current.fit({ animation: { duration: 500 } });
    }
  };

  const handleZoomIn = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 1.3, animation: { duration: 300 } });
    }
  };

  const handleZoomOut = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 0.7, animation: { duration: 300 } });
    }
  };

  return (
    <div className="tab-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
          {causalChain ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ color: '#38bdf8', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={14} />
                <span>Chuỗi Nhân Quả cho: {causalChain.action_id}</span>
              </span>
              {onResetCausalChain && (
                <button
                  type="button"
                  className="btn-secondary"
                  style={{ padding: '3px 10px', fontSize: '0.75rem', color: '#93c5fd' }}
                  onClick={onResetCausalChain}
                >
                  ← Toàn bộ đồ thị
                </button>
              )}
            </div>
          ) : (
            <span>Đồ thị tri thức cuộc họp (Evidence-Centered Knowledge Graph)</span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button type="button" className="btn-secondary" onClick={handleZoomIn} title="Phóng to" style={{ padding: '6px 10px' }}>
            <ZoomIn size={13} />
          </button>
          <button type="button" className="btn-secondary" onClick={handleZoomOut} title="Thu nhỏ" style={{ padding: '6px 10px' }}>
            <ZoomOut size={13} />
          </button>
          <button type="button" className="btn-secondary" onClick={handleResetZoom} title="Căn giữa toàn màn hình" style={{ padding: '6px 12px' }}>
            <RefreshCw size={13} />
            <span>Căn giữa</span>
          </button>
        </div>
      </div>

      {/* Causal Explanation Flow Card */}
      {causalChain && (
        <div className="item-card" style={{ borderLeft: '4px solid #38bdf8', background: 'rgba(15, 23, 42, 0.95)', padding: '14px 18px' }}>
          <div style={{ color: '#38bdf8', fontWeight: 700, fontSize: '0.84rem', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={14} />
            <span>GIẢI TRÌNH CHUỖI NHÂN QUẢ (Causal Chain Flow):</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
            <span className="badge badge-assigned">Nhiệm vụ: {causalChain.action_text || causalChain.action_id}</span>
            <span style={{ color: 'var(--text-dim)' }}><ArrowRight size={13} /></span>
            <span>Người làm: <strong style={{ color: '#fbbf24' }}>{causalChain.assignee || 'Chưa phân công'}</strong></span>
            {causalChain.decision && (
              <>
                <span style={{ color: 'var(--text-dim)' }}><ArrowRight size={13} /></span>
                <span>Thực thi: <strong style={{ color: '#34d399' }}>{causalChain.decision.content}</strong></span>
              </>
            )}
            {causalChain.superseded_decision && (
              <>
                <span style={{ color: 'var(--text-dim)' }}><ArrowRight size={13} /></span>
                <span>Thay thế: <strong style={{ textDecoration: 'line-through', color: '#94a3b8' }}>{causalChain.superseded_decision.content}</strong></span>
              </>
            )}
            {causalChain.objection_reason && (
              <>
                <span style={{ color: 'var(--text-dim)' }}><ArrowRight size={13} /></span>
                <span>Do phản biện: <strong style={{ color: '#f87171' }}>{causalChain.objection_reason}</strong></span>
              </>
            )}
          </div>
        </div>
      )}

      <div className="graph-container">
        <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

        <div className="graph-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#10b981' }} />
            <span>Quyết định chốt</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#475569' }} />
            <span>Bị thay thế (SUPERSEDES)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#2563eb' }} />
            <span>Công việc</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#dc2626' }} />
            <span>Rủi ro / Issue</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#0e7490' }} />
            <span>Bằng chứng</span>
          </div>
        </div>
      </div>

      {selectedNodeInfo && (
        <div className="item-card" style={{ marginTop: '8px', borderLeft: '4px solid #38bdf8' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', fontWeight: 700, fontSize: '0.84rem' }}>
            <Info size={15} />
            <span>CHI TIẾT NODE ĐƯỢC CHỌN: {selectedNodeInfo.type} ({selectedNodeInfo.id})</span>
          </div>
          <div style={{ fontSize: '0.98rem', fontWeight: 600, color: '#fff' }}>
            {selectedNodeInfo.label}
          </div>
          {selectedNodeInfo.properties && (
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {JSON.stringify(selectedNodeInfo.properties, null, 2)}
            </div>
          )}
        </div>
      )}

      {/* Graph Retrieval & Question Templates Widget */}
      <GraphQA />
    </div>
  );
}
