import { useState } from 'react'
import { Download, FileText, Check, Loader2 } from 'lucide-react'

interface ReportDownloadProps {
  statementId: string
}

export function ReportDownload({ statementId }: ReportDownloadProps) {
  const [downloading, setDownloading] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleDownload = async () => {
    setDownloading(true)
    try {
      // Direct browser navigation for file download
      window.location.href = `/api/report/pdf?statement_id=${statementId}`
      // Add a slight delay for better UX states
      await new Promise((resolve) => setTimeout(resolve, 1500))
    } catch (e) {
      console.error(e)
    } finally {
      setDownloading(false)
    }
  }

  const handleCopyLink = () => {
    const downloadUrl = `${window.location.origin}/api/report/pdf?statement_id=${statementId}`
    navigator.clipboard.writeText(downloadUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-white border rounded-xl shadow-sm p-6 max-w-md mx-auto space-y-6 text-center">
      <div className="mx-auto w-12 h-12 bg-indigo-50 rounded-full flex items-center justify-center text-indigo-600">
        <FileText className="w-6 h-6" />
      </div>

      <div className="space-y-1">
        <h3 className="font-bold text-gray-900 text-lg">Download PDF Report</h3>
        <p className="text-sm text-gray-500">
          Get a professional PDF summary containing all your financial overview details.
        </p>
      </div>

      <div className="space-y-2">
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="w-full py-3 rounded-xl font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-sm"
        >
          {downloading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating PDF...
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              Download Report PDF
            </>
          )}
        </button>

        <button
          onClick={handleCopyLink}
          className="w-full py-2.5 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 border border-gray-200 transition-colors flex items-center justify-center gap-2"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-500" />
              Link Copied!
            </>
          ) : (
            <>
              File Link
            </>
          )}
        </button>
      </div>
    </div>
  )
}
