'use client'
import { useEffect, useState } from 'react'
import { useDonationStore, Donation } from '@/stores/donations'

export function DonationAlert() {
  const [visible, setVisible] = useState<Donation | null>(null)
  const recent = useDonationStore((s) => s.recent)

  useEffect(() => {
    const latest = recent[0]
    if (!latest || latest.type !== 'donation') return
    setVisible(latest)
    const t = setTimeout(() => setVisible(null), 5000)
    return () => clearTimeout(t)
  }, [recent])

  if (!visible) return null

  return (
    <div className="donation-alert fixed top-6 right-6 z-50 slash-card glow-pink"
      style={{ background: 'var(--bg-elevated)', border: '1px solid var(--pink)', padding: '1rem 1.5rem', minWidth: '260px' }}>
      <p className="font-mono text-xs tracking-widest mb-1" style={{ color: 'var(--pink)' }}>DONATION</p>
      <p className="font-mono text-2xl font-semibold" style={{ color: 'var(--pink)' }}>${visible.amount.toFixed(2)}</p>
      <p className="font-mono text-sm mt-1" style={{ color: 'var(--text-primary)' }}>from <strong>{visible.username}</strong></p>
      {visible.message && <p className="font-mono text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>"{visible.message}"</p>}
    </div>
  )
}
