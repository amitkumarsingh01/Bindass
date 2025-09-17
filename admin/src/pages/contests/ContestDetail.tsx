import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
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

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading Contest</h3>
        <p className="text-red-600">{error}</p>
        <Link to="/contests" className="mt-4 inline-block px-4 py-2 bg-primary text-white rounded-lg hover:shadow-lg transition-all">
          Back to Contests
        </Link>
      </div>
    )
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
        <div className="flex-1">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            {overview?.contestName}
          </h1>
          <p className="text-gray-600 mt-1">Contest Details & Analytics</p>
        </div>
      </div>

      {/* Contest Header Card */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-primary to-yellow-500 p-8 text-white">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-4">
                <h2 className="text-3xl font-bold">{overview?.contestName}</h2>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  getStatusColor(overview?.status, overview?.isDrawCompleted)
                }`}>
                  {getStatusText(overview?.status, overview?.isDrawCompleted)}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎫</span>
                  <div>
                    <p className="text-sm opacity-75">Ticket Price</p>
                    <p className="text-2xl font-bold">₹{overview?.ticketPrice}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl">💰</span>
                  <div>
                    <p className="text-sm opacity-75">Total Prize</p>
                    <p className="text-2xl font-bold">₹{overview?.totalPrizeMoney?.toLocaleString()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎯</span>
                  <div>
                    <p className="text-sm opacity-75">Total Seats</p>
                    <p className="text-2xl font-bold">{overview?.totalSeats?.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-xl">
              <div className="text-3xl font-bold text-gray-800">{overview?.totalSeats?.toLocaleString()}</div>
              <div className="text-sm text-gray-500">Total Seats</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-xl">
              <div className="text-3xl font-bold text-blue-700">{(overview?.totalSeats || 0) - (overview?.availableSeats || 0)}</div>
              <div className="text-sm text-gray-500">Purchased</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-xl">
              <div className="text-3xl font-bold text-green-700">{overview?.availableSeats?.toLocaleString()}</div>
              <div className="text-sm text-gray-500">Available</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
              <span>Seats Sold</span>
              <span>{((overview?.totalSeats || 0) - (overview?.availableSeats || 0)) / (overview?.totalSeats || 1) * 100}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-primary to-yellow-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${((overview?.totalSeats || 0) - (overview?.availableSeats || 0)) / (overview?.totalSeats || 1) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
          <nav className="flex overflow-x-auto">
            {[
              { key: 'overview', label: 'Overview', icon: '📊', description: 'Contest statistics and categories' },
              { key: 'purchases', label: 'Purchases', icon: '🛒', description: 'Seat purchase history' },
              { key: 'leaderboard', label: 'Leaderboard', icon: '🏆', description: 'Top buyers ranking' },
              { key: 'winners', label: 'Winners', icon: '🎉', description: 'Prize winners list' }
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key as any)}
                className={`flex items-center gap-3 px-6 py-4 font-medium transition-all duration-200 min-w-0 flex-shrink-0 ${
                  tab === t.key
                    ? 'bg-gradient-to-r from-primary to-yellow-500 text-white shadow-lg transform scale-105'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-white hover:shadow-md'
                }`}
              >
                <span className="text-xl">{t.icon}</span>
                <div className="text-left">
                  <div className="font-semibold">{t.label}</div>
                  <div className={`text-xs ${tab === t.key ? 'text-white/80' : 'text-gray-500'}`}>
                    {t.description}
                  </div>
                </div>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-8">
          {tab === 'overview' && (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-gray-800">Contest Overview</h3>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">Live Data</span>
                </div>
              </div>
              
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">🎯</span>
                    <span className="text-sm font-medium text-blue-700">Total Categories</span>
                  </div>
                  <div className="text-3xl font-bold text-blue-800">{overview?.categories?.length || 0}</div>
                </div>
                
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">💰</span>
                    <span className="text-sm font-medium text-green-700">Revenue Generated</span>
                  </div>
                  <div className="text-3xl font-bold text-green-800">
                    ₹{((overview?.totalSeats || 0) - (overview?.availableSeats || 0)) * (overview?.ticketPrice || 0)}
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">📊</span>
                    <span className="text-sm font-medium text-purple-700">Fill Rate</span>
                  </div>
                  <div className="text-3xl font-bold text-purple-800">
                    {Math.round(((overview?.totalSeats || 0) - (overview?.availableSeats || 0)) / (overview?.totalSeats || 1) * 100)}%
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">🔥</span>
                    <span className="text-sm font-medium text-orange-700">Active Days</span>
                  </div>
                  <div className="text-3xl font-bold text-orange-800">
                    {overview?.contestStartDate ? Math.ceil((new Date().getTime() - new Date(overview.contestStartDate).getTime()) / (1000 * 60 * 60 * 24)) : 0}
                  </div>
                </div>
              </div>
              
              {/* Categories Grid */}
              <div>
                <h4 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                  <span className="text-2xl">📋</span>
                  Categories Breakdown
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {overview?.categories?.map((category: any, index: number) => (
                    <div 
                      key={category.categoryId} 
                      className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary to-yellow-500 rounded-xl flex items-center justify-center text-white font-bold">
                            {category.categoryId}
                          </div>
                          <div>
                            <h5 className="font-bold text-gray-800 text-lg">{category.categoryName}</h5>
                            <p className="text-sm text-gray-500">Category #{category.categoryId}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="text-center p-3 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-700">{category.totalSeats}</div>
                            <div className="text-xs text-blue-600">Total Seats</div>
                          </div>
                          <div className="text-center p-3 bg-green-50 rounded-lg">
                            <div className="text-2xl font-bold text-green-700">{category.availableSeats}</div>
                            <div className="text-xs text-green-600">Available</div>
                          </div>
                        </div>
                        
                        <div className="text-center p-3 bg-purple-50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-700">{category.purchasedSeats}</div>
                          <div className="text-xs text-purple-600">Purchased</div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm text-gray-600">
                            <span>Progress</span>
                            <span className="font-medium">{Math.round((category.purchasedSeats / category.totalSeats) * 100)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div 
                              className="bg-gradient-to-r from-primary to-yellow-500 h-3 rounded-full transition-all duration-500"
                              style={{ width: `${(category.purchasedSeats / category.totalSeats) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === 'purchases' && (
            <div className="space-y-6">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <h3 className="text-2xl font-bold text-gray-800">Purchase History</h3>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">📊</span>
                    <span className="text-sm text-gray-600">
                      {purchases.items?.length || 0} total purchases
                    </span>
                  </div>
                  <select 
                    className="border border-gray-200 rounded-xl px-4 py-2 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                    value={categoryId || ''} 
                    onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : undefined)}
                  >
                    <option value="">All Categories</option>
                    {overview?.categories?.map((c: any) => (
                      <option key={c.categoryId} value={c.categoryId}>
                        {c.categoryId}. {c.categoryName}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Purchase Stats */}
              {purchases.items && purchases.items.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">🛒</span>
                      <span className="text-sm font-medium text-blue-700">Total Purchases</span>
                    </div>
                    <div className="text-3xl font-bold text-blue-800">{purchases.items.length}</div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">💰</span>
                      <span className="text-sm font-medium text-green-700">Total Revenue</span>
                    </div>
                    <div className="text-3xl font-bold text-green-800">
                      ₹{purchases.items.reduce((sum: number, item: any) => sum + item.ticketPrice, 0).toLocaleString()}
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">👥</span>
                      <span className="text-sm font-medium text-purple-700">Unique Buyers</span>
                    </div>
                    <div className="text-3xl font-bold text-purple-800">
                      {new Set(purchases.items.map((item: any) => item.userId)).size}
                    </div>
                  </div>
                </div>
              )}

              {(!purchases.items || purchases.items.length === 0) ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🛒</div>
                  <h4 className="text-xl font-semibold text-gray-800 mb-2">No purchases yet</h4>
                  <p className="text-gray-600">Once users start buying seats, they will appear here with detailed information.</p>
                </div>
              ) : (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                        <tr>
                          <th className="text-left p-6 font-semibold text-gray-700">Category</th>
                          <th className="text-left p-6 font-semibold text-gray-700">Seat Number</th>
                          <th className="text-left p-6 font-semibold text-gray-700">User</th>
                          <th className="text-left p-6 font-semibold text-gray-700">Contact</th>
                          <th className="text-left p-6 font-semibold text-gray-700">Amount</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {purchases.items.map((item: any, idx: number) => (
                          <tr key={idx} className="hover:bg-gray-50 transition-colors">
                            <td className="p-6">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-primary to-yellow-500 text-white rounded-xl flex items-center justify-center text-sm font-bold">
                                  {item.categoryId}
                                </div>
                                <div>
                                  <div className="font-semibold text-gray-800">{item.categoryName}</div>
                                  <div className="text-xs text-gray-500">Category #{item.categoryId}</div>
                                </div>
                              </div>
                            </td>
                            <td className="p-6">
                              <div className="flex items-center gap-2">
                                <span className="w-8 h-8 bg-blue-100 text-blue-700 rounded-lg flex items-center justify-center text-sm font-bold">
                                  🎫
                                </span>
                                <span className="font-mono font-semibold text-gray-800">{item.seatNumber}</span>
                              </div>
                            </td>
                            <td className="p-6">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-gray-400 to-gray-500 rounded-xl flex items-center justify-center text-white font-bold text-sm">
                                  {item.userName?.charAt(0)?.toUpperCase() || 'U'}
                                </div>
                                <div>
                                  <div className="font-semibold text-gray-800">{item.userName}</div>
                                  <div className="text-sm text-gray-500">@{item.userId}</div>
                                </div>
                              </div>
                            </td>
                            <td className="p-6">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">📱</span>
                                <span className="text-sm text-gray-600">{item.phoneNumber}</span>
                              </div>
                            </td>
                            <td className="p-6">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">💰</span>
                                <span className="font-bold text-green-600 text-lg">₹{item.ticketPrice}</span>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {tab === 'leaderboard' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-gray-800">Top Buyers Leaderboard</h3>
                <div className="flex items-center gap-2">
                  <span className="text-lg">🏆</span>
                  <span className="text-sm text-gray-600">
                    {leaderboard.length} participants
                  </span>
                </div>
              </div>
              
              {leaderboard.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🏆</div>
                  <h4 className="text-xl font-semibold text-gray-800 mb-2">No purchases yet</h4>
                  <p className="text-gray-600">The leaderboard will populate once users start buying seats.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {leaderboard.map((row: any, i: number) => (
                    <div 
                      key={i} 
                      className={`flex items-center gap-6 p-6 rounded-2xl shadow-lg border transition-all duration-300 transform hover:-translate-y-1 ${
                        i === 0 ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200' :
                        i === 1 ? 'bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200' :
                        i === 2 ? 'bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200' :
                        'bg-white border-gray-200'
                      }`}
                      style={{ animationDelay: `${i * 100}ms` }}
                    >
                      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-white font-bold text-xl ${
                        i === 0 ? 'bg-gradient-to-br from-yellow-500 to-orange-500' :
                        i === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                        i === 2 ? 'bg-gradient-to-br from-orange-500 to-yellow-500' :
                        'bg-gradient-to-br from-primary to-yellow-500'
                      }`}>
                        {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-12 h-12 bg-gradient-to-br from-gray-400 to-gray-500 rounded-xl flex items-center justify-center text-white font-bold">
                            {row.userName?.charAt(0)?.toUpperCase() || 'U'}
                          </div>
                          <div>
                            <div className="font-bold text-gray-800 text-lg">{row.userName}</div>
                            <div className="text-sm text-gray-500">@{row.userId}</div>
                          </div>
                        </div>
                        
                        {i < 3 && (
                          <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
                            i === 0 ? 'bg-yellow-100 text-yellow-700' :
                            i === 1 ? 'bg-gray-100 text-gray-700' :
                            'bg-orange-100 text-orange-700'
                          }`}>
                            <span className="text-lg">
                              {i === 0 ? '👑' : i === 1 ? '🥈' : '🥉'}
                            </span>
                            {i === 0 ? 'Champion' : i === 1 ? 'Runner-up' : 'Third Place'}
                          </div>
                        )}
                      </div>
                      
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-800 mb-1">{row.totalPurchases} seats</div>
                        <div className="text-lg font-semibold text-green-600">₹{row.totalAmount}</div>
                        <div className="text-sm text-gray-500">Total Spent</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {tab === 'winners' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-gray-800">Contest Winners</h3>
                <div className="flex items-center gap-2">
                  <span className="text-lg">🎉</span>
                  <span className="text-sm text-gray-600">
                    {winners.length} winners announced
                  </span>
                </div>
              </div>
              
              {winners.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🎉</div>
                  <h4 className="text-xl font-semibold text-gray-800 mb-2">No winners yet</h4>
                  <p className="text-gray-600">Winners will be announced after the draw is conducted.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Winners Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">🏆</span>
                        <span className="text-sm font-medium text-yellow-700">Total Winners</span>
                      </div>
                      <div className="text-3xl font-bold text-yellow-800">{winners.length}</div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">💰</span>
                        <span className="text-sm font-medium text-green-700">Total Prize Money</span>
                      </div>
                      <div className="text-3xl font-bold text-green-800">
                        ₹{winners.reduce((sum: number, winner: any) => sum + winner.prizeAmount, 0).toLocaleString()}
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">🎯</span>
                        <span className="text-sm font-medium text-purple-700">Prize Levels</span>
                      </div>
                      <div className="text-3xl font-bold text-purple-800">
                        {new Set(winners.map((winner: any) => winner.prizeRank)).size}
                      </div>
                    </div>
                  </div>

                  {/* Winners List */}
                  <div className="space-y-4">
                    {winners.map((winner: any, i: number) => (
                      <div 
                        key={i} 
                        className={`flex items-center gap-6 p-6 rounded-2xl shadow-lg border transition-all duration-300 transform hover:-translate-y-1 ${
                          winner.prizeRank === 1 ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200' :
                          winner.prizeRank === 2 ? 'bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200' :
                          winner.prizeRank === 3 ? 'bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200' :
                          'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
                        }`}
                        style={{ animationDelay: `${i * 100}ms` }}
                      >
                        <div className={`w-20 h-20 rounded-2xl flex items-center justify-center text-white font-bold text-2xl ${
                          winner.prizeRank === 1 ? 'bg-gradient-to-br from-yellow-500 to-orange-500' :
                          winner.prizeRank === 2 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                          winner.prizeRank === 3 ? 'bg-gradient-to-br from-orange-500 to-yellow-500' :
                          'bg-gradient-to-br from-blue-500 to-indigo-500'
                        }`}>
                          {winner.prizeRank === 1 ? '🥇' : 
                           winner.prizeRank === 2 ? '🥈' : 
                           winner.prizeRank === 3 ? '🥉' : 
                           winner.prizeRank}
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 bg-gradient-to-br from-gray-400 to-gray-500 rounded-xl flex items-center justify-center text-white font-bold">
                              {winner.userName?.charAt(0)?.toUpperCase() || 'U'}
                            </div>
                            <div>
                              <div className="font-bold text-gray-800 text-xl">{winner.userName}</div>
                              <div className="text-sm text-gray-500">@{winner.userId}</div>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-6 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">🎫</span>
                              <span>Seat: <span className="font-mono font-semibold text-gray-800">{winner.seatNumber}</span></span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-lg">📋</span>
                              <span>Category: <span className="font-semibold text-gray-800">{winner.categoryName}</span></span>
                            </div>
                          </div>
                          
                          {winner.prizeRank <= 3 && (
                            <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium mt-2 ${
                              winner.prizeRank === 1 ? 'bg-yellow-100 text-yellow-700' :
                              winner.prizeRank === 2 ? 'bg-gray-100 text-gray-700' :
                              'bg-orange-100 text-orange-700'
                            }`}>
                              <span className="text-lg">
                                {winner.prizeRank === 1 ? '👑' : winner.prizeRank === 2 ? '🥈' : '🥉'}
                              </span>
                              {winner.prizeRank === 1 ? 'Grand Prize Winner' : 
                               winner.prizeRank === 2 ? 'Second Place' : 
                               'Third Place'}
                            </div>
                          )}
                        </div>
                        
                        <div className="text-right">
                          <div className="text-3xl font-bold text-green-600 mb-1">₹{winner.prizeAmount.toLocaleString()}</div>
                          <div className="text-sm text-gray-500">Prize Money</div>
                          <div className="text-xs text-gray-400 mt-1">
                            {winner.prizeRank}{winner.prizeRank === 1 ? 'st' : winner.prizeRank === 2 ? 'nd' : winner.prizeRank === 3 ? 'rd' : 'th'} Place
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}



