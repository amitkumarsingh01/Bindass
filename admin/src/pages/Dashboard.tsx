import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { AdminDashboard } from '../lib/api'

export default function Dashboard() {
  const [data, setData] = useState<AdminDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/admin/dashboard')
        setData(res.data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) return <p>Loading...</p>
  if (error) return <p className="text-red-600">{error}</p>
  if (!data) return null

  const cards = [
    { label: 'Users', value: data.users.total },
    { label: 'Active Users', value: data.users.active },
    { label: 'Contests', value: data.contests.total },
    { label: 'Active Contests', value: data.contests.active },
    { label: 'Transactions', value: data.transactions.total },
    { label: 'Pending Withdrawals', value: data.withdrawals.pending },
    { label: 'Prize Distributed', value: `₹${data.prizeMoney.totalDistributed}` },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="bg-white border rounded p-4 shadow-sm">
            <p className="text-gray-500 text-sm">{c.label}</p>
            <p className="text-2xl font-bold">{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}


