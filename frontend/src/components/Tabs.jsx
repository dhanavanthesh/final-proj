export default function Tabs({ tabs, active, onChange }) {
  return (
    <div className="tabs">
      {tabs.map(t => (
        <button
          key={t.id}
          className={`tab ${active === t.id ? 'active' : ''}`}
          onClick={() => onChange(t.id)}
          aria-pressed={active === t.id}
        >
          {t.icon ? `${t.icon} ` : ''}{t.label}
        </button>
      ))}
    </div>
  )
}
