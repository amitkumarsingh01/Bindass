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
                  <td className="p-2 space-x-2">
                    <Link to={`/contests/${c.id}/prize-structure`} className="text-primary">Prizes</Link>
                    <Link to={`/contests/${c.id}/draw`} className="text-primary">Draw</Link>
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


