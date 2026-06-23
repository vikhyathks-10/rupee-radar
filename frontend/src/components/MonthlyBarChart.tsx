import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export type MonthlyBreakdown = { month: string; income: number; spend: number }

export default function MonthlyBarChart({ data }: { data: MonthlyBreakdown[] }) {
  const chartData = data.map((m) => ({
    name: m.month,
    Income: m.income,
    Spend: m.spend,
    Savings: m.income - m.spend,
  }))

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold">Monthly Breakdown</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Income" fill="#10B981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Spend" fill="#EF4444" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Savings" fill="#3B82F6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
