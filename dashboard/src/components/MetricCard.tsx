interface MetricCardProps {
  label: string
  value: string | number
  unit?: string
  delta?: string
  deltaPositive?: boolean
  variant?: 'teal' | 'pink' | 'default'
  className?: string
}

export function MetricCard({ label, value, unit, delta, deltaPositive, variant = 'default', className = '' }: MetricCardProps) {
  const accentColor = variant === 'teal' ? 'var(--teal)' : variant === 'pink' ? 'var(--pink)' : 'var(--text-primary)'
  const glowClass = variant === 'teal' ? 'glow-teal' : variant === 'pink' ? 'glow-pink' : ''
  return (
    <div className={`slash-card ${glowClass} ${className}`}
      style={{
        background: 'var(--bg-elevated)',
        border: `1px solid ${variant !== 'default' ? accentColor + '40' : 'var(--bg-border)'}`,
        padding: '1.25rem 1.5rem',
        position: 'relative',
      }}>
      <div style={{
        position: 'absolute', top: 0, right: 0, width: 16, height: 16,
        background: variant !== 'default' ? accentColor : 'var(--bg-border)',
        clipPath: 'polygon(100% 0, 0 0, 100% 100%)', opacity: 0.6,
      }} />
      <p className="font-mono text-xs tracking-widest mb-2 uppercase" style={{ color: 'var(--text-secondary)' }}>
        {label}
      </p>
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-3xl font-semibold" style={{ color: accentColor }}>{value}</span>
        {unit && <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>{unit}</span>}
      </div>
      {delta && (
        <p className="font-mono text-xs mt-1" style={{ color: deltaPositive ? 'var(--teal)' : 'var(--pink)' }}>
          {deltaPositive ? '\u2191' : '\u2193'} {delta}
        </p>
      )}
    </div>
  )
}
