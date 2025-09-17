import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
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

  // Load existing prize structure on mount
  useEffect(() => {
    (async () => {
      if (!id) return
      try {
        const res = await api.get(`/admin/contests/${id}/prize-structure`)
        const items = (res.data?.items || []) as any[]
        if (items.length > 0) {
          setRows(items.map(it => ({
            prizeRank: Number(it.prizeRank) || 0,
            prizeAmount: Number(it.prizeAmount) || 0,
            numberOfWinners: Number(it.numberOfWinners) || 0,
            prizeDescription: it.prizeDescription || '',
            winnersSeatNumbers: Array.isArray(it.winnersSeatNumbers) ? it.winnersSeatNumbers.join(',') : (it.winnersSeatNumbers || '')
          })))
        }
      } catch (e) {
        // ignore load errors; start with defaults
      }
    })()
  }, [id])

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

  const calculateTotalPrize = () => {
    return rows.reduce((sum, row) => sum + (row.prizeAmount * row.numberOfWinners), 0)
  }

  const getRankSuffix = (rank: number) => {
    if (rank === 1) return 'st'
    if (rank === 2) return 'nd'
    if (rank === 3) return 'rd'
    return 'th'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link 
          to="/contests" 
          className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition-all duration-200"
        >
          <span className="text-xl">←</span>
        </Link>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            Prize Structure
          </h1>
          <p className="text-gray-600 mt-1">Define prizes and winners for contest #{id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Form */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
                <span className="text-3xl">🏆</span>
                Prize Structure Configuration
              </h2>
              <p className="text-gray-600">Define prizes and winners for your lottery contest</p>
            </div>
            
            <form onSubmit={submit} className="space-y-8">
              <div className="space-y-6">
                {rows.map((row, i) => (
                  <div key={i} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-6 border border-gray-200 shadow-lg">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary to-yellow-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                          {row.prizeRank}
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-800">
                            {row.prizeRank}{getRankSuffix(row.prizeRank)} Place Prize
                          </h3>
                          <p className="text-sm text-gray-500">Prize Level #{row.prizeRank}</p>
                        </div>
                      </div>
                      <button 
                        type="button" 
                        onClick={() => removeRow(i)}
                        className="p-3 text-red-500 hover:bg-red-50 rounded-xl transition-all duration-200 hover:shadow-md"
                      >
                        <span className="text-xl">🗑️</span>
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Rank Position
                        </label>
                        <div className="relative">
                          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-lg">#</span>
                          <input 
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                            type="number" 
                            value={row.prizeRank} 
                            onChange={(e) => update(i, 'prizeRank', e.target.value)} 
                            placeholder="1"
                            min="1"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Prize Amount (₹)
                        </label>
                        <div className="relative">
                          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-lg">₹</span>
                          <input 
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                            type="number" 
                            value={row.prizeAmount} 
                            onChange={(e) => update(i, 'prizeAmount', e.target.value)} 
                            placeholder="100000"
                            min="0"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Number of Winners
                        </label>
                        <div className="relative">
                          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-lg">👥</span>
                          <input 
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                            type="number" 
                            value={row.numberOfWinners} 
                            onChange={(e) => update(i, 'numberOfWinners', e.target.value)} 
                            placeholder="1"
                            min="1"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Total Prize Value
                        </label>
                        <div className="w-full bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl px-4 py-3 text-green-700 font-bold text-lg">
                          ₹{(row.prizeAmount * row.numberOfWinners).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Description (Optional)
                        </label>
                        <div className="relative">
                          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-lg">📝</span>
                          <input 
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent transition-all" 
                            value={row.prizeDescription || ''} 
                            onChange={(e) => update(i, 'prizeDescription', e.target.value)} 
                            placeholder="e.g., Grand Prize, First Runner-up"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          Fixed Seat Numbers (Optional)
                        </label>
                        <div className="relative">
                          <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-lg">🎯</span>
                          <input 
                            className="w-full border border-gray-200 rounded-xl pl-10 pr-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent transition-all" 
                            value={row.winnersSeatNumbers || ''} 
                            onChange={(e) => update(i, 'winnersSeatNumbers', e.target.value)} 
                            placeholder="e.g., 156,36,256,589"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                          <span>💡</span>
                          <span>Comma-separated seat numbers for guaranteed winners</span>
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-4 pt-8">
                <button 
                  type="button" 
                  onClick={addRow}
                  className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium"
                >
                  <span className="text-xl">➕</span>
                  Add Prize Level
                </button>
                <div className="text-sm text-gray-500">
                  {rows.length} prize level{rows.length !== 1 ? 's' : ''} configured
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <div className="flex items-center gap-2">
                    <span className="text-red-500 text-xl">⚠️</span>
                    <p className="text-red-700 font-medium">{error}</p>
                  </div>
                </div>
              )}

              <div className="flex gap-4 pt-6">
                <button 
                  type="button"
                  onClick={() => nav('/contests')}
                  className="flex-1 px-6 py-3 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={loading || rows.length === 0}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Saving Prize Structure...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-xl">🏆</span>
                      Save Prize Structure
                    </div>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Summary */}
        <div className="space-y-6">
          {/* Prize Summary */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <span className="text-2xl">💰</span>
              Prize Summary
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-blue-700 font-medium">Total Prize Levels</span>
                  <span className="text-2xl font-bold text-blue-800">{rows.length}</span>
                </div>
                <p className="text-xs text-blue-600">Number of prize categories</p>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-green-700 font-medium">Total Winners</span>
                  <span className="text-2xl font-bold text-green-800">
                    {rows.reduce((sum, row) => sum + row.numberOfWinners, 0)}
                  </span>
                </div>
                <p className="text-xs text-green-600">Total number of winners</p>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl border border-purple-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-700 font-medium">Total Prize Value</span>
                  <span className="text-2xl font-bold text-purple-800">₹{calculateTotalPrize().toLocaleString()}</span>
                </div>
                <p className="text-xs text-purple-600">Total prize money to distribute</p>
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <span className="text-2xl">📝</span>
              Instructions
            </h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-blue-500 text-xl mt-1">1</span>
                <div>
                  <span className="font-medium text-blue-800">Set prize ranks in ascending order</span>
                  <p className="text-sm text-blue-600">1st, 2nd, 3rd, etc.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <span className="text-green-500 text-xl mt-1">2</span>
                <div>
                  <span className="font-medium text-green-800">Specify number of winners</span>
                  <p className="text-sm text-green-600">How many people win each prize level</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                <span className="text-purple-500 text-xl mt-1">3</span>
                <div>
                  <span className="font-medium text-purple-800">Use fixed seat numbers for guaranteed winners</span>
                  <p className="text-sm text-purple-600">Specify exact seat numbers that will win</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg border border-orange-200">
                <span className="text-orange-500 text-xl mt-1">4</span>
                <div>
                  <span className="font-medium text-orange-800">Leave seat numbers empty for random selection</span>
                  <p className="text-sm text-orange-600">System will randomly select winners</p>
                </div>
              </div>
            </div>
          </div>

          {/* Example */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <span className="text-2xl">💡</span>
              Example Configuration
            </h3>
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border border-yellow-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                    1
                  </div>
                  <div className="font-bold text-gray-800">1st Place: ₹100,000 (1 winner)</div>
                </div>
                <div className="text-sm text-gray-600 ml-11">Fixed seats: 156, 36, 256</div>
              </div>
              <div className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-gray-400 to-gray-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                    2
                  </div>
                  <div className="font-bold text-gray-800">2nd Place: ₹50,000 (3 winners)</div>
                </div>
                <div className="text-sm text-gray-600 ml-11">Random selection from all participants</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


