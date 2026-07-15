import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Lightbulb,
  FileBarChart,
  Upload,
  Download,
} from 'lucide-react'
import { useTransactionStore } from '@/store/transactionStore'

export default function Layout({
  children,
}: {
  children: ReactNode
}) {
  const location = useLocation()

  // Removed unused "metrics"
  const { statementId, status } = useTransactionStore()

  const navItems = [
    {
      path: '/dashboard',
      icon: <LayoutDashboard className="w-5 h-5" />,
      label: 'Dashboard',
    },
    {
      path: '/insights',
      icon: <Lightbulb className="w-5 h-5" />,
      label: 'Insights',
    },
    {
      path: '/report',
      icon: <FileBarChart className="w-5 h-5" />,
      label: 'Report',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r p-6 flex flex-col">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-indigo-600">
            RupeeRadar
          </h1>

          {statementId && (
            <div className="mt-2 text-xs text-gray-500">
              <p>Statement ID: {statementId.slice(0, 8)}...</p>

              <p
                className={`mt-1 ${
                  status === 'completed'
                    ? 'text-green-600'
                    : 'text-amber-600'
                }`}
              >
                ●{' '}
                {status === 'completed'
                  ? 'Analysis Complete'
                  : 'Processing'}
              </p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="space-y-2 flex-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                location.pathname === item.path
                  ? 'bg-indigo-50 text-indigo-600 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Bottom Actions */}
        <div className="space-y-2 pt-4 border-t">
          <button
            onClick={() => {
              if (statementId) {
                window.location.href = `/api/report/pdf?statement_id=${statementId}`
              }
            }}
            disabled={!statementId}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-100 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-5 h-5" />
            Download PDF
          </button>

          <Link
            to="/"
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition"
          >
            <Upload className="w-5 h-5" />
            New Upload
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}