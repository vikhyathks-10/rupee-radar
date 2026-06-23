export type MetricCard = { label: string; value: string; color: string }

export default function MetricsSummary({ metrics }: { metrics: { total_income: number; total_spend: number; savings: number; savings_rate: number } }) {
  const formatRs = (n: number) => `Rs.${Math.abs(n).toLocaleString('en-IN')}`

  const cards = [
    { label: 'Total Income', value: formatRs(metrics.total_income), color: 'green' },
    { label: 'Total Spend', value: formatRs(metrics.total_spend), color: 'red' },
    { label: 'Savings', value: formatRs(metrics.savings), color: 'blue' },
    { label: 'Savings Rate', value: `${metrics.savings_rate}%`, color: 'purple' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((card, i) => (
        <div key={i} className={`bg-${card.color}-50 rounded-xl p-5 border`}>
          <p className="text-sm text-gray-500">{card.label}</p>
          <p className="text-xl font-bold">{card.value}</p>
        </div>
      ))}
    </div>
  )
}
