import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react'

const COLORS = ['#4F46E5', '#7C3AED', '#EC4899', '#F59E0B', '#10B981', '#06B6D4', '#EF4444', '#8B5CF6', '#F97316', '#14B8A6']

export default function ReportPreview({
  metrics,
  categories,
  recurring,
  insights,
}: {
  metrics: { total_income: number; total_spend: number; savings: number; savings_rate: number }
  categories: { name: string; total: number; count: number }[]
  recurring: { merchant: string; frequency: string; occurrences: number; amount: number; annual_cost: number; next_expected_date: string }[]
  insights: { type: string; severity: string; message: string }[]
}) {
  const formatRs = (n: number) => `Rs.${Math.abs(n).toLocaleString('en-IN')}`

  const pieData = categories.map((c, i) => ({ name: c.name, value: Math.abs(c.total), color: COLORS[i % COLORS.length] }))

  return (
    <div className="space-y-8">
      {/* Financial Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-green-50 rounded-xl p-5 border">
          <p className="text-sm text-gray-500">Total Income</p>
          <p className="text-xl font-bold">{formatRs(metrics.total_income)}</p>
        </div>
        <div className="bg-red-50 rounded-xl p-5 border">
          <p className="text-sm text-gray-500">Total Spend</p>
          <p className="text-xl font-bold">{formatRs(metrics.total_spend)}</p>
        </div>
        <div className="bg-blue-50 rounded-xl p-5 border">
          <p className="text-sm text-gray-500">Savings</p>
          <p className="text-xl font-bold">{formatRs(metrics.savings)}</p>
        </div>
        <div className="bg-purple-50 rounded-xl p-5 border">
          <p className="text-sm text-gray-500">Savings Rate</p>
          <p className="text-xl font-bold">{metrics.savings_rate}%</p>
        </div>
      </div>

      {/* Spending by Category */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="font-semibold text-lg mb-4">Spending by Category</h2>
        {pieData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
              </Pie>
              <Tooltip formatter={(v: number) => formatRs(v)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        ) : <p className="text-gray-400">No category data</p>}
      </div>

      {/* Recurring Payments */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="font-semibold text-lg mb-4">Recurring Payments ({recurring.length})</h2>
        <div className="space-y-2">
          {recurring.map((r, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
              <div>
                <p className="font-medium text-sm">{r.merchant}</p>
                <p className="text-xs text-gray-400">{r.frequency} · x{r.occurrences} · next {r.next_expected_date}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-sm">{formatRs(Math.abs(r.amount))}</p>
                <p className="text-xs text-gray-400">annual {formatRs(r.annual_cost)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Insights */}
      {insights.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="font-semibold text-lg mb-4">AI Insights</h2>
          <div className="space-y-3">
            {insights.map((insight, i) => {
              const icon = insight.severity === 'high' ? <AlertCircle className="w-5 h-5 text-red-600" /> :
                          insight.severity === 'medium' ? <AlertTriangle className="w-5 h-5 text-amber-600" /> :
                          <CheckCircle className="w-5 h-5 text-green-600" />
              const bgColor = insight.severity === 'high' ? 'bg-red-50 border-red-200' :
                             insight.severity === 'medium' ? 'bg-amber-50 border-amber-200' :
                             'bg-green-50 border-green-200'
              return (
                <div key={i} className={`flex items-start gap-3 p-4 rounded-lg border ${bgColor}`}>
                  {icon}
                  <div>
                    <p className="font-medium text-sm">{insight.type}</p>
                    <p className="text-sm text-gray-600 mt-1">{insight.message}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
