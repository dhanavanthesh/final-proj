export default function Metric({ label, value, unit = '' }) {
  const display = typeof value === 'number' ? value.toFixed(2) : value ?? '—'
  return (
    <div className="metric-card">
      <div className="metric-title">{label}</div>
      <div className="metric-value">{display} {unit}</div>
    </div>
  )
}
