import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../lib/api'

type User = {
  id: string
  userId: string
  userName: string
  email: string
  phoneNumber: string
  walletBalance?: number
  isActive?: boolean
}

export default function Users() {
  const [items, setItems] = useState<User[]>([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/users', { params: { q, limit: 50 } })
      setItems(res.data.items)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-primary">Users</h1>
        <div className="flex items-center gap-2">
          <input className="border rounded px-2 py-1" placeholder="Search" value={q} onChange={e=>setQ(e.target.value)} />
          <button onClick={load} className="px-3 py-1 border rounded">Search</button>
        </div>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <div className="overflow-x-auto bg-white border rounded">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-2">userId</th>
                <th className="text-left p-2">Name</th>
                <th className="text-left p-2">Email</th>
                <th className="text-left p-2">Phone</th>
                <th className="text-left p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((u)=> (
                <tr key={u.id} className="border-t">
                  <td className="p-2">{u.userId}</td>
                  <td className="p-2">{u.userName}</td>
                  <td className="p-2">{u.email}</td>
                  <td className="p-2">{u.phoneNumber}</td>
                  <td className="p-2">
                    <Link to={`/users/${u.userId}`} className="text-primary">View</Link>
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


