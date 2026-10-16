import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PresetBar from './components/PresetBar';
import TranscriptEditor from './components/TranscriptEditor';
import MetricsBanner from './components/MetricsBanner';
import DecisionsTab from './components/tabs/DecisionsTab';
import ActionsTab from './components/tabs/ActionsTab';
import IssuesTab from './components/tabs/IssuesTab';
import RequirementsTab from './components/tabs/RequirementsTab';
import UnresolvedTab from './components/tabs/UnresolvedTab';
import GraphViewer from './components/GraphViewer';
import EvidenceDrawer from './components/EvidenceDrawer';
import ExportModal from './components/ExportModal';

import { TEST_CASES } from './data/presets';
import { checkHealth, processMeeting, getSubgraph, getCausalChain, syncNeo4j } from './api/client';
import { CheckCircle2, ListTodo, AlertTriangle, MessageSquare, HelpCircle, Share2 } from 'lucide-react';

export default function App() {
  const [isOnline, setIsOnline] = useState(false);
  const [selectedPresetId, setSelectedPresetId] = useState('TC-01');

  const [currentMeetingId, setCurrentMeetingId] = useState('MTG-TC01');

  // Input States
  const [meetingTitle, setMeetingTitle] = useState('');
  const [meetingDate, setMeetingDate] = useState('');
  const [participants, setParticipants] = useState('');
  const [transcriptText, setTranscriptText] = useState('');

  // Processing States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [subgraph, setSubgraph] = useState(null);
  const [causalChain, setCausalChain] = useState(null);
  const [syncingNeo4j, setSyncingNeo4j] = useState(false);

  // Active Tab
  const [activeTab, setActiveTab] = useState('decisions');

  // Modals & Drawers
  const [evidenceDrawer, setEvidenceDrawer] = useState({ isOpen: false, title: '', list: [] });
  const [exportModalOpen, setExportModalOpen] = useState(false);

  // Check Backend Health
  useEffect(() => {
    const ping = async () => {
      const res = await checkHealth();
      setIsOnline(res.status === 'healthy' || res.status === 'ok');
    };
    ping();
    const interval = setInterval(ping, 10000);
    return () => clearInterval(interval);
  }, []);

  // Helper to format transcript array to text
  const formatTranscriptToText = (utterances) => {
    return utterances
      .map((u) => `[${u.timestamp || '00:00'}] ${u.speaker_name || 'Người tham gia'}: ${u.text}`)
      .join('\n');
  };

  // Helper to parse text back to utterance objects
  const parseTextToUtterances = (text) => {
    const lines = text.split('\n').filter((l) => l.trim().length > 0);
    return lines.map((line, idx) => {
      // Match pattern [hh:mm] Speaker: Text
      const match = line.match(/^\s*\[(\d{1,2}:\d{2})\]\s*([^:]+):\s*(.+)$/);
      if (match) {
        return {
          utterance_id: `UTT-${String(idx + 1).padStart(2, '0')}`,
          timestamp: match[1].trim(),
          speaker_name: match[2].trim(),
          text: match[3].trim(),
        };
      }
      // Fallback pattern Speaker: Text
      const match2 = line.match(/^\s*([^:]+):\s*(.+)$/);
      if (match2) {
        return {
          utterance_id: `UTT-${String(idx + 1).padStart(2, '0')}`,
          timestamp: '00:00',
          speaker_name: match2[1].trim(),
          text: match2[2].trim(),
        };
      }
      return {
        utterance_id: `UTT-${String(idx + 1).padStart(2, '0')}`,
        timestamp: '00:00',
        speaker_name: 'Người tham gia',
        text: line.trim(),
      };
    });
  };

  // Select Preset Handler
  const handleSelectPreset = (tc) => {
    setSelectedPresetId(tc.id);
    setCurrentMeetingId(tc.meeting.meeting_id || `MTG-${tc.id.replace('-', '')}`);
    setMeetingTitle(tc.meeting.title);
    setMeetingDate(tc.meeting.meeting_date);
    setParticipants(tc.meeting.participants.join(', '));
    setTranscriptText(formatTranscriptToText(tc.meeting.transcript));
    setError(null);
  };

  // Load default preset TC-01 on first load
  useEffect(() => {
    const tc01 = TEST_CASES[0];
    if (tc01) {
      handleSelectPreset(tc01);
    }
  }, []);

  // Process Meeting
  const handleProcess = async () => {
    setLoading(true);
    setError(null);
    setCausalChain(null);

    try {
      const utterances = parseTextToUtterances(transcriptText);
      const participantList = participants
        .split(',')
        .map((p) => p.trim())
        .filter(Boolean);

      const payload = {
        meeting_id: currentMeetingId || (selectedPresetId ? `MTG-${selectedPresetId.replace('-', '')}` : `MTG-${Date.now()}`),
        title: meetingTitle || 'Cuộc họp thảo luận dự án',
        meeting_date: meetingDate || new Date().toISOString().split('T')[0],
        participants: participantList.length > 0 ? participantList : ['Thành viên'],
        transcript: utterances,
      };

      const res = await processMeeting(payload);
      setResults(res);
      setActiveTab('decisions');

      // Fetch Subgraph for visualizer
      try {
        const graphData = await getSubgraph(res.meeting_id);
        setSubgraph(graphData);
      } catch (gErr) {
        console.warn('Subgraph fetch failed:', gErr);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'Lỗi xử lý cuộc họp.');
    } finally {
      setLoading(false);
    }
  };

  // View Causal Chain for specific action item
  const handleViewCausalChain = async (actionId) => {
    try {
      setLoading(true);
      const chain = await getCausalChain(actionId);
      setCausalChain(chain);
      setActiveTab('graph');
    } catch (err) {
      alert(`Không thể lấy chuỗi nhân quả: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Open Evidence Drawer
  const handleOpenEvidence = (title, list) => {
    setEvidenceDrawer({
      isOpen: true,
      title,
      list: list || [],
    });
  };

  // Sync to Neo4j AuraDB
  const handleSyncNeo4j = async () => {
    if (!results?.meeting_id) return;
    setSyncingNeo4j(true);
    try {
      const res = await syncNeo4j(results.meeting_id);
      alert(`✅ Đồng bộ thành công lên Neo4j AuraDB!\n- Nodes tạo mới: ${res.nodes_created || 0}\n- Quan hệ tạo mới: ${res.relationships_created || 0}`);
    } catch (err) {
      alert(`❌ Lỗi đồng bộ Neo4j: ${err.message}`);
    } finally {
      setSyncingNeo4j(false);
    }
  };

  // Reset form
  const handleReset = () => {
    setSelectedPresetId(null);
    setMeetingTitle('');
    setMeetingDate('');
    setParticipants('');
    setTranscriptText('');
    setResults(null);
    setSubgraph(null);
    setCausalChain(null);
    setError(null);
  };

  const handleOpenGraphTab = async () => {
    setActiveTab('graph');
    if (!subgraph || !subgraph.nodes || subgraph.nodes.length === 0) {
      try {
        const mId = results?.meeting_id || currentMeetingId;
        const gData = await getSubgraph(mId);
        setSubgraph(gData);
      } catch (err) {
        console.warn('Error refreshing subgraph:', err);
      }
    }
  };

  return (
    <div className="app-container">
      {/* 1. Header */}
      <Header
        isOnline={isOnline}
        onSyncNeo4j={handleSyncNeo4j}
        syncingNeo4j={syncingNeo4j}
        onOpenExport={() => setExportModalOpen(true)}
        hasResults={Boolean(results)}
      />

      {/* 2. Preset Scenarios */}
      <PresetBar
        selectedPresetId={selectedPresetId}
        onSelectPreset={handleSelectPreset}
      />

      {/* 3. Main Workspace: Two Columns */}
      <div className="workspace-grid">
        {/* Left Column: Input Panel */}
        <TranscriptEditor
          meetingTitle={meetingTitle}
          setMeetingTitle={setMeetingTitle}
          meetingDate={meetingDate}
          setMeetingDate={setMeetingDate}
          participants={participants}
          setParticipants={setParticipants}
          transcriptText={transcriptText}
          setTranscriptText={setTranscriptText}
          onProcess={handleProcess}
          loading={loading}
          onReset={handleReset}
        />

        {/* Right Column: Results & Tabs */}
        <div className="results-container">
          {error && (
            <div className="item-card" style={{ borderLeft: '4px solid var(--danger)', color: '#f87171' }}>
              <strong>Đã xảy ra lỗi:</strong> {error}
            </div>
          )}

          {results ? (
            <>
              {/* Metric Cards Banner */}
              <MetricsBanner results={results} />

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button
                  type="button"
                  className={`tab-btn ${activeTab === 'decisions' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('decisions'); setCausalChain(null); }}
                >
                  <CheckCircle2 size={16} />
                  <span>Quyết định</span>
                  <span className="tab-badge">{results.decisions?.length || 0}</span>
                </button>

                <button
                  type="button"
                  className={`tab-btn ${activeTab === 'actions' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('actions'); setCausalChain(null); }}
                >
                  <ListTodo size={16} />
                  <span>Việc cần làm</span>
                  <span className="tab-badge">{results.action_items?.length || 0}</span>
                </button>

                <button
                  type="button"
                  className={`tab-btn ${activeTab === 'issues' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('issues'); setCausalChain(null); }}
                >
                  <AlertTriangle size={16} />
                  <span>Vướng mắc</span>
                  <span className="tab-badge">{results.issues?.length || 0}</span>
                </button>

                <button
                  type="button"
                  className={`tab-btn ${activeTab === 'requirements' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('requirements'); setCausalChain(null); }}
                >
                  <MessageSquare size={16} />
                  <span>Yêu cầu & Góp ý</span>
                  <span className="tab-badge">{results.requirements_feedbacks?.length || 0}</span>
                </button>

                <button
                  type="button"
                  className={`tab-btn ${activeTab === 'unresolved' ? 'active' : ''}`}
                  onClick={() => { setActiveTab('unresolved'); setCausalChain(null); }}
                >
                  <HelpCircle size={16} />
                  <span>Chưa chốt</span>
                  <span className="tab-badge">{results.unresolved_topics?.length || 0}</span>
                </button>

                <button
                  type="button"
                  className={`tab-btn ${activeTab === 'graph' ? 'active' : ''}`}
                  onClick={handleOpenGraphTab}
                >
                  <Share2 size={16} />
                  <span>Đồ thị & Nhân quả</span>
                </button>
              </div>

              {/* Tab Content Display */}
              {activeTab === 'decisions' && (
                <DecisionsTab
                  decisions={results.decisions}
                  onOpenEvidence={handleOpenEvidence}
                />
              )}

              {activeTab === 'actions' && (
                <ActionsTab
                  actionItems={results.action_items}
                  onOpenEvidence={handleOpenEvidence}
                  onViewCausalChain={handleViewCausalChain}
                />
              )}

              {activeTab === 'issues' && (
                <IssuesTab
                  issues={results.issues}
                  onOpenEvidence={handleOpenEvidence}
                />
              )}

              {activeTab === 'requirements' && (
                <RequirementsTab
                  requirementsFeedbacks={results.requirements_feedbacks}
                  onOpenEvidence={handleOpenEvidence}
                />
              )}

              {activeTab === 'unresolved' && (
                <UnresolvedTab
                  unresolvedTopics={results.unresolved_topics}
                  onOpenEvidence={handleOpenEvidence}
                />
              )}

              {activeTab === 'graph' && (
                <GraphViewer
                  subgraph={subgraph}
                  causalChain={causalChain}
                  onResetCausalChain={() => setCausalChain(null)}
                  onNodeClick={(node) => console.log('Node clicked:', node)}
                />
              )}
            </>
          ) : (
            <div className="item-card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>
                Sẵn Sàng Phân Tích Cuộc Họp
              </div>
              <p style={{ maxWidth: '480px', margin: '0 auto', fontSize: '0.9rem', lineHeight: 1.6 }}>
                Chọn 1 trong các kịch bản kiểm thử phía trên (TC-01 đến TC-05) hoặc dán biên bản hội thoại thô, sau đó nhấn <strong>"Phân Tích Cuộc Họp"</strong> để AI trích xuất dữ liệu đa tầng và kiến tạo đồ thị tri thức.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 4. Slide-out Evidence Drawer */}
      <EvidenceDrawer
        isOpen={evidenceDrawer.isOpen}
        onClose={() => setEvidenceDrawer({ isOpen: false, title: '', list: [] })}
        entityTitle={evidenceDrawer.title}
        evidenceList={evidenceDrawer.list}
      />

      {/* 5. Export Report Modal */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        results={results}
        meetingMeta={{
          title: meetingTitle,
          date: meetingDate,
          participants: participants,
        }}
      />
    </div>
  );
}
