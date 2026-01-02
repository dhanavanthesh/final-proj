import React, { useEffect, useRef, useState } from 'react'
import Chart from 'chart.js/auto'
import Metric from './components/Metric.jsx'
import Tabs from './components/Tabs.jsx'
import Table from './components/Table.jsx'
import Helix3D from './components/Helix3D.jsx'
import HMMModelSelector from './components/HMMModelSelector.jsx'
import DecodedPathViewer from './components/DecodedPathViewer.jsx'
import ViterbiComparison from './components/ViterbiComparison.jsx'

const API_BASE = 'http://localhost:8000'

export default function App() {
  const [sequence1, setSequence1] = useState('')
  const [sequence2, setSequence2] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('viterbi')

  // Original algorithm results
  const [alignResult, setAlignResult] = useState(null)
  const [motifResult, setMotifResult] = useState(null)
  const [variantResult, setVariantResult] = useState(null)
  const [swResult, setSwResult] = useState(null)
  const [blastResults, setBlastResults] = useState(null)
  const [helixData, setHelixData] = useState(null)
  const [circuitData, setCircuitData] = useState(null)
  const [runs, setRuns] = useState([])
  const [runsLoading, setRunsLoading] = useState(false)

  // Viterbi-specific state
  const [hmmModel, setHmmModel] = useState('2-state-exon-intron')
  const [decodingMethod, setDecodingMethod] = useState('quantum') // 'quantum' or 'classical' or 'compare'
  const [viterbiResult, setViterbiResult] = useState(null)
  const [quantumResult, setQuantumResult] = useState(null)
  const [classicalResult, setClassicalResult] = useState(null)
  const [comparisonData, setComparisonData] = useState(null)
  const [viterbiAnimationFrames, setViterbiAnimationFrames] = useState([])
  const [viterbiHelixData, setViterbiHelixData] = useState(null)

  const chartRef = useRef(null)
  const chartInstanceRef = useRef(null)

  useEffect(() => {
    const loadSamples = async () => {
      try {
        const res = await fetch(`${API_BASE}/samples`)
        if (res.ok) {
          const data = await res.json()
          setSequence1(data.sequence1 || 'ATGCCTACGCATGCTACCTGCTGCTGATCCGCCT')
          setSequence2(data.sequence2 || '')
        }
      } catch {}
    }
    loadSamples()
    fetchRuns()
  }, [])

  const fetchRuns = async () => {
    setRunsLoading(true)
    try {
      const res = await fetch(`${API_BASE}/runs`)
      if (res.ok) setRuns(await res.json())
    } catch {}
    finally { setRunsLoading(false) }
  }

  useEffect(() => {
    // VQE chart rendering (convergence)
    if (alignResult?.results?.convergence && chartRef.current) {
      const ctx = chartRef.current.getContext('2d')
      if (chartInstanceRef.current) chartInstanceRef.current.destroy()
      chartInstanceRef.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: alignResult.results.convergence.map((_, i) => `Iter ${i}`),
          datasets: [{
            label: 'Energy (VQE)',
            data: alignResult.results.convergence,
            borderColor: '#0a5ec0',
            backgroundColor: 'rgba(10, 94, 192, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      })
    }
  }, [alignResult])

  // ========== VITERBI ALGORITHM HANDLERS ==========

  const handleViterbi = async () => {
    if (!sequence1 || sequence1.length === 0) {
      setError('Please enter a DNA sequence');
      return;
    }

    setError(''); setLoading(true)
    setViterbiResult(null)
    setQuantumResult(null)
    setClassicalResult(null)
    setComparisonData(null)
    setViterbiAnimationFrames([])
    setViterbiHelixData(null)

    try {
      let endpoint = '';
      let requestBody = {
        sequence: sequence1.toUpperCase(),
        hmm_model: hmmModel,
        shots: 1024
      };

      if (decodingMethod === 'quantum') {
        endpoint = '/viterbi/quantum';
      } else if (decodingMethod === 'classical') {
        endpoint = '/viterbi/classical';
      } else if (decodingMethod === 'compare') {
        endpoint = '/viterbi/compare';
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      if (!res.ok) {
        let msg = 'Viterbi decoding failed';
        try {
          const data = await res.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }

      const data = await res.json()

      if (decodingMethod === 'compare') {
        setQuantumResult(data.quantum)
        setClassicalResult(data.classical)
        setComparisonData(data.comparison)
      } else if (decodingMethod === 'quantum') {
        setViterbiResult(data.results)
        setQuantumResult(data.results)
      } else if (decodingMethod === 'classical') {
        setViterbiResult(data.results)
        setClassicalResult(data.results)
      }

      // Fetch animation frames and helix visualization for Viterbi
      try {
        // Fetch animation frames
        const animRes = await fetch(`${API_BASE}/viterbi/animation-frames`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sequence: sequence1.toUpperCase(),
            hmm_model: hmmModel
          })
        });
        if (animRes.ok) {
          const animData = await animRes.json();
          setViterbiAnimationFrames(animData.frames || []);
        }

        // Fetch helix visualization
        const helixRes = await fetch(`${API_BASE}/visualize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sequence: sequence1.toUpperCase(), type: 'helix' })
        });
        if (helixRes.ok) {
          const helixData = await helixRes.json();
          setViterbiHelixData(helixData);
        }
      } catch (visualErr) {
        console.warn('Visualization loading failed:', visualErr);
        // Don't fail the whole operation if visualization fails
      }

      fetchRuns()
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  // ========== ORIGINAL ALGORITHM HANDLERS ==========

  const handleAlign = async () => {
    setError(''); setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/align`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence1, sequence2 })
      })
      if (!res.ok) {
        let msg = 'Alignment failed';
        try {
          const data = await res.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      setAlignResult(await res.json())
      fetchRuns()
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  const handleMotif = async () => {
    setError(''); setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/find-motifs`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequences: [sequence1, sequence2], motif_length: 8 })
      })
      if (!res.ok) {
        let msg = 'Motif failed';
        try {
          const data = await res.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      setMotifResult(await res.json())
      fetchRuns()
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  const handleVariant = async () => {
    setError(''); setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/detect-variant`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence: sequence1 })
      })
      if (!res.ok) {
        let msg = 'Variant failed';
        try {
          const data = await res.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      setVariantResult(await res.json())
      fetchRuns()
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  const handleSmithWaterman = async () => {
    setError(''); setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/smith-waterman`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence1, sequence2 })
      })
      if (!res.ok) {
        let msg = 'SW failed';
        try {
          const data = await res.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      setSwResult(await res.json())
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  const handleBlastSearch = async () => {
    setError(''); setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/blast-search`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequences: [sequence1, sequence2], motif_length: 8 })
      })
      if (!res.ok) {
        let msg = 'BLAST failed';
        try {
          const data = await res.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      setBlastResults(await res.json())
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  const handleVisualize = async () => {
    setError(''); setLoading(true)
    try {
      // Fetch helix visualization
      const helixRes = await fetch(`${API_BASE}/visualize`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence: sequence1, type: 'helix' })
      });
      if (!helixRes.ok) {
        let msg = 'Helix viz failed';
        try {
          const data = await helixRes.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      const helixData = await helixRes.json();
      setHelixData(helixData);

      // Fetch circuit visualization
      const circuitRes = await fetch(`${API_BASE}/visualize`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence: sequence1, type: 'circuit' })
      });
      if (!circuitRes.ok) {
        let msg = 'Circuit viz failed';
        try {
          const data = await circuitRes.json();
          msg = data.detail || JSON.stringify(data);
        } catch (e) {}
        throw new Error(msg);
      }
      const circuitData = await circuitRes.json();
      setCircuitData(circuitData);
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  const exportJSON = () => {
    const data = {
      timestamp: new Date().toISOString(),
      sequences: { sequence1, sequence2 },
      viterbi: {
        hmmModel,
        decodingMethod,
        viterbiResult,
        quantumResult,
        classicalResult,
        comparisonData
      },
      alignResult,
      motifResult,
      variantResult,
      swResult,
      blastResults,
      visualizations: { helixData, circuitData }
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `qgenome-results-${Date.now()}.json`; a.click()
    URL.revokeObjectURL(url)
  }

  function formatError(err) {
    if (!err) return '';
    if (typeof err === 'string') return err;
    if (err.message) return err.message;
    if (Array.isArray(err)) return err.map(formatError).join(', ');
    if (typeof err === 'object') return JSON.stringify(err);
    return String(err);
  }

  return (
    <div>
      <header>
        <h1>🧬 QGENOME</h1>
        <p>Quantum Viterbi DNA Decoder • Real-time Sequence Alignment & Analysis</p>
      </header>
      <div className="container">
        {error && <div className="error-message">❌ Error: {formatError(error)}</div>}

        <div className="grid grid-2">
          <div className="card">
            <label>Sequence 1 (Query)</label>
            <textarea
              value={sequence1}
              onChange={e => setSequence1(e.target.value.toUpperCase())}
              placeholder="Enter DNA (ATGC)..."
              disabled={loading}
              rows={3}
            />
          </div>
          <div className="card">
            <label>Sequence 2 (Subject - for alignment)</label>
            <textarea
              value={sequence2}
              onChange={e => setSequence2(e.target.value.toUpperCase())}
              placeholder="Enter DNA (ATGC)..."
              disabled={loading}
              rows={3}
            />
          </div>
        </div>

        <Tabs
          tabs={[
            { id: 'viterbi', label: 'Viterbi (QVA)', icon: '🔬' },
            { id: 'quantum', label: 'Quantum', icon: '⚛️' },
            { id: 'classical', label: 'Classical', icon: '🔬' },
            { id: 'visualizations', label: 'Viz', icon: '📊' },
            { id: 'history', label: 'History', icon: '📈' },
          ]}
          active={activeTab}
          onChange={setActiveTab}
        />

        {/* ========== VITERBI TAB (CORE QVA FUNCTIONALITY) ========== */}
        {activeTab === 'viterbi' && (
          <>
            <div className="card">
              <h3>🧬 Quantum Viterbi Algorithm (QVA) - Core QGENOME Functionality</h3>
              <p className="muted">
                Decode hidden genomic states (Exon/Intron/Promoter) using quantum-enhanced HMM inference
              </p>

              {/* HMM Model Selector */}
              <HMMModelSelector
                selected={hmmModel}
                onChange={setHmmModel}
              />

              {/* Decoding Method Selection */}
              <div className="method-selector" style={{ marginTop: '20px' }}>
                <label><strong>Decoding Method:</strong></label>
                <div className="flex" style={{ marginTop: '10px', gap: '10px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      value="quantum"
                      checked={decodingMethod === 'quantum'}
                      onChange={(e) => setDecodingMethod(e.target.value)}
                      disabled={loading}
                    />
                    <span style={{ marginLeft: '8px' }}>⚛️ Quantum Viterbi (QVA)</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      value="classical"
                      checked={decodingMethod === 'classical'}
                      onChange={(e) => setDecodingMethod(e.target.value)}
                      disabled={loading}
                    />
                    <span style={{ marginLeft: '8px' }}>📊 Classical Viterbi (hmmlearn)</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      value="compare"
                      checked={decodingMethod === 'compare'}
                      onChange={(e) => setDecodingMethod(e.target.value)}
                      disabled={loading}
                    />
                    <span style={{ marginLeft: '8px' }}>🔍 Compare Both Methods</span>
                  </label>
                </div>
              </div>

              {/* Run Button */}
              <div style={{ marginTop: '20px' }}>
                <button
                  onClick={handleViterbi}
                  disabled={loading || !sequence1}
                  style={{ width: '100%', padding: '12px', fontSize: '16px' }}
                >
                  {loading ? '⏳ Processing...' : '🚀 Run Viterbi Decoding'}
                </button>
              </div>
            </div>

            {/* Display Results */}
            {decodingMethod === 'compare' && quantumResult && classicalResult && (
              <>
                {/* Decoded Path for Quantum */}
                <DecodedPathViewer
                  dnaSequence={sequence1}
                  decodedPath={quantumResult.decoded_path}
                  decodedPathString={quantumResult.decoded_path_string}
                />

                {/* Comparison Table */}
                <ViterbiComparison
                  quantumResult={quantumResult}
                  classicalResult={classicalResult}
                  comparisonData={comparisonData}
                />

                {/* 3D Visualization for Comparison Mode */}
                {viterbiHelixData && viterbiHelixData.data && (
                  <div className="card">
                    <h3>3D DNA Helix with Quantum Decoding Animation</h3>
                    <div className="muted" style={{ marginBottom: '1rem' }}>
                      Visualize the quantum decoding process (showing quantum results)
                    </div>
                    <Helix3D
                      bases={viterbiHelixData.data?.bases || []}
                      hydrogenBonds={viterbiHelixData.data?.hydrogen_bonds || []}
                      animationFrames={viterbiAnimationFrames}
                      showHydrogenBonds={true}
                      autoRotate={false}
                    />
                    <div className="muted" style={{ marginTop: '1rem', textAlign: 'center' }}>
                      💡 Interactive Controls: Drag to rotate • Scroll to zoom • Right-click to pan
                      {viterbiAnimationFrames.length > 0 && ' • Play animation to see decoding process'}
                    </div>
                  </div>
                )}
              </>
            )}

            {decodingMethod === 'quantum' && viterbiResult && (
              <>
                <DecodedPathViewer
                  dnaSequence={sequence1}
                  decodedPath={viterbiResult.decoded_path}
                  decodedPathString={viterbiResult.decoded_path_string}
                />

                <div className="card">
                  <h3>Quantum Metrics</h3>
                  <div className="metrics">
                    <Metric label="Qubits Used" value={viterbiResult.qubits_used} />
                    <Metric label="Circuit Depth" value={viterbiResult.circuit_depth?.toFixed(2)} />
                    <Metric label="Runtime" value={viterbiResult.runtime_ms?.toFixed(2)} unit="ms" />
                    <Metric label="Total Shots" value={viterbiResult.total_shots?.toLocaleString()} />
                  </div>
                </div>

                {viterbiHelixData && viterbiHelixData.data && (
                  <div className="card">
                    <h3>3D DNA Helix with Decoding Animation</h3>
                    <div className="muted" style={{ marginBottom: '1rem' }}>
                      Watch the quantum decoding process unfold in real-time 3D visualization
                    </div>
                    <Helix3D
                      bases={viterbiHelixData.data?.bases || []}
                      hydrogenBonds={viterbiHelixData.data?.hydrogen_bonds || []}
                      animationFrames={viterbiAnimationFrames}
                      showHydrogenBonds={true}
                      autoRotate={false}
                    />
                    <div className="muted" style={{ marginTop: '1rem', textAlign: 'center' }}>
                      💡 Interactive Controls: Drag to rotate • Scroll to zoom • Right-click to pan
                      {viterbiAnimationFrames.length > 0 && ' • Play animation to see decoding process'}
                    </div>
                  </div>
                )}
              </>
            )}

            {decodingMethod === 'classical' && viterbiResult && (
              <>
                <DecodedPathViewer
                  dnaSequence={sequence1}
                  decodedPath={viterbiResult.decoded_path}
                  decodedPathString={viterbiResult.decoded_path_string}
                />

                <div className="card">
                  <h3>Classical Metrics</h3>
                  <div className="metrics">
                    <Metric label="Runtime" value={viterbiResult.runtime_ms?.toFixed(2)} unit="ms" />
                    <Metric label="Log Probability" value={viterbiResult.log_probability?.toFixed(4)} />
                    <Metric label="Method" value={viterbiResult.method} />
                  </div>
                </div>

                {viterbiHelixData && viterbiHelixData.data && (
                  <div className="card">
                    <h3>3D DNA Helix with Decoding Animation</h3>
                    <div className="muted" style={{ marginBottom: '1rem' }}>
                      Watch the classical decoding process unfold in real-time 3D visualization
                    </div>
                    <Helix3D
                      bases={viterbiHelixData.data?.bases || []}
                      hydrogenBonds={viterbiHelixData.data?.hydrogen_bonds || []}
                      animationFrames={viterbiAnimationFrames}
                      showHydrogenBonds={true}
                      autoRotate={false}
                    />
                    <div className="muted" style={{ marginTop: '1rem', textAlign: 'center' }}>
                      💡 Interactive Controls: Drag to rotate • Scroll to zoom • Right-click to pan
                      {viterbiAnimationFrames.length > 0 && ' • Play animation to see decoding process'}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* ========== QUANTUM TAB (OTHER ALGORITHMS) ========== */}
        {activeTab === 'quantum' && (
          <>
            <div className="card">
              <h3>Select Quantum Algorithm</h3>
              <div className="flex">
                <button onClick={handleAlign} disabled={loading || !sequence1 || !sequence2}>{loading ? '⏳' : '⚛️'} VQE Alignment</button>
                <button onClick={handleMotif} disabled={loading || !sequence1}>{loading ? '⏳' : '🔍'} QAOA Motif</button>
                <button onClick={handleVariant} disabled={loading || !sequence1}>{loading ? '⏳' : '🧪'} QCNN Variant</button>
              </div>
            </div>

            {alignResult && (
              <div className="card vqe-card" style={{ marginBottom: '12px' }}>
                <h3 style={{ marginBottom: '10px' }}>VQE Alignment Results</h3>
                <div className="metrics" style={{ marginBottom: alignResult.results?.convergence?.length > 0 ? '18px' : '0' }}>
                  <Metric label="Score" value={alignResult.results?.alignment_score} unit="%" />
                  <Metric label="Energy" value={alignResult.results?.final_energy} unit="Eh" />
                  <Metric label="Qubits" value={alignResult.results?.qubits} />
                  <Metric label="Iterations" value={alignResult.results?.convergence?.length || 0} />
                </div>
                {alignResult.results?.convergence?.length > 0 && (
                  <div style={{ height: '220px', marginTop: '0' }}>
                    <canvas ref={chartRef}></canvas>
                  </div>
                )}
              </div>
            )}
            {motifResult && (
              <div className="card" style={{ marginBottom: '18px' }}>
                <h3>QAOA Motif Results</h3>
                <div className="metrics">
                  <Metric label="Motif" value={motifResult.results?.motif} />
                  <Metric label="Score" value={motifResult.results?.score} />
                  <Metric label="IC" value={motifResult.results?.information_content} unit="bits" />
                </div>
              </div>
            )}
            {variantResult && (
              <div className="card">
                <h3>QCNN Variant Results</h3>
                <div className="metrics">
                  <Metric label="Prob" value={variantResult.results?.pathogenic_probability} unit="%" />
                  <Metric label="Classification" value={variantResult.results?.classification} />
                </div>
              </div>
            )}
          </>
        )}

        {/* ========== CLASSICAL TAB ========== */}
        {activeTab === 'classical' && (
          <div className="grid">
            <div className="card algo-card">
              <h4>Smith-Waterman</h4>
              <p className="muted">Local alignment</p>
              <button onClick={handleSmithWaterman} disabled={loading || !sequence1 || !sequence2}>▶️ Run</button>
              {swResult && <div className="metrics" style={{marginTop:'12px'}}><Metric label="Score" value={swResult.results?.score ?? swResult.score} /></div>}
            </div>
            <div className="card algo-card">
              <h4>BLAST Search</h4>
              <p className="muted">Word-based search</p>
              <button onClick={handleBlastSearch} disabled={loading || !sequence1 || !sequence2}>▶️ Run</button>
              {blastResults && Array.isArray(blastResults.results) && blastResults.results.length > 0 && (
                <div className="metrics" style={{marginTop:'12px'}}>
                  <Metric label="Top Score" value={blastResults.results[0]?.alignment_score} />
                  <Metric label="Word Matches" value={blastResults.results[0]?.word_matches} />
                  <Metric label="E-value" value={blastResults.results[0]?.evalue?.toFixed(4)} />
                </div>
              )}
              {blastResults && Array.isArray(blastResults.results) && blastResults.results.length === 0 && (
                <div className="muted" style={{marginTop:'12px'}}>No significant matches found.</div>
              )}
            </div>
          </div>
        )}

        {/* ========== VISUALIZATIONS TAB ========== */}
        {activeTab === 'visualizations' && (
          <div className="grid">
            <div className="card">
              <h3>Visualization Generator</h3>
              <button onClick={handleVisualize} disabled={loading || !sequence1}>🎨 Generate</button>
            </div>
            {helixData && helixData.data && (
              <div className="card">
                <h3>3D DNA Helix (Interactive)</h3>
                <div className="muted">
                  Sequence: {helixData.data?.sequence_length} bp | Turns: {helixData.data?.helical_turn?.toFixed(2)}
                  {helixData.data?.with_complementary && ' | Double Helix with H-Bonds'}
                </div>
                <Helix3D
                  bases={helixData.data?.bases || []}
                  hydrogenBonds={helixData.data?.hydrogen_bonds || []}
                  animationFrames={[]}
                  showHydrogenBonds={true}
                  autoRotate={true}
                />
                <div className="muted" style={{ marginTop: '1rem', textAlign: 'center' }}>
                  💡 Use mouse to interact: Drag to rotate, Scroll to zoom, Right-click to pan
                </div>
                <Table
                  columns={[{ label: 'Base' }, { label: 'Pos' }, { label: 'Coord' }, { label: 'Color' }]}
                  rows={helixData.data?.bases?.slice(0, 10).map(b => [
                    <span style={{ color: b.color, fontWeight: 'bold' }}>{b.base}</span>,
                    b.index,
                    <span className="muted" style={{ fontSize: '11px' }}>
                      ({b.position[0].toFixed(2)}, {b.position[1].toFixed(2)}, {b.position[2].toFixed(2)})
                    </span>,
                    <div style={{ width:'16px', height:'16px', background: b.color, borderRadius:'3px' }}></div>
                  ])}
                />
              </div>
            )}
            {circuitData && circuitData.data && (
              <div className="card">
                <h3>Quantum Circuit</h3>
                <div className="muted">Qubits: {circuitData.data?.num_qubits} | Depth: {circuitData.data?.depth}</div>
                <Table
                  columns={[{ label: 'Gate' }, { label: 'Qubits' }, { label: 'Label' }]}
                  rows={circuitData.data?.gates?.slice(0, 10).map(g => [
                    <span className="pill">{g.type}</span>,
                    `[${g.qubits.join(',')}]`,
                    <span className="muted">{g.label}</span>
                  ])}
                />
              </div>
            )}
          </div>
        )}

        {/* ========== HISTORY TAB ========== */}
        {activeTab === 'history' && (
          <div className="card">
            <h3>Recent Runs</h3>
            {runsLoading ? <div className="muted">Loading...</div> : (
              <Table
                columns={[{ label: 'Type' }, { label: 'Score' }, { label: 'Time' }]}
                rows={runs.map(r => [
                  <span className="pill">{r.run_type}</span>,
                  r.score?.toFixed(2) || 'N/A',
                  <span className="muted">{new Date(r.created_at).toLocaleString()}</span>
                ])}
              />
            )}
          </div>
        )}

        <div className="grid grid-2">
          <div className="card">
            <h3>Export Results</h3>
            <button onClick={exportJSON} disabled={!viterbiResult && !alignResult && !motifResult && !variantResult}>📥 Download JSON</button>
          </div>
          <div className="card">
            <h3>Information</h3>
            <p className="muted">• All computations run locally</p>
            <p className="muted">• Qiskit Aer Simulator • MongoDB persistence</p>
            <p className="muted">• Supports sequences up to 500 bp</p>
          </div>
        </div>

        <footer>🔬 QGENOME © 2025 • Built with React, FastAPI, Qiskit & NumPy</footer>
      </div>
    </div>
  )
}
