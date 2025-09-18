import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../../lib/api'

export default function PrizeSettings() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [contest, setContest] = useState<any>(null)
  const [totalWinners, setTotalWinners] = useState(0)
  const [cashbackforhighest, setCashbackforhighest] = useState<number | null>(null)

  const loadContest = async () => {
    if (!id) return
    
    setLoading(true)
    setError('')
    try {
      const res = await api.get(`/api/contests/${id}`)
      setContest(res.data)
      setTotalWinners(res.data.totalWinners || 0)
      setCashbackforhighest(res.data.cashbackforhighest || null)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load contest')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadContest() }, [id])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    
    setSaving(true)
    setError('')
    setSuccess('')
    
    try {
      await api.put(`/api/admin/contests/${id}/prize-settings`, {
        totalWinners,
        cashbackforhighest
      })
      setSuccess('Prize settings updated successfully')
      await loadContest() // Refresh data
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to update prize settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading contest details...</p>
        </div>
      </div>
    )
  }

  if (!contest) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Contest Not Found</h3>
        <p className="text-red-600">The requested contest could not be found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
        >
          <span className="text-2xl">←</span>
        </button>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            Prize Settings
          </h1>
          <p className="text-gray-600 mt-1">Configure total winners and cashback for highest prize</p>
        </div>
      </div>

      {/* Contest Info */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-primary to-yellow-500 rounded-xl flex items-center justify-center">
            <span className="text-2xl text-white">🎯</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">{contest.contestName}</h2>
            <p className="text-gray-600">Ticket Price: ₹{contest.ticketPrice} • Total Prize: ₹{contest.totalPrizeMoney?.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700">{error}</div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4 text-green-700">{success}</div>
      )}

      {/* Prize Settings Form */}
      <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-lg font-semibold text-gray-800 mb-3">
                Total Winners
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">🏆</span>
                <input
                  type="number"
                  className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg"
                  value={totalWinners}
                  onChange={(e) => setTotalWinners(parseInt(e.target.value) || 0)}
                  min="0"
                  placeholder="Enter total number of winners"
                />
              </div>
              <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                <span>💡</span>
                <span>Total number of winners for this contest</span>
              </p>
            </div>

            <div>
              <label className="block text-lg font-semibold text-gray-800 mb-3">
                Cashback for Highest Prize
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">💰</span>
                <input
                  type="number"
                  step="0.01"
                  className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg"
                  value={cashbackforhighest || ''}
                  onChange={(e) => setCashbackforhighest(e.target.value ? parseFloat(e.target.value) : null)}
                  min="0"
                  placeholder="Enter cashback amount"
                />
              </div>
              <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                <span>💡</span>
                <span>Additional cashback for the highest prize winner (optional)</span>
              </p>
            </div>
          </div>

          <div className="flex gap-4 pt-6">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex-1 px-6 py-4 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium text-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-6 py-4 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium text-lg disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Update Prize Settings'}
            </button>
          </div>
        </form>
      </div>

      {/* Current Values Display */}
      <div className="bg-gray-50 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <span className="text-xl">📊</span>
          Current Settings
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl p-4 border border-gray-200">
            <div className="text-sm text-gray-500">Total Winners</div>
            <div className="text-2xl font-bold text-gray-800">{totalWinners}</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-200">
            <div className="text-sm text-gray-500">Cashback for Highest</div>
            <div className="text-2xl font-bold text-gray-800">
              {cashbackforhighest ? `₹${cashbackforhighest.toLocaleString()}` : 'Not set'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
