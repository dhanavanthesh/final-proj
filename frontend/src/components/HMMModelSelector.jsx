import React from 'react';

/**
 * HMM Model Selector Component
 * Allows users to select which HMM model to use for Viterbi decoding
 */
export function HMMModelSelector({ selected, onChange, models }) {
  // Default models if not provided
  const defaultModels = [
    {
      id: "2-state-exon-intron",
      name: "2-State: Exon (E) / Intron (I)",
      description: "Basic model for exon and intron regions"
    },
    {
      id: "3-state-promoter-exon-intron",
      name: "3-State: Promoter / Exon / Intron",
      description: "Extended model including promoter regions"
    }
  ];

  const availableModels = models || defaultModels;

  return (
    <div className="hmm-model-selector">
      <label htmlFor="hmm-model" className="selector-label">
        <strong>HMM Model:</strong>
      </label>
      <select
        id="hmm-model"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        className="model-select"
      >
        {availableModels.map(model => (
          <option key={model.id} value={model.id}>
            {model.name}
          </option>
        ))}
      </select>

      {/* Show description of selected model */}
      {availableModels.find(m => m.id === selected)?.description && (
        <div className="model-description">
          <small>
            {availableModels.find(m => m.id === selected).description}
          </small>
        </div>
      )}
    </div>
  );
}

export default HMMModelSelector;
