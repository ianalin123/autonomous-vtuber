'use client'
import { useDonationStore } from '@/stores/donations'

export function DonationFeed() {
  const recent = useDonationStore((s) => s.recent)
  const mockRecent = recent.length === 0 ? [
    { id: '1', username: 'viewer123', amount: 5.0, message: 'love the stream!', timestamp: new Date().toISOString(), type: 'donation' as const },
    { id: '2', username: 'subber99', amount: 0, message: '', timestamp: new Date().toISOString(), type: 'sub' as const },
    { id: '3', username: 'bitslord', amount: 1.0, message: 'PogChamp', timestamp: new Date().toISOString(), type: 'bits' as const },
  ] : recent

  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)', padding: '1.25rem', height: '320px', overflowY: 'auto' }}>
      <p className="font-mono text-xs tracking-widest mb-3 uppercase" style={{ color: 'var(--text-secondary)' }}>
        Donation Feed
      </p>
      <div className="flex flex-col gap-2">
        {mockRecent.map((d) => (
          <div key={d.id} className="flex items-start gap-3 font-mono text-xs"
            style={{ borderLeft: `2px solid ${d.type === 'donation' ? 'var(--pink)' : 'var(--teal)'}`, paddingLeft: '0.5rem' }}>
            <span style={{ color: d.type === 'donation' ? 'var(--pink)' : 'var(--teal)', minWidth: '3.5rem' }}>
              {d.type === 'donation' ? `$${d.amount.toFixed(2)}` : d.type === 'sub' ? 'SUB' : `${d.amount * 100}b`}
            </span>
            <div>
              <span style={{ color: 'var(--text-primary)' }}>{d.username}</span>
              {d.message && <p style={{ color: 'var(--text-secondary)' }} className="mt-0.5">{d.message}</p>}
            </div>
            <span className="ml-auto" style={{ color: 'var(--text-secondary)', flexShrink: 0 }}>
              {new Date(d.timestamp).toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
