'use client'
import { useStreamStore } from '@/stores/stream'

export function StatusBar() {
  const isLive = useStreamStore((s) => s.isLive)
  const viewerCount = useStreamStore((s) => s.viewerCount)
  const uptime = useStreamStore((s) => s.uptime)
  return (
    <div className="fixed bottom-0 left-16 right-0 h-8 flex items-center px-4 gap-6 font-mono text-xs z-40"
      style={{ background: 'var(--bg-surface)', borderTop: '1px solid var(--bg-border)', color: 'var(--text-secondary)' }}>
      <span style={{ color: isLive ? 'var(--teal)' : 'var(--pink)' }}>
        {isLive ? '\u25CF LIVE' : '\u25CB OFFLINE'}
      </span>
      <span>{viewerCount.toLocaleString()} viewers</span>
      <span>uptime {uptime}</span>
      <span className="ml-auto">autonomous-vtuber v0.1</span>
    </div>
  )
}
