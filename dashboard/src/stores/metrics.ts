import { create } from 'zustand'

export interface RevenuePoint { timestamp: string; amount: number; cumulative: number }

interface MetricsState {
  revenueToday: number
  revenueTimeline: RevenuePoint[]
  subsCount: number
  bitsToday: number
  donationsPerHour: number
  set: (patch: Partial<Omit<MetricsState, 'set' | 'addRevenuePoint'>>) => void
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
