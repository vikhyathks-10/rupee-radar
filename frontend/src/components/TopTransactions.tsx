import { Transaction } from '@/api/types'

export default function TopTransactions({ transactions }: { transactions: Transaction[] }) {
  const formatRs = (n: number) => `Rs.${Math.abs(n).toLocaleString('en-IN')}`
  const debits = transactions.filter((t) => t.amount < 0).sort((a, b) => a.amount - b.amount).slice(0, 5)

  if (debits.length === 0) {
    return <p className="text-gray-400 text-sm">No expense transactions found</p>
  }

  return (
    <div className="space-y-3">
      {debits.map((t) => (
        <div key={t.id} className="flex items-center justify-between py-2 border-b last:border-0">
          <div className="flex-1">
            <p className="font-medium text-sm">{t.description}</p>
            <p className="text-xs text-gray-400">{t.date} · {t.category}</p>
          </div>
          <p className="font-semibold text-red-600 text-sm">-{formatRs(t.amount)}</p>
        </div>
      ))}
    </div>
  )
}
