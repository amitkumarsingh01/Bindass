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
  purchasedSeats?: number
  contestStartDate?: string
  contestEndDate?: string
  drawDate?: string
  isDrawCompleted?: boolean
}

export default function Contests() {
  const [items, setItems] = useState<Contest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState<string>('')
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

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

  const remove = async (id: string) => {
    if (!confirm('Are you sure you want to delete this contest? This action cannot be undone.')) return
    setBusyId(id)
    try {
      await api.delete(`/admin/contests/${id}`)
      setItems((p) => p.filter((c) => c.id !== id))
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to delete contest')
    } finally {
      setBusyId('')
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getStatusColor = (status: string, isDrawCompleted?: boolean) => {
    if (isDrawCompleted) return 'bg-purple-100 text-purple-700'
    if (status === 'active') return 'bg-green-100 text-green-700'
    if (status === 'completed') return 'bg-gray-100 text-gray-700'
    return 'bg-yellow-100 text-yellow-700'
  }

  const getStatusText = (status: string, isDrawCompleted?: boolean) => {
    if (isDrawCompleted) return 'Draw Completed'
    if (status === 'active') return 'Active'
    if (status === 'completed') return 'Completed'
    return 'Pending'
  }

  const filteredItems = items.filter(contest => {
    if (filter === 'all') return true
    if (filter === 'active') return contest.status === 'active' && !contest.isDrawCompleted
    if (filter === 'completed') return contest.isDrawCompleted || contest.status === 'completed'
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading contests...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading Contests</h3>
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            Contest Management
          </h1>
          <p className="text-gray-600 mt-1">Create, manage, and monitor all lottery contests</p>
        </div>
        
        <Link 
          to="/contests/create" 
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium"
        >
          <span className="text-xl">➕</span>
          Create New Contest
        </Link>
      </div>

      {/* Filters and Stats */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Filter by status:</span>
            <div className="flex gap-2">
              {[
                { key: 'all', label: 'All', count: items.length },
                { key: 'active', label: 'Active', count: items.filter(c => c.status === 'active' && !c.isDrawCompleted).length },
                { key: 'completed', label: 'Completed', count: items.filter(c => c.isDrawCompleted || c.status === 'completed').length }
              ].map(({ key, label, count }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key as any)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    filter === key
                      ? 'bg-primary text-white shadow-md'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {label} ({count})
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span>Total: {items.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Active: {items.filter(c => c.status === 'active' && !c.isDrawCompleted).length}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
              <span>Completed: {items.filter(c => c.isDrawCompleted || c.status === 'completed').length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Contest Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredItems.map((contest, index) => (
          <div
            key={contest.id}
            className="bg-white rounded-2xl shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-primary to-yellow-500 p-6 text-white">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-2">{contest.contestName}</h3>
                  <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
                    getStatusColor(contest.status, contest.isDrawCompleted)
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${
                      contest.isDrawCompleted ? 'bg-purple-500' :
                      contest.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'
                    }`}></div>
                    {getStatusText(contest.status, contest.isDrawCompleted)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">₹{contest.ticketPrice}</div>
                  <div className="text-sm opacity-75">per ticket</div>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="space-y-4">
                {/* Prize Money */}
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">💰</span>
                    <div>
                      <p className="text-sm text-gray-500">Total Prize</p>
                      <p className="text-xl font-bold text-green-700">₹{contest.totalPrizeMoney.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                {/* Seats Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-xl">
                    <div className="text-2xl font-bold text-gray-800">{contest.totalSeats.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">Total Seats</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-xl">
                    <div className="text-2xl font-bold text-blue-700">{contest.availableSeats.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">Available</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                    <span>Seats Sold</span>
                    <span>{((contest.totalSeats - contest.availableSeats) / contest.totalSeats * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-primary to-yellow-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${((contest.totalSeats - contest.availableSeats) / contest.totalSeats) * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Dates */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <span>📅</span>
                    <span>Start: {formatDate(contest.contestStartDate)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <span>🏁</span>
                    <span>End: {formatDate(contest.contestEndDate)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <span>🎲</span>
                    <span>Draw: {formatDate(contest.drawDate)}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6 pt-4 border-t border-gray-100">
                <div className="grid grid-cols-2 gap-2">
                  <Link
                    to={`/contests/${contest.id}`}
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:shadow-lg transition-all duration-200 text-sm font-medium text-center"
                  >
                    View Details
                  </Link>
                  <Link
                    to={`/contests/${contest.id}/prize-structure`}
                    className="px-4 py-2 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-200 text-sm font-medium text-center"
                  >
                    Manage Prizes
                  </Link>
                </div>
                <div className="mt-2 flex gap-2">
                  <Link
                    to={`/contests/${contest.id}/draw`}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:shadow-lg transition-all duration-200 text-sm font-medium text-center"
                  >
                    Conduct Draw
                  </Link>
                  <button
                    onClick={() => remove(contest.id)}
                    disabled={busyId === contest.id}
                    className="px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:shadow-lg transition-all duration-200 text-sm font-medium disabled:opacity-50"
                  >
                    {busyId === contest.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredItems.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No contests found</h3>
          <p className="text-gray-600 mb-4">
            {filter === 'all' 
              ? "No contests have been created yet" 
              : `No ${filter} contests found`
            }
          </p>
          <Link 
            to="/contests/create" 
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium"
          >
            <span className="text-xl">➕</span>
            Create First Contest
          </Link>
        </div>
      )}
    </div>
  )
}


