import { useEffect, useState } from 'react'
import { api } from '../lib/api'

type Slider = { id: string; title: string; imageUrl: string; linkUrl?: string; description?: string; order: number; isActive: boolean }

export default function Sliders() {
  const [items, setItems] = useState<Slider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/admin/home-sliders')
      setItems(res.data.sliders)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load sliders')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-4">Home Sliders</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <div className="grid md:grid-cols-2 gap-4">
          {items.map((s) => (
            <div key={s.id} className="bg-white border rounded p-3">
              <p className="font-semibold">{s.title}</p>
              <p className="text-sm text-gray-500">Order: {s.order} • {s.isActive ? 'Active' : 'Inactive'}</p>
              <a href={s.linkUrl} className="text-primary text-sm" target="_blank">{s.linkUrl}</a>
              <p className="text-sm">{s.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


