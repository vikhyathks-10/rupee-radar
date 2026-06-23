// API response types — mirrors backend Pydantic schemas

export interface HealthResponse {
  status: string
  service: string
  version: string
}

export interface UploadResponse {
  statement_id: string
  status: 'processing' | 'completed' | 'failed'
  transaction_count: number
}

export interface Transaction {
  id: string
  date: string
  description: string
  original_description: string
  amount: number
  category: string
  is_recurring: boolean
  confidence: number | null
}

export interface TransactionsResponse {
  transactions: Transaction[]
  total: number
}

export interface CategoryBreakdown {
  name: string
  total: number
  count: number
  percentage: number
}

export interface CategoriesResponse {
  categories: CategoryBreakdown[]
}

export interface RecurringItem {
  merchant: string
  amount: number
  frequency: string
  occurrences: number
  next_expected_date: string | null
  annual_cost: number
  category: string
}

export interface RecurringResponse {
  recurring: RecurringItem[]
}

export interface BiggestTransaction {
  description: string
  amount: number
  date: string
}

export interface MonthlyBreakdown {
  month: string
  income: number
  spend: number
}

export interface MetricsResponse {
  total_income: number
  total_spend: number
  savings: number
  savings_rate: number | null
  top_categories: CategoryBreakdown[]
  biggest_transactions: BiggestTransaction[]
  monthly_breakdown: MonthlyBreakdown[]
}

export interface Insight {
  id: string
  title: string
  description: string
  severity: 'info' | 'warning' | 'critical'
  category: string | null
  amount_referenced: number | null
}

export interface InsightsResponse {
  insights: Insight[]
}

export type ProcessingStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error'
