import { useNavigate } from 'react-router-dom'
import { FileText, ArrowRight } from 'lucide-react'

interface EmptyStateProps {
  title?: string
  description?: string
}

export function EmptyState({
  title = 'No Bank Statement Selected',
  description = 'Upload your bank statement (CSV or PDF) to generate insights and view your financial summary.',
}: EmptyStateProps) {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center">
      <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
        <FileText className="w-8 h-8" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
      <p className="text-gray-500 max-w-md mb-8 leading-relaxed">
        {description}
      </p>
      <button
        onClick={() => navigate('/')}
        className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center gap-2 transition-all shadow-md shadow-indigo-100"
      >
        Upload Statement
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  )
}
