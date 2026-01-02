import React from 'react';

/**
 * Decoded Path Viewer Component
 * Displays DNA sequence aligned with decoded hidden state path
 */
export function DecodedPathViewer({ dnaSequence, decodedPath, decodedPathString }) {
  if (!dnaSequence || !decodedPath) {
    return null;
  }

  // Color mapping for states
  const stateColors = {
    'E': '#4CAF50',  // Green for Exon
    'I': '#FF9800',  // Orange for Intron
    'P': '#2196F3'   // Blue for Promoter
  };

  // Color mapping for DNA bases
  const baseColors = {
    'A': '#E57373',  // Red
    'C': '#64B5F6',  // Blue
    'G': '#81C784',  // Green
    'T': '#FFD54F'   // Yellow
  };

  return (
    <div className="decoded-path-viewer">
      <h3>Decoded Path Visualization</h3>

      {/* DNA Sequence */}
      <div className="sequence-row">
        <label className="row-label">DNA Sequence:</label>
        <div className="sequence-display">
          {dnaSequence.split('').map((base, i) => (
            <span
              key={`base-${i}`}
              className="base-char"
              style={{
                color: baseColors[base.toUpperCase()] || '#333',
                fontWeight: 'bold'
              }}
            >
              {base}
            </span>
          ))}
        </div>
      </div>

      {/* Decoded Hidden States */}
      <div className="sequence-row">
        <label className="row-label">Hidden States:</label>
        <div className="sequence-display">
          {decodedPath.map((state, i) => (
            <span
              key={`state-${i}`}
              className="state-char"
              style={{
                backgroundColor: stateColors[state] || '#999',
                color: 'white',
                padding: '2px 4px',
                margin: '0 1px',
                borderRadius: '3px',
                fontWeight: 'bold',
                display: 'inline-block',
                minWidth: '20px',
                textAlign: 'center'
              }}
            >
              {state}
            </span>
          ))}
        </div>
      </div>

      {/* String representation */}
      <div className="path-string">
        <strong>Path String:</strong> <code>{decodedPathString || decodedPath.join('')}</code>
      </div>

      {/* Legend */}
      <div className="state-legend">
        <strong>Legend:</strong>
        <div className="legend-items">
          <span className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#4CAF50' }}></span>
            E = Exon
          </span>
          <span className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#FF9800' }}></span>
            I = Intron
          </span>
          <span className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#2196F3' }}></span>
            P = Promoter
          </span>
        </div>
      </div>

      <style jsx>{`
        .decoded-path-viewer {
          margin: 20px 0;
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: #f9f9f9;
        }

        .sequence-row {
          margin: 15px 0;
        }

        .row-label {
          display: block;
          font-weight: bold;
          margin-bottom: 5px;
          color: #333;
        }

        .sequence-display {
          font-family: 'Courier New', monospace;
          font-size: 14px;
          padding: 10px;
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
          overflow-x: auto;
          white-space: nowrap;
        }

        .base-char, .state-char {
          margin: 0 1px;
        }

        .path-string {
          margin: 15px 0;
          padding: 10px;
          background: white;
          border-radius: 4px;
        }

        .path-string code {
          background: #e0e0e0;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
        }

        .state-legend {
          margin-top: 15px;
          padding: 10px;
          background: white;
          border-radius: 4px;
        }

        .legend-items {
          display: flex;
          gap: 20px;
          margin-top: 8px;
          flex-wrap: wrap;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .legend-color {
          display: inline-block;
          width: 20px;
          height: 20px;
          border-radius: 3px;
        }
      `}</style>
    </div>
  );
}

export default DecodedPathViewer;
