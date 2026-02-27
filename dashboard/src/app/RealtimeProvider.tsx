'use client'
import { useRealtimeMetrics } from '@/hooks/useRealtimeMetrics'

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  useRealtimeMetrics()
  return <>{children}</>
}
