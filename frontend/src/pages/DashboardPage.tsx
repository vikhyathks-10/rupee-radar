import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowUpRight, ArrowDownRight, PiggyBank, TrendingUp } from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useTransactionStore } from '@/store/transactionStore'
import MonthlyBarChart from '@/components/MonthlyBarChart'
import TopTransactions from '@/components/TopTransactions'

const COLORS = ['#4F46E5', '#7C3AED', '#EC4899', '#F59E0B', '#10B981', '#06B6D4', '#EF4444', '#8B5CF6', '#F97316', '#14B8A6']

function formatRs(n: number) {
  const abs = Math.abs(n)
  const sign = n < 0 ? '-' : ''
  if (abs >= 10000000) return `${sign}Rs.${(abs / 10000000).toFixed(2)} Cr`
  if (abs >= 100000) return `${sign}Rs.${(abs / 100000).toFixed(2)} L`
  return `${sign}Rs.${abs.toLocaleString('en-IN')}`
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { statementId, metrics, categories, transactions, recurring, status } = useTransactionStore()

  useEffect(() => {
    if (!statementId) { navigate('/'); return }
    if (status === 'idle') {
      useTransactionStore.getState().fetchAllData(statementId)
    }
  }, [statementId, status, navigate])

  if (status === 'processing' || status === 'uploading') {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="animate-pulse text-gray-500">Loading your financial data...</div>
      </div>
    )
  }

  if (!metrics) return null

  const pieData = categories.map((c, i) => ({ name: c.name, value: Math.abs(c.total), color: COLORS[i % COLORS.length] }))

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard icon={<ArrowUpRight className="w-5 h-5" />} label="Total Income" value={formatRs(metrics.total_income)} color="green" />
        <MetricCard icon={<ArrowDownRight className="w-5 h-5" />} label="Total Spend" value={formatRs(metrics.total_spend)} color="red" />
        <MetricCard icon={<PiggyBank className="w-5 h-5" />} label="Savings" value={formatRs(metrics.savings)} color="blue" />
        <MetricCard icon={<TrendingUp className="w-5 h-5" />} label="Savings Rate" value={`${metrics.savings_rate ?? 0}%`} color="purple" />
      </div>

      {/* Category Chart + Recurring */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie chart */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="font-semibold text-lg mb-4">Spending Breakdown</h2>
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

        {/* Recurring */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="font-semibold text-lg mb-4">Recurring Payments ({recurring.length})</h2>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
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
      </div>

      {/* Monthly Bar Chart */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="font-semibold text-lg mb-4">Monthly Income vs Spend</h2>
        <MonthlyBarChart data={metrics.monthly_breakdown} />
      </div>

      {/* Top Transactions */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="font-semibold text-lg mb-4">Top 5 Largest Expenses</h2>
        <TopTransactions transactions={transactions} />
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="font-semibold text-lg mb-4">All Transactions ({transactions.length})</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-gray-500">
                <th className="py-2 px-3 text-left">Date</th>
                <th className="py-2 px-3 text-left">Description</th>
                <th className="py-2 px-3 text-right">Amount</th>
                <th className="py-2 px-3 text-left">Category</th>
                <th className="py-2 px-3 text-center">Recurring</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-2 px-3 text-gray-600">{t.date}</td>
                  <td className="py-2 px-3">{t.description}</td>
                  <td className={`py-2 px-3 text-right font-medium ${t.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatRs(t.amount)}
                  </td>
                  <td className="py-2 px-3">
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">{t.category}</span>
                  </td>
                  <td className="py-2 px-3 text-center">
                    {t.is_recurring && <span className="px-2 py-1 rounded-full text-xs bg-amber-50 text-amber-700">Yes</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  const bg = { green: 'bg-green-50', red: 'bg-red-50', blue: 'bg-blue-50', purple: 'bg-purple-50' }[color]
  const iconBg = { green: 'bg-green-100 text-green-600', red: 'bg-red-100 text-red-600', blue: 'bg-blue-100 text-blue-600', purple: 'bg-purple-100 text-purple-600' }[color]
  return (
    <div className={`${bg} rounded-xl p-5 border`}>
      <div className={`w-10 h-10 rounded-lg ${iconBg} flex items-center justify-center mb-3`}>{icon}</div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-xl font-bold">{value}</p>
    </div>
  )
}
