import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { formatCurrency } from '@/lib/formatCurrency'
import type { CategoryBreakdown } from '@/api/types'

const COLORS = ['#4F46E5', '#7C3AED', '#EC4899', '#F59E0B', '#10B981', '#06B6D4', '#EF4444', '#8B5CF6', '#F97316', '#14B8A6']

interface CategoryPieChartProps {
  categories: CategoryBreakdown[]
}

export function CategoryPieChart({ categories }: CategoryPieChartProps) {
  const pieData = categories.map((c, i) => ({
    name: c.name,
    value: Math.abs(c.total),
    color: COLORS[i % COLORS.length]
  }))

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="font-semibold text-lg mb-4">Spending Breakdown</h2>
      {pieData.length > 0 ? (
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((d, i) => (
                  <Cell key={i} fill={d.color} />
                ))}
              </Pie>
              <Tooltip formatter={(v: number) => formatCurrency(v)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="text-gray-400 text-center py-20">No category data</p>
      )}
    </div>
  )
}
