import { useEffect, useState } from 'react'
import { api } from '../lib/api'

type Withdrawal = {
  id: string
  amount: number
  status: string
  user: { userId: string; userName: string; phoneNumber: string }
  bankDetails?: { bankName?: string; accountNumber?: string }
}

export default function Withdrawals() {
  const [items, setItems] = useState<Withdrawal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/admin/withdrawals')
      setItems(res.data.withdrawals)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load withdrawals')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const updateStatus = async (id: string, status: string) => {
    try {
      await api.put(`/admin/withdrawals/${id}/status`, null, { params: { status } })
      await load()
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to update status')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-4">Withdrawals</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <div className="overflow-x-auto bg-white border rounded">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-2 text-left">User</th>
                <th className="p-2 text-left">Amount</th>
                <th className="p-2 text-left">Status</th>
                <th className="p-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((w) => (
                <tr key={w.id} className="border-t">
                  <td className="p-2">{w.user.userName} ({w.user.userId})</td>
                  <td className="p-2">₹{w.amount}</td>
                  <td className="p-2">{w.status}</td>
                  <td className="p-2 space-x-2">
                    <button onClick={()=>updateStatus(w.id, 'processing')} className="px-2 py-1 border rounded">Process</button>
                    <button onClick={()=>updateStatus(w.id, 'completed')} className="px-2 py-1 border rounded">Complete</button>
                    <button onClick={()=>updateStatus(w.id, 'rejected')} className="px-2 py-1 border rounded text-red-600">Reject</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


