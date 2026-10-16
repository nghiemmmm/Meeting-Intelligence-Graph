const API_BASE = '';

/**
 * Health check endpoint
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Healthcheck failed:', err);
    return { status: 'offline', error: err.message };
  }
}

/**
 * Process raw meeting transcript through FastAPI Pipeline
 */
export async function processMeeting(payload) {
  const res = await fetch(`${API_BASE}/api/meetings/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Lỗi xử lý cuộc họp (${res.status})`);
  }

  return await res.json();
}

/**
 * Fetch meeting details by ID
 */
export async function getMeeting(meetingId) {
  const res = await fetch(`${API_BASE}/api/meetings/${meetingId}`);
  if (!res.ok) throw new Error(`Không tìm thấy cuộc họp ${meetingId}`);
  return await res.json();
}

/**
 * Get final active decisions (filters out superseded ones)
 */
export async function getFinalDecisions(meetingId) {
  const url = meetingId 
    ? `${API_BASE}/api/decisions/final?meeting_id=${encodeURIComponent(meetingId)}`
    : `${API_BASE}/api/decisions/final`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Lỗi lấy quyết định cuối cùng`);
  return await res.json();
}

/**
 * Get causal chain explanation for an action item
 */
export async function getCausalChain(actionId) {
  const res = await fetch(`${API_BASE}/api/actions/${encodeURIComponent(actionId)}/causal-chain`);
  if (!res.ok) throw new Error(`Lỗi truy vết chuỗi nhân quả cho ${actionId}`);
  return await res.json();
}

/**
 * Get knowledge subgraph for visualization
 */
export async function getSubgraph(meetingId) {
  const url = meetingId
    ? `${API_BASE}/api/graph/subgraph?meeting_id=${encodeURIComponent(meetingId)}`
    : `${API_BASE}/api/graph/subgraph`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Lỗi lấy dữ liệu đồ thị`);
  return await res.json();
}

/**
 * Trigger sync to Neo4j AuraDB
 */
export async function syncNeo4j(meetingId) {
  const url = meetingId
    ? `${API_BASE}/api/graph/neo4j/sync?meeting_id=${encodeURIComponent(meetingId)}`
    : `${API_BASE}/api/graph/neo4j/sync`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Lỗi đồng bộ Neo4j AuraDB`);
  }
  return await res.json();
}

/**
 * Natural language Graph Retrieval & Q&A
 */
export async function queryGraph(payload) {
  const res = await fetch(`${API_BASE}/api/graph/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Lỗi truy vấn đồ thị (${res.status})`);
  }

  return await res.json();
}
