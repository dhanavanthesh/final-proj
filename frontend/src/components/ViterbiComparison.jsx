import React from 'react';

/**
 * Viterbi Comparison Component
 * Displays side-by-side comparison of Quantum and Classical Viterbi results
 */
export function ViterbiComparison({ quantumResult, classicalResult, comparisonData }) {
  if (!quantumResult && !classicalResult) {
    return null;
  }

  return (
    <div className="viterbi-comparison">
      <h3>Performance Comparison</h3>

      <table className="comparison-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Quantum Viterbi (QVA)</th>
            <th>Classical Viterbi</th>
          </tr>
        </thead>
        <tbody>
          {/* Runtime */}
          <tr>
            <td><strong>Runtime</strong></td>
            <td>{quantumResult?.runtime_ms?.toFixed(2)} ms</td>
            <td>{classicalResult?.runtime_ms?.toFixed(2)} ms</td>
          </tr>

          {/* Decoded Path */}
          <tr>
            <td><strong>Decoded Path</strong></td>
            <td><code>{quantumResult?.decoded_path_string}</code></td>
            <td><code>{classicalResult?.decoded_path_string}</code></td>
          </tr>

          {/* Qubits Used (Quantum only) */}
          {quantumResult?.qubits_used && (
            <tr>
              <td><strong>Qubits Used</strong></td>
              <td>{quantumResult.qubits_used}</td>
              <td className="not-applicable">—</td>
            </tr>
          )}

          {/* Circuit Depth (Quantum only) */}
          {quantumResult?.circuit_depth && (
            <tr>
              <td><strong>Circuit Depth</strong></td>
              <td>{quantumResult.circuit_depth.toFixed(2)}</td>
              <td className="not-applicable">—</td>
            </tr>
          )}

          {/* Total Shots (Quantum only) */}
          {quantumResult?.total_shots && (
            <tr>
              <td><strong>Total Measurements</strong></td>
              <td>{quantumResult.total_shots.toLocaleString()}</td>
              <td className="not-applicable">—</td>
            </tr>
          )}

          {/* Log Probability (Classical only) */}
          {classicalResult?.log_probability && (
            <tr>
              <td><strong>Log Probability</strong></td>
              <td className="not-applicable">—</td>
              <td>{classicalResult.log_probability.toFixed(4)}</td>
            </tr>
          )}

          {/* Sequence Length */}
          <tr>
            <td><strong>Sequence Length</strong></td>
            <td>{quantumResult?.sequence_length || classicalResult?.sequence_length} bases</td>
            <td>{quantumResult?.sequence_length || classicalResult?.sequence_length} bases</td>
          </tr>
        </tbody>
      </table>

      {/* Agreement metrics if comparison data available */}
      {comparisonData && (
        <div className="agreement-metrics">
          <h4>Agreement Analysis</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">{comparisonData.agreement_percent}%</div>
              <div className="metric-label">Path Agreement</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{comparisonData.matches}/{comparisonData.total_positions}</div>
              <div className="metric-label">Matching Positions</div>
            </div>
            {comparisonData.runtime_speedup && (
              <div className="metric-card">
                <div className="metric-value">{comparisonData.runtime_speedup}x</div>
                <div className="metric-label">
                  {comparisonData.runtime_speedup > 1 ? 'Classical Faster' : 'Quantum Faster'}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <style jsx>{`
        .viterbi-comparison {
          margin: 30px 0;
          padding: 20px;
          border: 2px solid #2196F3;
          border-radius: 8px;
          background: #f5f5f5;
        }

        .viterbi-comparison h3 {
          margin-top: 0;
          color: #2196F3;
        }

        .comparison-table {
          width: 100%;
          border-collapse: collapse;
          background: white;
          border-radius: 4px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .comparison-table th {
          background: #2196F3;
          color: white;
          padding: 12px;
          text-align: left;
          font-weight: bold;
        }

        .comparison-table td {
          padding: 10px 12px;
          border-bottom: 1px solid #ddd;
        }

        .comparison-table tr:last-child td {
          border-bottom: none;
        }

        .comparison-table tr:hover {
          background: #f9f9f9;
        }

        .comparison-table code {
          background: #e0e0e0;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
          font-size: 12px;
        }

        .not-applicable {
          color: #999;
          text-align: center;
        }

        .agreement-metrics {
          margin-top: 20px;
          padding: 15px;
          background: white;
          border-radius: 4px;
        }

        .agreement-metrics h4 {
          margin-top: 0;
          color: #333;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 15px;
          margin-top: 15px;
        }

        .metric-card {
          padding: 15px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 8px;
          text-align: center;
          color: white;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .metric-value {
          font-size: 28px;
          font-weight: bold;
          margin-bottom: 5px;
        }

        .metric-label {
          font-size: 12px;
          opacity: 0.9;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      `}</style>
    </div>
  );
}

export default ViterbiComparison;
