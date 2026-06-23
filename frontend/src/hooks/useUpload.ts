import { useCallback } from 'react'
import { useTransactionStore } from '@/store/transactionStore'
import type { ProcessingStatus } from '@/api/types'

interface UseUploadReturn {
  status: ProcessingStatus
  error: string | null
  statementId: string | null
  filename: string | null
  uploadFile: (file: File) => Promise<string | null>
  reset: () => void
}

export function useUpload(): UseUploadReturn {
  const { status, error, statementId, filename, uploadFile, reset } = useTransactionStore()

  const handleUpload = useCallback(async (file: File): Promise<string | null> => {
    return uploadFile(file)
  }, [uploadFile])

  return {
    status,
    error,
    statementId,
    filename,
    uploadFile: handleUpload,
    reset,
  }
}
