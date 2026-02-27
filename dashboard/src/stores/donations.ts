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
  setTopDonors: (donors: { username: string; total: number }[]) => void
}

export const useDonationStore = create<DonationState>((set) => ({
  recent: [],
  topDonors: [],
  add: (d) => set((s) => ({ recent: [d, ...s.recent.slice(0, 49)] })),
  setTopDonors: (donors) => set({ topDonors: donors }),
}))
