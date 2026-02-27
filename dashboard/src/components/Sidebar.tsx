'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const NAV = [
  { href: '/',         label: 'Dashboard', icon: '\u25C8' },
  { href: '/revenue',  label: 'Revenue',   icon: '\u25C7' },
  { href: '/viewers',  label: 'Viewers',   icon: '\u25C9' },
  { href: '/streams',  label: 'Streams',   icon: '\u25B6' },
  { href: '/controls', label: 'Controls',  icon: '\u2295' },
]

export function Sidebar() {
  const pathname = usePathname()
  return (
    <aside className="fixed left-0 top-0 h-screen w-16 flex flex-col items-center py-6 gap-1 z-50"
      style={{ background: 'var(--bg-surface)', borderRight: '1px solid var(--bg-border)' }}>
      <div className="font-mono text-xs mb-6 tracking-widest"
        style={{ color: 'var(--teal)', writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}>
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
