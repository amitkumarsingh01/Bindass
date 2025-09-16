import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../lib/api'

export default function CreateContest() {
  const nav = useNavigate()
  const [form, setForm] = useState({
    contestName: '',
    totalPrizeMoney: '',
    ticketPrice: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/admin/contests', {
        contestName: form.contestName,
        totalPrizeMoney: Number(form.totalPrizeMoney),
        ticketPrice: Number(form.ticketPrice),
      })
      nav('/contests', { replace: true })
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create contest')
    } finally {
      setLoading(false)
    }
  }

  const set = (k: string, v: string) => setForm((p) => ({ ...p, [k]: v }))

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-4">Create Contest</h1>
      <form onSubmit={submit} className="grid gap-4 max-w-xl bg-white border rounded p-4">
        <Field label="Contest Name">
          <input className="w-full border rounded px-3 py-2" value={form.contestName} onChange={(e)=>set('contestName', e.target.value)} />
        </Field>
        <Field label="Total Prize Money">
          <input className="w-full border rounded px-3 py-2" type="number" value={form.totalPrizeMoney} onChange={(e)=>set('totalPrizeMoney', e.target.value)} />
        </Field>
        <Field label="Ticket Price">
          <input className="w-full border rounded px-3 py-2" type="number" value={form.ticketPrice} onChange={(e)=>set('ticketPrice', e.target.value)} />
        </Field>
        {error && <p className="text-red-600">{error}</p>}
        <button disabled={loading} className="bg-primary text-white px-3 py-2 rounded hover:opacity-95 disabled:opacity-60">{loading ? 'Creating...' : 'Create Contest'}</button>
      </form>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-sm mb-1 text-gray-700">{label}</span>
      {children}
    </label>
  )
}


