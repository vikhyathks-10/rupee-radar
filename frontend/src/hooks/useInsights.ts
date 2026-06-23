import { useTransactionStore } from '@/store/transactionStore'
import type { Insight } from '@/api/types'

interface UseInsightsReturn {
  insights: Insight[]
  fetchInsights: () => Promise<void>
}

export function useInsights(): UseInsightsReturn {
  const { insights, fetchInsights } = useTransactionStore()

  return {
    insights,
    fetchInsights,
  }
}
