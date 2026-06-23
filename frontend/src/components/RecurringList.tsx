import { formatCurrency } from '@/lib/formatCurrency'
import type { RecurringItem } from '@/api/types'

interface RecurringListProps {
  recurring: RecurringItem[]
}

export function RecurringList({ recurring }: RecurringListProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="font-semibold text-lg mb-4">Recurring Payments ({recurring.length})</h2>
      <div className="space-y-2 max-h-[300px] overflow-y-auto">
        {recurring.length === 0 ? (
          <p className="text-gray-400 text-center py-20">No recurring payments detected</p>
        ) : (
          recurring.map((r, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
              <div>
                <p className="font-medium text-sm">{r.merchant}</p>
                <p className="text-xs text-gray-400">
                  {r.frequency} · x{r.occurrences} · next {r.next_expected_date}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-sm">{formatCurrency(Math.abs(r.amount))}</p>
                <p className="text-xs text-gray-400">annual {formatCurrency(r.annual_cost)}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
