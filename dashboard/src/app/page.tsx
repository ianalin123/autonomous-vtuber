import { MetricCard } from '@/components/MetricCard'
import { RevenueChart } from '@/components/RevenueChart'
import { DonationFeed } from '@/components/DonationFeed'
import { DonationAlert } from '@/components/DonationAlert'
import { RealtimeProvider } from './RealtimeProvider'

export default function DashboardPage() {
  return (
    <RealtimeProvider>
      <DonationAlert />
      <div className="flex items-center justify-between mb-8 reveal reveal-1">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Syne' }}>Stream Ops</h1>
          <p className="font-mono text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>AIKO_NATSUKI &middot; AUTONOMOUS</p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs px-3 py-1.5"
          style={{ border: '1px solid var(--teal)', color: 'var(--teal)' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--teal)',
            display: 'inline-block', boxShadow: '0 0 8px var(--teal)' }} />
          LIVE
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <MetricCard label="Viewers"         value="\u2014" unit="live"  variant="teal"    className="reveal reveal-2" />
        <MetricCard label="Chat / min"       value="\u2014" unit="msg"   variant="default" className="reveal reveal-3" />
        <MetricCard label="Revenue Today"    value="\u2014" unit="USD"   variant="teal"    className="reveal reveal-4" />
        <MetricCard label="Engagement Score" value="\u2014" unit="/ 100" variant="default" className="reveal reveal-5" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 flex flex-col gap-4">
          <RevenueChart />
          <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)', padding: '1.25rem' }}>
            <p className="font-mono text-xs tracking-widest mb-2 uppercase" style={{ color: 'var(--text-secondary)' }}>Current Activity</p>
            <p className="font-mono text-lg" style={{ color: 'var(--text-primary)' }}>idle</p>
          </div>
        </div>
        <div><DonationFeed /></div>
      </div>
    </RealtimeProvider>
  )
}
