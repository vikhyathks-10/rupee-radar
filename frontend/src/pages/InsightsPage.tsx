import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lightbulb } from 'lucide-react'
import { useTransactionStore } from '@/store/transactionStore'
import { InsightCards } from '@/components/InsightCards'
import { InsightsSkeleton } from '@/components/LoadingSkeleton'
import { EmptyState } from '@/components/EmptyState'

export default function InsightsPage() {
  const navigate = useNavigate()
  const { statementId, insights, status, error } = useTransactionStore()

  useEffect(() => {
    if (!statementId) {
      return
    }
    if (insights.length === 0 && status === 'completed') {
      useTransactionStore.getState().fetchInsights()
    }
  }, [statementId, insights.length, status])

  if (status === 'processing' || status === 'uploading') {
    return <InsightsSkeleton />
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto mt-20 p-6 bg-red-50 border border-red-200 rounded-xl text-center space-y-4">
        <h3 className="font-bold text-red-800 text-lg">Error Loading Insights</h3>
        <p className="text-sm text-red-600">{error}</p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!statementId) {
    return <EmptyState />
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-6 animate-fadeIn">
      <div>
        <div className="flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-indigo-600" />
          <h1 className="text-2xl font-bold">Financial Insights</h1>
        </div>
        <p className="text-gray-500 mt-1">AI-generated analysis of your spending patterns and financial health</p>
      </div>

      <InsightCards insights={insights} />
    </div>
  )
}
