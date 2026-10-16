import React from 'react';
import { Sparkles, Activity, Database, Download } from 'lucide-react';

export default function Header({ isOnline, onSyncNeo4j, syncingNeo4j, onOpenExport, hasResults }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-icon-wrapper">
          <Sparkles size={24} color="#ffffff" />
        </div>
        <div>
          <h1 className="brand-title">Trí Tuệ Cuộc Họp</h1>
          <p className="brand-subtitle">Meeting Intelligence Assistant • Temporal Tracking & Knowledge Graph</p>
        </div>
      </div>

      <div className="header-actions">
        <div className="status-badge" title={isOnline ? 'FastAPI Backend đang hoạt động' : 'Không thể kết nối FastAPI backend'}>
          <span className={`status-dot ${isOnline ? 'online' : 'offline'}`} />
          <span>{isOnline ? 'FastAPI Online' : 'FastAPI Offline'}</span>
        </div>

        {hasResults && (
          <>
            <button
              className="btn-secondary"
              onClick={onSyncNeo4j}
              disabled={syncingNeo4j}
              title="Đồng bộ Đồ thị tri thức lên Neo4j AuraDB"
            >
              <Database size={15} />
              <span>{syncingNeo4j ? 'Đang đồng bộ...' : 'Đồng bộ Neo4j'}</span>
            </button>

            <button
              className="btn-secondary"
              onClick={onOpenExport}
              title="Xuất biên bản họp ra định dạng Markdown / JSON"
            >
              <Download size={15} />
              <span>Xuất Biên Bản</span>
            </button>
          </>
        )}
      </div>
    </header>
  );
}
