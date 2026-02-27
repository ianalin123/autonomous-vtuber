import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/Sidebar'
import { StatusBar } from '@/components/StatusBar'

export const metadata: Metadata = { title: 'Aiko \u2014 Stream Ops' }

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
