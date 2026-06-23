import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Download } from 'lucide-react'
import { useTransactionStore } from '@/store/transactionStore'
import ReportPreview from '@/components/ReportPreview'

export default function ReportPage() {
  const navigate = useNavigate()
  const { statementId, metrics, categories, recurring, insights, status } = useTransactionStore()

  useEffect(() => {
    if (!statementId) { navigate('/'); return }
    if (status === 'idle') {
      useTransactionStore.getState().fetchAllData(statementId)
    }
  }, [statementId, status, navigate])

  if (status === 'processing' || status === 'uploading') {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="animate-pulse text-gray-500">Loading report data...</div>
      </div>
    )
  }

  if (!metrics) return null

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Financial Report</h1>
          <p className="text-gray-500 mt-1">Complete analysis of your bank statement</p>
        </div>
        <button
          onClick={() => window.location.href = `/api/report/pdf?statement_id=${statementId}`}
          className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Download PDF
        </button>
      </div>

      <ReportPreview
        metrics={metrics}
        categories={categories}
        recurring={recurring}
        insights={insights}
      />
    </div>
  )
}
