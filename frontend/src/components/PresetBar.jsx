import React from 'react';
import { Layers } from 'lucide-react';
import { TEST_CASES } from '../data/presets';

export default function PresetBar({ selectedPresetId, onSelectPreset }) {
  return (
    <div className="presets-card">
      <div className="presets-title">
        <Layers size={16} />
        <span>Kịch bản kiểm thử chuẩn hóa (Mission 2 Test Cases)</span>
      </div>
      <div className="presets-grid">
        {TEST_CASES.map((tc) => {
          const isSelected = selectedPresetId === tc.id;
          return (
            <button
              key={tc.id}
              className={`preset-chip ${isSelected ? 'active' : ''}`}
              onClick={() => onSelectPreset(tc)}
              type="button"
            >
              <div className="preset-header">
                <span className="preset-id">{tc.id}</span>
                <span className="preset-tag">{tc.tag}</span>
              </div>
              <div className="preset-name">{tc.name}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
