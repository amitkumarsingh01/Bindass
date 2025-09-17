import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { AdminDashboard } from '../lib/api'

export default function Dashboard() {
  const [data, setData] = useState<AdminDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/admin/dashboard')
        setData(res.data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading dashboard...</p>
        </div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading Dashboard</h3>
        <p className="text-red-600">{error}</p>
      </div>
    )
  }
  
  if (!data) return null

  const cards = [
    { 
      label: 'Total Users', 
      value: data.users.total, 
      icon: '👥', 
      color: 'from-blue-500 to-blue-600',
      bgColor: 'from-blue-50 to-blue-100',
      textColor: 'text-blue-700',
      changeType: 'positive'
    },
    { 
      label: 'Active Users', 
      value: data.users.active, 
      icon: '✅', 
      color: 'from-green-500 to-green-600',
      bgColor: 'from-green-50 to-green-100',
      textColor: 'text-green-700',
      changeType: 'positive'
    },
    { 
      label: 'Total Contests', 
      value: data.contests.total, 
      icon: '🎯', 
      color: 'from-purple-500 to-purple-600',
      bgColor: 'from-purple-50 to-purple-100',
      textColor: 'text-purple-700',
      changeType: 'positive'
    },
    { 
      label: 'Active Contests', 
      value: data.contests.active, 
      icon: '🔥', 
      color: 'from-orange-500 to-orange-600',
      bgColor: 'from-orange-50 to-orange-100',
      textColor: 'text-orange-700',
      changeType: 'neutral'
    },
    { 
      label: 'Total Transactions', 
      value: data.transactions.total, 
      icon: '💳', 
      color: 'from-indigo-500 to-indigo-600',
      bgColor: 'from-indigo-50 to-indigo-100',
      textColor: 'text-indigo-700',
      changeType: 'positive'
    },
    { 
      label: 'Pending Withdrawals', 
      value: data.withdrawals.pending, 
      icon: '⏳', 
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'from-yellow-50 to-yellow-100',
      textColor: 'text-yellow-700',
      changeType: 'warning'
    },
    { 
      label: 'Prize Distributed', 
      value: `₹${data.prizeMoney.totalDistributed.toLocaleString()}`, 
      icon: '💰', 
      color: 'from-emerald-500 to-emerald-600',
      bgColor: 'from-emerald-50 to-emerald-100',
      textColor: 'text-emerald-700',
      changeType: 'positive'
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-primary to-yellow-500 rounded-3xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Dashboard Overview</h1>
            <p className="text-xl opacity-90">Real-time insights into your lottery system</p>
          </div>
          <div className="hidden lg:block">
            <div className="w-32 h-32 bg-white/20 rounded-full flex items-center justify-center">
              <span className="text-6xl">📊</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <div 
            key={card.label} 
            className={`bg-gradient-to-br ${card.bgColor} rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-white/50`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 bg-gradient-to-br ${card.color} rounded-xl flex items-center justify-center shadow-lg`}>
                <span className="text-2xl">{card.icon}</span>
              </div>
              <div className={`text-xs px-2 py-1 rounded-full ${
                card.changeType === 'positive' ? 'bg-green-100 text-green-700' :
                card.changeType === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {card.change}
              </div>
            </div>
            <div>
              <p className={`text-sm font-medium ${card.textColor} mb-1`}>{card.label}</p>
              <p className={`text-3xl font-bold ${card.textColor}`}>{card.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">➕</span>
            <span className="font-semibold">Create Contest</span>
          </button>
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">👥</span>
            <span className="font-semibold">View Users</span>
          </button>
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">💰</span>
            <span className="font-semibold">Withdrawals</span>
          </button>
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">🖼️</span>
            <span className="font-semibold">Manage Sliders</span>
          </button>
        </div>
      </div>
    </div>
  )
}


