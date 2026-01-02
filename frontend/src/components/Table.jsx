export default function Table({ columns, rows }) {
  return (
    <table className="table">
      <thead>
        <tr>
          {columns.map((c, i) => (
            <th key={i} className={c.className}>{c.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr><td colSpan={columns.length} className="muted">No data</td></tr>
        ) : rows.map((row, ri) => (
          <tr key={ri}>
            {row.map((cell, ci) => (
              <td key={ci}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
