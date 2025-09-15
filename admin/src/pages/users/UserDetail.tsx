import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../../lib/api'

export default function UserDetail() {
  const { id } = useParams()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/users/${id}`)
        setData(res.data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load user')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  if (loading) return <p>Loading...</p>
  if (error) return <p className="text-red-600">{error}</p>
  if (!data) return null

  const rows = [
    ['userId', data.userId],
    ['userName', data.userName],
    ['email', data.email],
    ['phoneNumber', data.phoneNumber],
    ['city', data.city],
    ['state', data.state],
    ['walletBalance', `₹${data.walletBalance}`],
    ['isActive', String(data.isActive)],
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-4">User - {data.userId}</h1>
      <div className="bg-white border rounded p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {rows.map(([k,v])=> (
            <div key={k}>
              <p className="text-xs text-gray-500">{k}</p>
              <p className="font-semibold">{v}</p>
            </div>
          ))}
        </div>
        {data.bankDetails && (
          <div className="mt-6">
            <p className="font-bold mb-2">Bank Details</p>
            <pre className="bg-gray-50 p-3 rounded text-sm overflow-auto">{JSON.stringify(data.bankDetails, null, 2)}</p>
          </div>
        )}
      </div>
    </div>
  )
}


