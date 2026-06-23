import { useTransactionStore } from '@/store/transactionStore'
import type { Transaction } from '@/api/types'

interface UseTransactionsReturn {
  transactions: Transaction[]
  total: number
  fetchTransactions: (page?: number, limit?: number, category?: string) => Promise<void>
}

export function useTransactions(): UseTransactionsReturn {
  const { transactions, transactionCount, fetchTransactions } = useTransactionStore()

  return {
    transactions,
    total: transactionCount,
    fetchTransactions,
  }
}
