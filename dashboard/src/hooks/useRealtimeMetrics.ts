'use client'
import { useEffect, useRef } from 'react'
import { useStreamStore } from '@/stores/stream'
import { useMetricsStore } from '@/stores/metrics'
import { useDonationStore, Donation } from '@/stores/donations'
import { RevenuePoint } from '@/stores/metrics'

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
          case 'stream_state': setStream(msg.data as unknown as Parameters<typeof setStream>[0]); break
          case 'metrics_update': setMetrics(msg.data as unknown as Parameters<typeof setMetrics>[0]); break
          case 'revenue_point': addRevenue(msg.data as unknown as RevenuePoint); break
          case 'donation': addDonation(msg.data as unknown as Donation); break
        }
      }
      ws.onclose = () => setTimeout(connect, 3000)
    }
    connect()
    return () => wsRef.current?.close()
  }, [setStream, setMetrics, addRevenue, addDonation])
}
