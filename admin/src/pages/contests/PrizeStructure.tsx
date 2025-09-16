import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../../lib/api'

type Prize = { prizeRank: number; prizeAmount: number; numberOfWinners: number; prizeDescription?: string; winnersSeatNumbers?: string }

export default function PrizeStructure() {
  const { id } = useParams()
  const nav = useNavigate()
  const [rows, setRows] = useState<Prize[]>([
    { prizeRank: 1, prizeAmount: 100000, numberOfWinners: 1 },
    { prizeRank: 2, prizeAmount: 90000, numberOfWinners: 1 },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setError('')
    setLoading(true)
    try {
      // Convert CSV seat numbers string -> number[]
      const payload = rows.map(r => ({
        prizeRank: r.prizeRank,
        prizeAmount: r.prizeAmount,
        numberOfWinners: r.numberOfWinners,
        prizeDescription: r.prizeDescription,
        winnersSeatNumbers: r.winnersSeatNumbers ? r.winnersSeatNumbers.split(',').map(s=>Number(s.trim())).filter(n=>!Number.isNaN(n)) : undefined,
      }))
      await api.post(`/admin/contests/${id}/prize-structure`, payload)
      nav('/contests', { replace: true })
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to add prize structure')
    } finally {
      setLoading(false)
    }
  }

  const update = (i: number, key: keyof Prize, value: string) => {
    setRows((prev) => prev.map((r, idx) => idx === i ? { ...r, [key]: key === 'winnersSeatNumbers' ? value : (key.includes('Amount') || key.includes('Winners') || key === 'prizeRank' ? Number(value) : value) } as Prize : r))
  }

  const addRow = () => setRows((p) => [...p, { prizeRank: p.length + 1, prizeAmount: 0, numberOfWinners: 1 }])
  const removeRow = (i: number) => setRows((p) => p.filter((_, idx) => idx !== i))

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-4">Prize Structure</h1>
      <form onSubmit={submit} className="space-y-4">
        <div className="space-y-2">
          {rows.map((r, i) => (
            <div key={i} className="grid grid-cols-1 md:grid-cols-6 gap-2 bg-white border rounded p-3">
              <input className="border rounded px-2 py-1" type="number" value={r.prizeRank} onChange={(e)=>update(i,'prizeRank', e.target.value)} placeholder="Rank" />
              <input className="border rounded px-2 py-1" type="number" value={r.prizeAmount} onChange={(e)=>update(i,'prizeAmount', e.target.value)} placeholder="Amount" />
              <input className="border rounded px-2 py-1" type="number" value={r.numberOfWinners} onChange={(e)=>update(i,'numberOfWinners', e.target.value)} placeholder="# Winners" />
              <input className="border rounded px-2 py-1 md:col-span-2" value={r.prizeDescription || ''} onChange={(e)=>update(i,'prizeDescription', e.target.value)} placeholder="Description (optional)" />
              <input className="border rounded px-2 py-1 md:col-span-2" value={r.winnersSeatNumbers || ''} onChange={(e)=>update(i,'winnersSeatNumbers', e.target.value)} placeholder="Seat numbers CSV (e.g. 156,36,256)" />
              <button type="button" onClick={()=>removeRow(i)} className="text-red-600">Remove</button>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={addRow} className="px-3 py-2 border rounded">Add Row</button>
          <button disabled={loading} className="bg-primary text-white px-3 py-2 rounded">{loading ? 'Saving...' : 'Save Prize Structure'}</button>
        </div>
        {error && <p className="text-red-600">{error}</p>}
      </form>
    </div>
  )
}


