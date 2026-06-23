import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import UploadPage from '@/pages/UploadPage'
import DashboardPage from '@/pages/DashboardPage'
import InsightsPage from '@/pages/InsightsPage'
import ReportPage from '@/pages/ReportPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/dashboard" element={<Layout><DashboardPage /></Layout>} />
      <Route path="/insights" element={<Layout><InsightsPage /></Layout>} />
      <Route path="/report" element={<Layout><ReportPage /></Layout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
