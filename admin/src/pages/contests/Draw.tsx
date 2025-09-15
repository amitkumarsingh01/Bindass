import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../../lib/api'

export default function Draw() {
  const { id } = useParams()
  const nav = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)

  const conduct = async () => {
    if (!id) return
    setError('')
    setLoading(true)
    try {
      const res = await api.post(`/admin/contests/${id}/draw`)
      setResult(res.data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to conduct draw')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-4">Conduct Draw</h1>
      <div className="bg-white border rounded p-4 space-y-3">
        <p>Contest ID: {id}</p>
        <button onClick={conduct} disabled={loading} className="bg-primary text-white px-3 py-2 rounded">{loading ? 'Processing...' : 'Conduct Draw'}</button>
        {error && <p className="text-red-600">{error}</p>}
        {result && (
          <pre className="bg-gray-50 p-3 rounded overflow-auto text-sm">{JSON.stringify(result, null, 2)}</pre>
        )}
        <button onClick={()=>nav('/contests')} className="px-3 py-2 border rounded">Back</button>
      </div>
    </div>
  )
}


