import { Info, AlertTriangle, AlertCircle } from 'lucide-react'
import { formatCurrency } from '@/lib/formatCurrency'
import type { Insight } from '@/api/types'

const SEVERITY_CONFIG = {
  info: {
    icon: Info,
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-700',
    badge: 'bg-blue-100 text-blue-700',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
    badge: 'bg-amber-100 text-amber-700',
  },
  critical: {
    icon: AlertCircle,
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-700',
    badge: 'bg-red-100 text-red-700',
  },
}

interface InsightCardsProps {
  insights: Insight[]
}

export function InsightCards({ insights }: InsightCardsProps) {
  return (
    <div className="space-y-4">
      {insights.length === 0 ? (
        <p className="text-gray-400 text-center py-20 bg-white rounded-xl border">No insights generated</p>
      ) : (
        insights.map((ins) => {
          const cfg = SEVERITY_CONFIG[ins.severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.info
          const Icon = cfg.icon
          return (
            <div key={ins.id || ins.title} className={`${cfg.bg} ${cfg.border} border rounded-xl p-5 transition-all hover:shadow-sm`}>
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg ${cfg.badge} flex items-center justify-center shrink-0`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900 leading-snug">{ins.title}</h3>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${cfg.badge}`}>
                      {ins.severity}
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm leading-relaxed mt-1">{ins.description}</p>
                  {ins.amount_referenced !== null && ins.amount_referenced !== undefined && (
                    <p className="text-sm font-medium text-gray-600 mt-2">
                      Amount referenced: <span className="text-gray-900">{formatCurrency(ins.amount_referenced)}</span>
                    </p>
                  )}
                  {ins.category && (
                    <p className="text-xs text-gray-400 mt-1">
                      Category: <span className="font-medium text-gray-500">{ins.category}</span>
                    </p>
                  )}
                </div>
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}
