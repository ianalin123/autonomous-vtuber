import { create } from 'zustand'

interface StreamState {
  isLive: boolean
  viewerCount: number
  uptime: string
  currentActivity: string
  chatVelocity: number
  engagementScore: number
  set: (patch: Partial<Omit<StreamState, 'set'>>) => void
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
