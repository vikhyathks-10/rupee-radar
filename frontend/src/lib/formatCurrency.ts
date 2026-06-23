export function formatCurrency(amount: number): string {
  if (amount === 0) return '₹0'

  const abs = Math.abs(amount)
  const sign = amount < 0 ? '-' : ''

  if (abs >= 10000000) {
    return `${sign}₹${(abs / 10000000).toFixed(2)} Cr`
  }
  if (abs >= 100000) {
    return `${sign}₹${(abs / 100000).toFixed(2)} L`
  }

  return `${sign}₹${abs.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}
