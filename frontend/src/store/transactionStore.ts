import { create } from 'zustand'
import client from '@/api/client'
import type {
  UploadResponse,
  MetricsResponse,
  CategoryBreakdown,
  Transaction,
  TransactionsResponse,
  RecurringItem,
  Insight,
  ProcessingStatus,
} from '@/api/types'

interface TransactionState {
  // Core identifiers
  statementId: string | null
  filename: string | null

  // Processing status
  status: ProcessingStatus
  error: string | null

  // Data
  metrics: MetricsResponse | null
  categories: CategoryBreakdown[]
  transactions: Transaction[]
  recurring: RecurringItem[]
  insights: Insight[]

  // Computed
  transactionCount: number

  // Actions
  uploadFile: (file: File) => Promise<string | null>
  fetchAllData: (statementId: string) => Promise<void>
  fetchTransactions: (page?: number, limit?: number, category?: string) => Promise<void>
  fetchInsights: () => Promise<void>
  reset: () => void
}

const initialState = {
  statementId: null,
  filename: null,
  status: 'idle' as ProcessingStatus,
  error: null,
  metrics: null,
  categories: [] as CategoryBreakdown[],
  transactions: [] as Transaction[],
  recurring: [] as RecurringItem[],
  insights: [] as Insight[],
  transactionCount: 0,
}

export const useTransactionStore = create<TransactionState>((set, get) => ({
  ...initialState,

  uploadFile: async (file: File) => {
    set({ status: 'uploading', error: null })
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await client.post<UploadResponse>('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      })
      const { statement_id, transaction_count } = res.data
      set({
        statementId: statement_id,
        filename: file.name,
        transactionCount: transaction_count,
        status: 'completed',
      })
      // Automatically fetch all data after upload
      await get().fetchAllData(statement_id)
      return statement_id
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed'
      set({ status: 'error', error: msg })
      return null
    }
  },

  fetchAllData: async (statementId: string) => {
    set({ status: 'processing' })
    try {
      const [mRes, cRes, tRes, rRes, iRes] = await Promise.all([
        client.get<MetricsResponse>(`/metrics?statement_id=${statementId}`),
        client.get(`/categories?statement_id=${statementId}`),
        client.get<TransactionsResponse>(`/transactions?statement_id=${statementId}&limit=100`),
        client.get(`/recurring?statement_id=${statementId}`),
        client.get(`/insights?statement_id=${statementId}`),
      ])

      // Metrics
      const metrics = mRes.data

      // Categories (handle both array and wrapped responses)
      const catData = cRes.data
      const categories = Array.isArray(catData) ? catData : catData.value || catData.categories || []

      // Transactions
      const transactions = tRes.data.transactions

      // Recurring
      const recData = rRes.data
      const recurring = Array.isArray(recData) ? recData : recData.value || recData.recurring || []

      // Insights
      const insData = iRes.data
      const insights = insData.insights || insData.value || (Array.isArray(insData) ? insData : [])

      set({
        metrics,
        categories,
        transactions,
        recurring,
        insights,
        status: 'completed',
        error: null,
      })
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to fetch data'
      set({ status: 'error', error: msg })
    }
  },

  fetchTransactions: async (page = 1, limit = 100, category?: string) => {
    const sid = get().statementId
    if (!sid) return
    try {
      let url = `/transactions?statement_id=${sid}&page=${page}&limit=${limit}`
      if (category) url += `&category=${category}`
      const res = await client.get<TransactionsResponse>(url)
      set({ transactions: res.data.transactions, transactionCount: res.data.total })
    } catch (err: any) {
      console.error('Failed to fetch transactions:', err)
    }
  },

  fetchInsights: async () => {
    const sid = get().statementId
    if (!sid) return
    try {
      const res = await client.get(`/insights?statement_id=${sid}`)
      const data = res.data
      const insights = data.insights || data.value || (Array.isArray(data) ? data : [])
      set({ insights })
    } catch (err: any) {
      console.error('Failed to fetch insights:', err)
    }
  },

  reset: () => set(initialState),
}))
