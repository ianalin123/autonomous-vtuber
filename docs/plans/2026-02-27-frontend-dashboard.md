# VTuber Analytics Dashboard — Frontend Agent Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a real-time stream ops dashboard in Next.js for monitoring and controlling the autonomous VTuber — live metrics, revenue tracking, viewer analytics, and stream override controls.

**Architecture:** Next.js 15 App Router, edge-compatible. Server Components for initial data hydration from the FastAPI backend. Client Components for real-time WebSocket/SSE updates. Zustand for client state. Recharts for revenue timelines. Tailwind + custom CSS variables for the "neural terminal" dark theme. Deployed to Render as a web service fronting the FastAPI backend.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS v4, Zustand, Recharts, `eventsource` / native WebSocket, IBM Plex Mono + Syne fonts via `next/font`, Render web service.

**Depends on:** Phase 3.5 API endpoints from backend plan (can develop against mock data first).

---

## Aesthetic Direction

**Theme: "Anime Stream Ops Terminal"**

Dark navy-black base (`#07080f`) with electric teal accents (`#00ffe7`) for live data and hot pink (`#ff2d7e`) for donation/alert states. Monospace numbers everywhere. Grid lines like graph paper at 8% opacity. Glowing borders on active metric cards. A diagonal slash motif (clip-path or border tricks) breaking up rectangular predictability.

**Fonts:**
- `IBM Plex Mono` — all numbers, live metrics, timestamps
- `Syne` — labels, headings, nav items

**Motion:** Staggered card reveal on load. Number counters animate on value change (CSS `counter-increment` trick or JS). Donation alerts slide in from the right with a pink glow pulse. Chat feed scrolls with momentum blur.

---

## Credentials Placement

### Local Development

```bash
# dashboard/.env.local  (gitignored)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/metrics
API_SECRET=your_internal_secret_for_server_routes
```

### Render Deployment

In Render Dashboard → your web service → **Environment**:
```
NEXT_PUBLIC_API_URL=https://api.your-render-app.onrender.com
NEXT_PUBLIC_WS_URL=wss://api.your-render-app.onrender.com/ws/metrics
API_SECRET=[generate with: openssl rand -hex 32]
```

---

## Worker Epsilon Spawn Instructions

Run-in spawns Worker Epsilon in parallel with Phase 3 backend workers:

```
You are Worker Epsilon (Frontend Dashboard) in the Autonomous VTuber swarm.
Root: /Users/ianalin/Desktop/autonomous-vtuber
Your directory: dashboard/  (Next.js app, isolated from Python backend)
Your branch: feat/dashboard
Backend API base: http://localhost:8000 (mock during development)
Use Context7 MCP to get Next.js 15 and Tailwind v4 docs before implementing.
Use frontend-design skill aesthetics: dark navy, teal/pink accents, IBM Plex Mono + Syne.
Commit after every task with conventional commits.
Message Run-in: "EPSILON READY" when Phase F1 complete.
```

---

## Phase F0 — Scaffold (Worker Epsilon solo)

### Task F0.1: Bootstrap Next.js app

**Files:**
- Create: `dashboard/` (entire Next.js app)

**Step 1: Create Next.js app**

```bash
cd /Users/ianalin/Desktop/autonomous-vtuber
npx create-next-app@latest dashboard \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-eslint
```

**Step 2: Install dependencies**

```bash
cd dashboard
npm install zustand recharts eventsource-parser
npm install -D @types/node
```

**Step 3: Verify dev server starts**

```bash
npm run dev
```
Expected: `http://localhost:3000` loads default Next.js page.

**Step 4: Commit**

```bash
git add dashboard/
git commit -m "chore: scaffold Next.js 15 dashboard app"
```

---

## Phase F1 — Design System & Layout (parallel-ready)

### Task F1.1: Global CSS design system

**Files:**
- Modify: `dashboard/src/app/globals.css`

```css
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Syne:wght@400;600;700;800&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Core palette */
  --bg-void: #07080f;
  --bg-surface: #0d0f1a;
  --bg-elevated: #12152a;
  --bg-border: rgba(255, 255, 255, 0.06);

  /* Accents */
  --teal: #00ffe7;
  --teal-dim: rgba(0, 255, 231, 0.15);
  --teal-glow: 0 0 20px rgba(0, 255, 231, 0.4);
  --pink: #ff2d7e;
  --pink-dim: rgba(255, 45, 126, 0.15);
  --pink-glow: 0 0 20px rgba(255, 45, 126, 0.5);

  /* Text */
  --text-primary: #e8eaf0;
  --text-secondary: #6b7399;
  --text-mono: #00ffe7;

  /* Graph paper grid */
  --grid: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Cpath d='M 40 0 L 0 0 0 40' fill='none' stroke='rgba(255,255,255,0.04)' stroke-width='1'/%3E%3C/svg%3E");
}

* { box-sizing: border-box; margin: 0; }

body {
  background-color: var(--bg-void);
  background-image: var(--grid);
  color: var(--text-primary);
  font-family: 'Syne', sans-serif;
  -webkit-font-smoothing: antialiased;
}

.font-mono { font-family: 'IBM Plex Mono', monospace; }

/* Glow variants */
.glow-teal { box-shadow: var(--teal-glow); }
.glow-pink  { box-shadow: var(--pink-glow); }

/* Slash accent — diagonal top-right corner clip */
.slash-card {
  clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%);
}

/* Animated number pulse */
@keyframes value-flash {
  0%   { color: var(--text-primary); }
  50%  { color: var(--teal); }
  100% { color: var(--text-primary); }
}
.value-updated { animation: value-flash 0.6s ease-out; }

/* Donation alert slide-in */
@keyframes alert-in {
  from { transform: translateX(120%); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}
.donation-alert { animation: alert-in 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards; }

/* Staggered load reveals */
@keyframes reveal-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.reveal { opacity: 0; animation: reveal-up 0.5s ease forwards; }
.reveal-1 { animation-delay: 0.05s; }
.reveal-2 { animation-delay: 0.10s; }
.reveal-3 { animation-delay: 0.15s; }
.reveal-4 { animation-delay: 0.20s; }
.reveal-5 { animation-delay: 0.25s; }
.reveal-6 { animation-delay: 0.30s; }
```

**Step 2: Verify styles load**

Run dev server, open browser. Expected: dark background with grid lines.

**Step 3: Commit**

```bash
git add dashboard/src/app/globals.css
git commit -m "feat: design system CSS - dark terminal theme, animations"
```

---

### Task F1.2: Shell layout with nav

**Files:**
- Modify: `dashboard/src/app/layout.tsx`
- Create: `dashboard/src/components/Sidebar.tsx`
- Create: `dashboard/src/components/StatusBar.tsx`

**Step 1: Write test for Sidebar**

```typescript
// dashboard/src/components/__tests__/Sidebar.test.tsx
import { render, screen } from '@testing-library/react'
import { Sidebar } from '../Sidebar'

test('renders nav links', () => {
  render(<Sidebar />)
  expect(screen.getByText('Dashboard')).toBeInTheDocument()
  expect(screen.getByText('Revenue')).toBeInTheDocument()
  expect(screen.getByText('Viewers')).toBeInTheDocument()
  expect(screen.getByText('Streams')).toBeInTheDocument()
})
```

**Step 2: Install test deps**

```bash
cd dashboard && npm install -D jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom @types/jest ts-jest
```

Run: `npm test -- --testPathPattern=Sidebar`
Expected: FAIL

**Step 3: Implement Sidebar**

```tsx
// dashboard/src/components/Sidebar.tsx
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const NAV = [
  { href: '/',          label: 'Dashboard',  icon: '◈' },
  { href: '/revenue',   label: 'Revenue',    icon: '◇' },
  { href: '/viewers',   label: 'Viewers',    icon: '◉' },
  { href: '/streams',   label: 'Streams',    icon: '▶' },
  { href: '/controls',  label: 'Controls',   icon: '⊕' },
]

export function Sidebar() {
  const pathname = usePathname()
  return (
    <aside className="fixed left-0 top-0 h-screen w-16 flex flex-col items-center py-6 gap-1 z-50"
      style={{ background: 'var(--bg-surface)', borderRight: '1px solid var(--bg-border)' }}>
      {/* Wordmark */}
      <div className="font-mono text-xs mb-6 rotate-[-90deg] tracking-widest"
        style={{ color: 'var(--teal)', whiteSpace: 'nowrap', transformOrigin: 'center' }}>
        AIKO
      </div>
      {NAV.map(({ href, label, icon }) => {
        const active = pathname === href
        return (
          <Link key={href} href={href} title={label}
            className="w-10 h-10 flex items-center justify-center rounded transition-all duration-200"
            style={{
              background: active ? 'var(--teal-dim)' : 'transparent',
              color: active ? 'var(--teal)' : 'var(--text-secondary)',
              fontSize: '1.1rem',
              boxShadow: active ? 'var(--teal-glow)' : 'none',
            }}>
            {icon}
          </Link>
        )
      })}
    </aside>
  )
}
```

**Step 4: Implement StatusBar**

```tsx
// dashboard/src/components/StatusBar.tsx
'use client'
import { useStreamStore } from '@/stores/stream'

export function StatusBar() {
  const { isLive, viewerCount, uptime } = useStreamStore()
  return (
    <div className="fixed bottom-0 left-16 right-0 h-8 flex items-center px-4 gap-6 font-mono text-xs z-40"
      style={{ background: 'var(--bg-surface)', borderTop: '1px solid var(--bg-border)', color: 'var(--text-secondary)' }}>
      <span style={{ color: isLive ? 'var(--teal)' : 'var(--pink)' }}>
        {isLive ? '● LIVE' : '○ OFFLINE'}
      </span>
      <span>{viewerCount.toLocaleString()} viewers</span>
      <span>uptime {uptime}</span>
      <span className="ml-auto" style={{ color: 'var(--text-secondary)' }}>
        autonomous-vtuber v0.1
      </span>
    </div>
  )
}
```

**Step 5: Update layout**

```tsx
// dashboard/src/app/layout.tsx
import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/Sidebar'
import { StatusBar } from '@/components/StatusBar'

export const metadata: Metadata = { title: 'Aiko — Stream Ops' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Sidebar />
        <main className="ml-16 mb-8 min-h-screen p-6">{children}</main>
        <StatusBar />
      </body>
    </html>
  )
}
```

Run: `npm test -- --testPathPattern=Sidebar`
Expected: PASS

**Step 6: Commit**

```bash
git add dashboard/src/
git commit -m "feat: shell layout - sidebar nav, status bar"
```

---

## Phase F2 — State & Data Layer

### Task F2.1: Zustand stores

**Files:**
- Create: `dashboard/src/stores/stream.ts`
- Create: `dashboard/src/stores/metrics.ts`
- Create: `dashboard/src/stores/donations.ts`

```typescript
// dashboard/src/stores/stream.ts
import { create } from 'zustand'

interface StreamState {
  isLive: boolean
  viewerCount: number
  uptime: string
  currentActivity: string
  chatVelocity: number
  engagementScore: number
  set: (patch: Partial<StreamState>) => void
}

export const useStreamStore = create<StreamState>((set) => ({
  isLive: false,
  viewerCount: 0,
  uptime: '0:00:00',
  currentActivity: 'idle',
  chatVelocity: 0,
  engagementScore: 0,
  set: (patch) => set(patch),
}))
```

```typescript
// dashboard/src/stores/metrics.ts
import { create } from 'zustand'

export interface RevenuePoint { timestamp: string; amount: number; cumulative: number }
export interface MetricsState {
  revenueToday: number
  revenueTimeline: RevenuePoint[]
  subsCount: number
  bitsToday: number
  donationsPerHour: number
  set: (patch: Partial<MetricsState>) => void
  addRevenuePoint: (point: RevenuePoint) => void
}

export const useMetricsStore = create<MetricsState>((set) => ({
  revenueToday: 0,
  revenueTimeline: [],
  subsCount: 0,
  bitsToday: 0,
  donationsPerHour: 0,
  set: (patch) => set(patch),
  addRevenuePoint: (point) =>
    set((s) => ({ revenueTimeline: [...s.revenueTimeline.slice(-200), point] })),
}))
```

```typescript
// dashboard/src/stores/donations.ts
import { create } from 'zustand'

export interface Donation {
  id: string
  username: string
  amount: number
  message: string
  timestamp: string
  type: 'donation' | 'sub' | 'bits'
}

interface DonationState {
  recent: Donation[]
  topDonors: { username: string; total: number }[]
  add: (d: Donation) => void
  setTopDonors: (donors: DonationState['topDonors']) => void
}

export const useDonationStore = create<DonationState>((set) => ({
  recent: [],
  topDonors: [],
  add: (d) => set((s) => ({ recent: [d, ...s.recent.slice(0, 49)] })),
  setTopDonors: (donors) => set({ topDonors: donors }),
}))
```

**Commit:**

```bash
git add dashboard/src/stores/
git commit -m "feat: zustand stores for stream state, metrics, donations"
```

---

### Task F2.2: WebSocket hook for real-time updates

**Files:**
- Create: `dashboard/src/hooks/useRealtimeMetrics.ts`

```typescript
// dashboard/src/hooks/useRealtimeMetrics.ts
'use client'
import { useEffect, useRef } from 'react'
import { useStreamStore } from '@/stores/stream'
import { useMetricsStore } from '@/stores/metrics'
import { useDonationStore } from '@/stores/donations'

export function useRealtimeMetrics() {
  const wsRef = useRef<WebSocket | null>(null)
  const setStream = useStreamStore((s) => s.set)
  const setMetrics = useMetricsStore((s) => s.set)
  const addRevenue = useMetricsStore((s) => s.addRevenuePoint)
  const addDonation = useDonationStore((s) => s.add)

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000/ws/metrics'
    const connect = () => {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data) as { type: string; data: Record<string, unknown> }
        switch (msg.type) {
          case 'stream_state':
            setStream(msg.data as Parameters<typeof setStream>[0])
            break
          case 'metrics_update':
            setMetrics(msg.data as Parameters<typeof setMetrics>[0])
            break
          case 'revenue_point':
            addRevenue(msg.data as Parameters<typeof addRevenue>[0])
            break
          case 'donation':
            addDonation(msg.data as Parameters<typeof addDonation>[0])
            break
        }
      }

      ws.onclose = () => {
        // Reconnect after 3s
        setTimeout(connect, 3000)
      }
    }

    connect()
    return () => wsRef.current?.close()
  }, [setStream, setMetrics, addRevenue, addDonation])
}
```

**Commit:**

```bash
git add dashboard/src/hooks/
git commit -m "feat: WebSocket hook with auto-reconnect for real-time metrics"
```

---

## Phase F3 — Dashboard Page (Main View)

### Task F3.1: MetricCard component

**Files:**
- Create: `dashboard/src/components/MetricCard.tsx`
- Create: `dashboard/src/components/__tests__/MetricCard.test.tsx`

**Step 1: Failing test**

```typescript
// dashboard/src/components/__tests__/MetricCard.test.tsx
import { render, screen } from '@testing-library/react'
import { MetricCard } from '../MetricCard'

test('renders label and value', () => {
  render(<MetricCard label="Viewers" value="1,234" unit="live" />)
  expect(screen.getByText('Viewers')).toBeInTheDocument()
  expect(screen.getByText('1,234')).toBeInTheDocument()
  expect(screen.getByText('live')).toBeInTheDocument()
})

test('renders teal variant with glow class', () => {
  const { container } = render(<MetricCard label="Revenue" value="$42" variant="teal" />)
  expect(container.firstChild).toHaveClass('glow-teal')
})
```

Run: `npm test -- --testPathPattern=MetricCard`
Expected: FAIL

**Step 2: Implement MetricCard**

```tsx
// dashboard/src/components/MetricCard.tsx
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
    <div
      className={`slash-card ${glowClass} ${className}`}
      style={{
        background: 'var(--bg-elevated)',
        border: `1px solid ${variant !== 'default' ? accentColor + '40' : 'var(--bg-border)'}`,
        padding: '1.25rem 1.5rem',
        position: 'relative',
      }}
    >
      {/* Corner slash decoration */}
      <div style={{
        position: 'absolute', top: 0, right: 0,
        width: 16, height: 16,
        background: variant !== 'default' ? accentColor : 'var(--bg-border)',
        clipPath: 'polygon(100% 0, 0 0, 100% 100%)',
        opacity: 0.6,
      }} />

      <p className="font-mono text-xs tracking-widest mb-2 uppercase"
        style={{ color: 'var(--text-secondary)' }}>
        {label}
      </p>

      <div className="flex items-baseline gap-2">
        <span className="font-mono text-3xl font-semibold" style={{ color: accentColor }}>
          {value}
        </span>
        {unit && (
          <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>
            {unit}
          </span>
        )}
      </div>

      {delta && (
        <p className="font-mono text-xs mt-1"
          style={{ color: deltaPositive ? 'var(--teal)' : 'var(--pink)' }}>
          {deltaPositive ? '↑' : '↓'} {delta}
        </p>
      )}
    </div>
  )
}
```

Run: `npm test -- --testPathPattern=MetricCard`
Expected: PASS

**Commit:**

```bash
git add dashboard/src/components/MetricCard.tsx dashboard/src/components/__tests__/
git commit -m "feat: MetricCard component with slash-corner aesthetic and glow variants"
```

---

### Task F3.2: Revenue chart component

**Files:**
- Create: `dashboard/src/components/RevenueChart.tsx`

```tsx
// dashboard/src/components/RevenueChart.tsx
'use client'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useMetricsStore } from '@/stores/metrics'

export function RevenueChart() {
  const timeline = useMetricsStore((s) => s.revenueTimeline)

  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)', padding: '1.25rem' }}>
      <p className="font-mono text-xs tracking-widest mb-4 uppercase" style={{ color: 'var(--text-secondary)' }}>
        Revenue Timeline
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={timeline}>
          <defs>
            <linearGradient id="tealGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="var(--teal)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="var(--teal)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="timestamp"
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 10, fill: 'var(--text-secondary)' }}
            axisLine={false} tickLine={false}
          />
          <YAxis
            tick={{ fontFamily: 'IBM Plex Mono', fontSize: 10, fill: 'var(--text-secondary)' }}
            axisLine={false} tickLine={false}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--teal)',
              fontFamily: 'IBM Plex Mono',
              fontSize: 11,
              color: 'var(--text-primary)',
            }}
            formatter={(v: number) => [`$${v.toFixed(2)}`, 'Revenue']}
          />
          <Area
            type="monotone"
            dataKey="cumulative"
            stroke="var(--teal)"
            strokeWidth={2}
            fill="url(#tealGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
```

**Commit:**

```bash
git add dashboard/src/components/RevenueChart.tsx
git commit -m "feat: RevenueChart with teal gradient area chart"
```

---

### Task F3.3: Donation feed + alert

**Files:**
- Create: `dashboard/src/components/DonationFeed.tsx`
- Create: `dashboard/src/components/DonationAlert.tsx`

```tsx
// dashboard/src/components/DonationFeed.tsx
'use client'
import { useDonationStore } from '@/stores/donations'

export function DonationFeed() {
  const recent = useDonationStore((s) => s.recent)

  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)', padding: '1.25rem', height: '320px', overflowY: 'auto' }}>
      <p className="font-mono text-xs tracking-widest mb-3 uppercase" style={{ color: 'var(--text-secondary)' }}>
        Donation Feed
      </p>
      <div className="flex flex-col gap-2">
        {recent.map((d) => (
          <div key={d.id} className="flex items-start gap-3 font-mono text-xs"
            style={{ borderLeft: `2px solid ${d.type === 'donation' ? 'var(--pink)' : 'var(--teal)'}`, paddingLeft: '0.5rem' }}>
            <span style={{ color: d.type === 'donation' ? 'var(--pink)' : 'var(--teal)', minWidth: '3.5rem' }}>
              {d.type === 'donation' ? `$${d.amount.toFixed(2)}` : d.type === 'sub' ? 'SUB' : `${d.amount}b`}
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
        {recent.length === 0 && (
          <p style={{ color: 'var(--text-secondary)' }}>No events yet</p>
        )}
      </div>
    </div>
  )
}
```

```tsx
// dashboard/src/components/DonationAlert.tsx
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
      style={{
        background: 'var(--bg-elevated)',
        border: '1px solid var(--pink)',
        padding: '1rem 1.5rem',
        minWidth: '260px',
      }}>
      <p className="font-mono text-xs tracking-widest mb-1" style={{ color: 'var(--pink)' }}>
        DONATION
      </p>
      <p className="font-mono text-2xl font-semibold" style={{ color: 'var(--pink)' }}>
        ${visible.amount.toFixed(2)}
      </p>
      <p className="font-mono text-sm mt-1" style={{ color: 'var(--text-primary)' }}>
        from <strong>{visible.username}</strong>
      </p>
      {visible.message && (
        <p className="font-mono text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
          "{visible.message}"
        </p>
      )}
    </div>
  )
}
```

**Commit:**

```bash
git add dashboard/src/components/DonationFeed.tsx dashboard/src/components/DonationAlert.tsx
git commit -m "feat: donation feed with real-time entries, slide-in alert overlay"
```

---

### Task F3.4: Main dashboard page

**Files:**
- Modify: `dashboard/src/app/page.tsx`
- Create: `dashboard/src/app/RealtimeProvider.tsx`

```tsx
// dashboard/src/app/RealtimeProvider.tsx
'use client'
import { useRealtimeMetrics } from '@/hooks/useRealtimeMetrics'

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  useRealtimeMetrics()
  return <>{children}</>
}
```

```tsx
// dashboard/src/app/page.tsx
import { Suspense } from 'react'
import { MetricCard } from '@/components/MetricCard'
import { RevenueChart } from '@/components/RevenueChart'
import { DonationFeed } from '@/components/DonationFeed'
import { DonationAlert } from '@/components/DonationAlert'
import { RealtimeProvider } from './RealtimeProvider'

export default function DashboardPage() {
  return (
    <RealtimeProvider>
      <DonationAlert />

      {/* Header */}
      <div className="flex items-center justify-between mb-8 reveal reveal-1">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Syne' }}>
            Stream Ops
          </h1>
          <p className="font-mono text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
            AIKO_NATSUKI · AUTONOMOUS
          </p>
        </div>
        <LiveIndicator />
      </div>

      {/* Top metric row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <MetricCard label="Viewers"         value="—" unit="live"  variant="teal"    className="reveal reveal-2" />
        <MetricCard label="Chat / min"       value="—" unit="msg"   variant="default" className="reveal reveal-3" />
        <MetricCard label="Revenue Today"    value="—" unit="USD"   variant="teal"    className="reveal reveal-4" />
        <MetricCard label="Engagement Score" value="—" unit="/ 100" variant="default" className="reveal reveal-5" />
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 flex flex-col gap-4">
          <Suspense><RevenueChart /></Suspense>
          <ActivityStatus />
        </div>
        <div>
          <Suspense><DonationFeed /></Suspense>
        </div>
      </div>
    </RealtimeProvider>
  )
}

function LiveIndicator() {
  return (
    <div className="flex items-center gap-2 font-mono text-xs px-3 py-1.5"
      style={{ border: '1px solid var(--teal)', color: 'var(--teal)' }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--teal)', display: 'inline-block',
        boxShadow: '0 0 8px var(--teal)', animation: 'value-flash 2s infinite' }} />
      LIVE
    </div>
  )
}

function ActivityStatus() {
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)', padding: '1.25rem' }}>
      <p className="font-mono text-xs tracking-widest mb-2 uppercase" style={{ color: 'var(--text-secondary)' }}>
        Current Activity
      </p>
      <p className="font-mono text-lg" style={{ color: 'var(--text-primary)' }}>idle</p>
    </div>
  )
}
```

**Step 2: Start dev server and verify visual**

```bash
cd dashboard && npm run dev
```
Open `http://localhost:3000`. Expected: dark terminal dashboard with grid, sidebar, metric cards with slash corners, teal accents.

**Step 3: Commit**

```bash
git add dashboard/src/app/
git commit -m "feat: main dashboard page - metric grid, revenue chart, donation feed"
```

Message Run-in: "EPSILON READY"

---

## Phase F4 — Additional Pages

### Task F4.1: `/revenue` — Revenue breakdown

- Revenue by source (subs, bits, direct donations) as stacked bar chart
- 7-day and 30-day toggles
- Top donors table with total amounts

### Task F4.2: `/viewers` — Viewer analytics

- Top chatters and donors from Neo4j (`GET /api/viewers/top`)
- Viewer retention graph
- Sub tier breakdown

### Task F4.3: `/streams` — Stream history

- Past streams table: date, duration, peak viewers, revenue
- Click-through to per-stream analytics

### Task F4.4: `/controls` — Stream controls

- Manual override: set activity (talk, react, game, q_and_a)
- Trigger donation goal announcement
- Set expression manually (test performer agent)
- Emergency stop stream button (with confirmation modal)

```tsx
// Confirmation modal for emergency stop
function StopStreamButton() {
  const [confirming, setConfirming] = useState(false)
  // Two-click confirm before calling POST /api/stream/stop
}
```

---

## Render Deployment for Dashboard

**Step 1: Add to render.yaml (Worker Alpha's file — coordinate via Run-in)**

```yaml
# Add to render.yaml services array:
  - type: web
    name: dashboard
    runtime: node
    buildCommand: cd dashboard && npm ci && npm run build
    startCommand: cd dashboard && npm start
    envVars:
      - key: NEXT_PUBLIC_API_URL
        fromService:
          name: api
          type: web
          property: host
      - key: NEXT_PUBLIC_WS_URL
        value: wss://api.your-render-app.onrender.com/ws/metrics
```

---

## Full Agent Roster (Updated)

| Agent | Role | Branch | Depends On |
|---|---|---|---|
| **Run-in** | Coordinator | `main` | — |
| **Worker Alpha** | Infra | `feat/infra` | — |
| **Worker Beta** | Platform | `feat/platform` | — |
| **Worker Gamma** | Twitch/Chat | `feat/twitch` | Alpha (event bus) |
| **Worker Delta** | Streaming/Clips | `feat/streaming` | Alpha (event bus) |
| **Worker Epsilon** | Frontend | `feat/dashboard` | Phase 3 API (mock first) |

Worker Epsilon can run in parallel with Phase 1–2 backend work using mock WebSocket data, then wire to live API at Phase 3 merge.
