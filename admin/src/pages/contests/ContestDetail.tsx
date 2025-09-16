import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../../lib/api'

export default function ContestDetail() {
  const { id } = useParams()
  const [overview, setOverview] = useState<any>(null)
  const [purchases, setPurchases] = useState<any>({ items: [], byCategory: [] })
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [winners, setWinners] = useState<any[]>([])
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined)
  const [tab, setTab] = useState<'overview'|'purchases'|'leaderboard'|'winners'>('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    (async () => {
      try {
        // Try admin endpoints first; if not available, fall back to public ones
        let o, p
        try {
          o = await api.get(`/admin/contests/${id}/overview`)
        } catch {
          o = await api.get(`/contests/${id}`)
        }
        try {
          p = await api.get(`/admin/contests/${id}/purchases`, { params: { categoryId } })
        } catch {
          // Fallback: fetch category-wise purchased seats and flatten (first category only)
          p = { data: { items: [], byCategory: [] } }
        }
        const lb = await api.get(`/contests/${id}/leaderboard`)
        const w = await api.get(`/contests/${id}/winners`)
        setOverview(o.data)
        setPurchases(p.data)
        setLeaderboard(lb.data?.leaderboard || lb.data || [])
        setWinners(w.data?.winners || w.data || [])
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load contest details')
      } finally {
        setLoading(false)
      }
    })()
  }, [id, categoryId])

  if (loading) return <p>Loading...</p>
  if (error) return <p className="text-red-600">{error}</p>

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">{overview?.contestName}</h1>
        <div className="text-sm text-gray-600 text-right">
          <div>Ticket ₹{overview?.ticketPrice} • Prize ₹{overview?.totalPrizeMoney}</div>
          <div>
            <span className="mr-3">Start: {overview?.contestStartDate ? new Date(overview.contestStartDate).toLocaleString() : '-'}</span>
            <span className="mr-3">End: {overview?.contestEndDate ? new Date(overview.contestEndDate).toLocaleString() : '-'}</span>
            <span>Draw: {overview?.drawDate ? new Date(overview.drawDate).toLocaleString() : '-'}</span>
          </div>
        </div>
      </header>

      <nav className="flex items-center gap-2 border-b">
        {['overview','purchases','leaderboard','winners'].map((t)=> (
          <button key={t} onClick={()=>setTab(t as any)} className={`px-3 py-2 ${tab===t? 'border-b-2 border-primary text-primary' : 'text-gray-600'}`}>{t[0].toUpperCase()+t.slice(1)}</button>
        ))}
      </nav>

      {tab==='overview' && (
        <section className="grid md:grid-cols-3 gap-4">
          <StatCard title="Total Seats" value={overview?.totalSeats} />
          <StatCard title="Purchased" value={overview?.purchasedSeats || 0} />
          <StatCard title="Available" value={(overview?.totalSeats || 0) - (overview?.purchasedSeats || 0)} />
        </section>
      )}

      {tab==='purchases' && (
        <section className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">Purchases</h2>
            <div className="flex items-center gap-2">
              <select className="border rounded px-2 py-1" value={categoryId || ''} onChange={(e)=>setCategoryId(e.target.value? Number(e.target.value): undefined)}>
                <option value="">All Categories</option>
                {overview?.categories?.map((c:any)=> (
                  <option key={c.categoryId} value={c.categoryId}>{c.categoryId}. {c.categoryName}</option>
                ))}
              </select>
            </div>
          </div>
          {(!purchases.items || purchases.items.length===0) && (
            <p className="text-sm text-gray-600 mb-3">No purchases found yet. Once users buy seats, they will show here with user and seat details.</p>
          )}
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left p-2">Category</th>
                  <th className="text-left p-2">Seat</th>
                  <th className="text-left p-2">User</th>
                  <th className="text-left p-2">Phone</th>
                </tr>
              </thead>
              <tbody>
                {purchases.items.map((it:any, idx:number)=> (
                  <tr key={idx} className="border-t">
                    <td className="p-2">{it.categoryName} ({it.categoryId})</td>
                    <td className="p-2">{it.seatNumber}</td>
                    <td className="p-2">{it.userName} ({it.userId})</td>
                    <td className="p-2">{it.phoneNumber}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {tab==='leaderboard' && (
        <section className="card">
          <h2 className="font-semibold mb-3">Leaderboard (Top buyers)</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50"><tr><th className="text-left p-2">User</th><th className="text-left p-2">Seats</th><th className="text-left p-2">Amount</th></tr></thead>
              <tbody>
                {leaderboard.map((row:any, i:number)=> (
                  <tr key={i} className="border-t">
                    <td className="p-2">{row.userName} ({row.userId})</td>
                    <td className="p-2">{row.totalPurchases}</td>
                    <td className="p-2">₹{row.totalAmount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {tab==='winners' && (
        <section className="card">
          <h2 className="font-semibold mb-3">Winners</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50"><tr><th className="text-left p-2">Rank</th><th className="text-left p-2">User</th><th className="text-left p-2">Seat</th><th className="text-left p-2">Amount</th><th className="text-left p-2">Category</th></tr></thead>
              <tbody>
                {winners.map((w:any, i:number)=> (
                  <tr key={i} className="border-t">
                    <td className="p-2">{w.prizeRank}</td>
                    <td className="p-2">{w.userName} ({w.userId})</td>
                    <td className="p-2">{w.seatNumber}</td>
                    <td className="p-2">₹{w.prizeAmount}</td>
                    <td className="p-2">{w.categoryName}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div className="card">
      <div className="text-sm text-gray-600">{title}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  )
}


