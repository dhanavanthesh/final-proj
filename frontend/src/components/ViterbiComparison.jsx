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

    </div>
  );
}

export default ViterbiComparison;
