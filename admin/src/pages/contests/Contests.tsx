import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../lib/api'

type Contest = {
  id: string
  contestName: string
  status: string
  totalPrizeMoney: number
  ticketPrice: number
  totalSeats: number
  availableSeats: number
}

export default function Contests() {
  const [items, setItems] = useState<Contest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState<string>('')

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/contests/')
        setItems(res.data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load contests')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const remove = async (id: string) => {
    if (!confirm('Delete this contest?')) return
    setBusyId(id)
    try {
      await api.delete(`/admin/contests/${id}`)
      setItems((p) => p.filter((c) => c.id !== id))
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to delete contest')
    } finally {
      setBusyId('')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-primary">Contests</h1>
        <Link to="/contests/create" className="bg-primary text-white px-3 py-2 rounded">Create Contest</Link>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <div className="overflow-x-auto bg-white border rounded">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-2">Name</th>
                <th className="text-left p-2">Status</th>
                <th className="text-left p-2">Prize</th>
                <th className="text-left p-2">Ticket</th>
                <th className="text-left p-2">Seats</th>
                <th className="text-left p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="p-2">{c.contestName}</td>
                  <td className="p-2">{c.status}</td>
                  <td className="p-2">₹{c.totalPrizeMoney}</td>
                  <td className="p-2">₹{c.ticketPrice}</td>
                  <td className="p-2">{c.availableSeats}/{c.totalSeats}</td>
                  <td className="p-2 space-x-3">
                    <Link to={`/contests/${c.id}/prize-structure`} className="text-primary">Prizes</Link>
                    <Link to={`/contests/${c.id}/draw`} className="text-primary">Draw</Link>
                    <button onClick={() => remove(c.id)} className="text-red-600 disabled:opacity-50" disabled={busyId===c.id}>
                      {busyId===c.id ? 'Deleting...' : 'Delete'}
                    </button>
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


