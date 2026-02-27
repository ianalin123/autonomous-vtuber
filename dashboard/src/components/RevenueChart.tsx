'use client'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useMetricsStore } from '@/stores/metrics'

export function RevenueChart() {
  const timeline = useMetricsStore((s) => s.revenueTimeline)
  const mockData = timeline.length === 0 ? [
    { timestamp: '20:00', cumulative: 0 },
    { timestamp: '20:30', cumulative: 12.5 },
    { timestamp: '21:00', cumulative: 31 },
    { timestamp: '21:30', cumulative: 47 },
    { timestamp: '22:00', cumulative: 89 },
  ] : timeline

  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)', padding: '1.25rem' }}>
      <p className="font-mono text-xs tracking-widest mb-4 uppercase" style={{ color: 'var(--text-secondary)' }}>
        Revenue Timeline
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={mockData}>
          <defs>
            <linearGradient id="tealGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#00ffe7" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00ffe7" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="timestamp"
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 10, fill: '#6b7399' }}
            axisLine={false} tickLine={false} />
          <YAxis tick={{ fontFamily: 'IBM Plex Mono', fontSize: 10, fill: '#6b7399' }}
            axisLine={false} tickLine={false}
            tickFormatter={(v) => `$${v}`} />
          <Tooltip
            contentStyle={{ background: '#0d0f1a', border: '1px solid #00ffe7', fontFamily: 'IBM Plex Mono', fontSize: 11, color: '#e8eaf0' }}
            formatter={(v) => [`$${Number(v).toFixed(2)}`, 'Revenue']} />
          <Area type="monotone" dataKey="cumulative" stroke="#00ffe7" strokeWidth={2} fill="url(#tealGrad)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
