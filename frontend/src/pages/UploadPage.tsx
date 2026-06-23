import { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Loader2, AlertCircle } from 'lucide-react'
import { useTransactionStore } from '@/store/transactionStore'

const PIPELINE_STEPS = [
  "Parsing bank statement CSV/PDF...",
  "Cleaning and normalizing transactions...",
  "Categorizing transactions (hybrid rules + AI)...",
  "Detecting recurring subscriptions & EMIs...",
  "Calculating financial metrics...",
  "Generating AI-powered insights...",
]

export default function UploadPage() {
  const navigate = useNavigate()
  const { uploadFile, status, error } = useTransactionStore()
  const [file, setFile] = useState<File | null>(null)
  const [dragging, setDragging] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const handleFile = (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase()
    if (ext !== 'csv' && ext !== 'pdf') {
      setFile(null)
      return
    }
    setFile(f)
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0])
  }, [])

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(true)
  }, [])

  const onDragLeave = useCallback(() => setDragging(false), [])

  const uploading = status === 'uploading' || status === 'processing'

  useEffect(() => {
    let interval: number
    if (uploading) {
      interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev < PIPELINE_STEPS.length - 1) {
            return prev + 1
          }
          return prev
        })
      }, 1800)
    } else {
      setCurrentStep(0)
    }
    return () => clearInterval(interval)
  }, [uploading])

  const handleUpload = async () => {
    if (!file) return
    setCurrentStep(0)
    const sid = await uploadFile(file)
    if (sid) {
      navigate(`/dashboard?sid=${sid}`)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50/50">
      <div className="max-w-lg w-full px-6 py-12">
        <div className="text-center">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2.5 mb-2">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-200">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">RupeeRadar</h1>
          </div>
          <p className="text-gray-500 mb-8 font-medium">AI-powered personal finance assistant for Indian bank statements</p>

          {/* Drop zone */}
          <div
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            className={`relative p-10 border-2 border-dashed rounded-2xl transition-all cursor-pointer ${
              dragging
                ? 'border-indigo-500 bg-indigo-50 shadow-md scale-[1.01]'
                : file
                  ? 'border-green-400 bg-green-50/50'
                  : 'border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-50/10'
            }`}
            onClick={() => !uploading && document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".csv,.pdf"
              className="hidden"
              disabled={uploading}
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />

            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileText className="w-12 h-12 text-green-500" />
                <p className="text-green-800 font-semibold">{file.name}</p>
                <p className="text-sm text-green-600 font-medium">{(file.size / 1024).toFixed(1)} KB</p>
                {!uploading && <p className="text-xs text-gray-400 mt-2 bg-white px-3 py-1 rounded-full border">Click to change file</p>}
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <Upload className={`w-12 h-12 transition-colors ${dragging ? 'text-indigo-500 animate-bounce' : 'text-gray-400'}`} />
                <p className="text-gray-600 font-semibold">Drop your bank statement here</p>
                <p className="text-sm text-gray-400">or click to browse from device</p>
                <p className="text-xs text-gray-400 mt-2">Supports CSV and PDF formats</p>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="mt-4 flex items-center gap-2 text-red-700 bg-red-50 border border-red-100 rounded-xl px-4 py-3 text-left">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          )}

          {/* Upload button */}
          {file && !uploading && (
            <button
              onClick={handleUpload}
              className="mt-6 w-full py-3.5 rounded-xl font-semibold text-white transition-all bg-indigo-600 hover:bg-indigo-700 flex items-center justify-center gap-2 shadow-lg shadow-indigo-100"
            >
              <Upload className="w-5 h-5" />
              Upload & Analyze
            </button>
          )}

          {/* Simulated progress checklist */}
          {uploading && (
            <div className="mt-8 text-left bg-white border rounded-2xl p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-gray-900 text-sm">Processing Pipeline</h3>
                <div className="flex items-center gap-2 text-xs text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Analyzing
                </div>
              </div>
              <div className="space-y-3">
                {PIPELINE_STEPS.map((step, idx) => {
                  const isCompleted = idx < currentStep
                  const isActive = idx === currentStep
                  return (
                    <div key={idx} className="flex items-center gap-3 text-sm">
                      <span
                        className={`w-3 h-3 rounded-full shrink-0 border transition-all ${
                          isCompleted
                            ? 'bg-green-500 border-green-500 shadow-sm shadow-green-150'
                            : isActive
                              ? 'bg-indigo-600 border-indigo-600 animate-pulse'
                              : 'bg-gray-50 border-gray-200'
                        }`}
                      />
                      <span
                        className={`transition-colors ${
                          isCompleted
                            ? 'text-green-600 font-medium'
                            : isActive
                              ? 'text-indigo-600 font-semibold'
                              : 'text-gray-400'
                        }`}
                      >
                        {step}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
