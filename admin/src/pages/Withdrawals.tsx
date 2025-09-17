import { useEffect, useState } from 'react'
import { api } from '../lib/api'

type Withdrawal = {
  id: string
  amount: number
  status: string
  user: { userId: string; userName: string; phoneNumber: string }
  bankDetails?: { bankName?: string; accountNumber?: string }
  createdAt?: string
  updatedAt?: string
}

export default function Withdrawals() {
  const [items, setItems] = useState<Withdrawal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<'all' | 'pending' | 'processing' | 'completed' | 'rejected'>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [processingId, setProcessingId] = useState<string>('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/admin/withdrawals')
      setItems(res.data.withdrawals)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load withdrawals')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const updateStatus = async (id: string, status: string) => {
    setProcessingId(id)
    try {
      await api.put(`/admin/withdrawals/${id}/status`, null, { params: { status } })
      await load()
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to update status')
    } finally {
      setProcessingId('')
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'processing': return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'completed': return 'bg-green-100 text-green-700 border-green-200'
      case 'rejected': return 'bg-red-100 text-red-700 border-red-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return '⏳'
      case 'processing': return '🔄'
      case 'completed': return '✅'
      case 'rejected': return '❌'
      default: return '❓'
    }
  }

  const filteredItems = items.filter(item => {
    const matchesFilter = filter === 'all' || item.status.toLowerCase() === filter
    const matchesSearch = searchTerm === '' || 
      item.user.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.user.userId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.user.phoneNumber.includes(searchTerm)
    return matchesFilter && matchesSearch
  })

  const totalAmount = items.reduce((sum, item) => sum + item.amount, 0)
  const pendingAmount = items.filter(item => item.status.toLowerCase() === 'pending').reduce((sum, item) => sum + item.amount, 0)
  const completedAmount = items.filter(item => item.status.toLowerCase() === 'completed').reduce((sum, item) => sum + item.amount, 0)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading withdrawals...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading Withdrawals</h3>
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            Withdrawal Management
          </h1>
          <p className="text-gray-600 mt-1">Process and manage user withdrawal requests</p>
        </div>
        
        <div className="flex items-center gap-4">
          <button
            onClick={load}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl hover:shadow-md transition-all duration-200"
          >
            <span className="text-lg">🔄</span>
            <span className="font-medium">Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-white">💰</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Requests</p>
              <p className="text-2xl font-bold text-gray-800">{items.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-white">⏳</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Pending Amount</p>
              <p className="text-2xl font-bold text-gray-800">₹{pendingAmount.toLocaleString()}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-white">✅</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Completed Amount</p>
              <p className="text-2xl font-bold text-gray-800">₹{completedAmount.toLocaleString()}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-white">📊</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Amount</p>
              <p className="text-2xl font-bold text-gray-800">₹{totalAmount.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <input
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                placeholder="Search by user name, ID, or phone..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
              <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                <span className="text-lg">🔍</span>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            {['all', 'pending', 'processing', 'completed', 'rejected'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status as any)}
                className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                  filter === status
                    ? 'bg-primary text-white shadow-lg'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Withdrawals List */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">💰</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No withdrawals found</h3>
          <p className="text-gray-600">No withdrawal requests match your current filters</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredItems.map((withdrawal, index) => (
            <div
              key={withdrawal.id}
              className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* User Info */}
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary to-yellow-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                    {withdrawal.user.userName?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-800 text-lg">{withdrawal.user.userName}</h3>
                    <p className="text-sm text-gray-500">@{withdrawal.user.userId}</p>
                    <p className="text-sm text-gray-500">{withdrawal.user.phoneNumber}</p>
                  </div>
                </div>

                {/* Amount and Status */}
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-800">₹{withdrawal.amount.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Requested Amount</p>
                  </div>
                  
                  <div className={`px-3 py-2 rounded-xl border font-medium flex items-center gap-2 ${getStatusColor(withdrawal.status)}`}>
                    <span className="text-lg">{getStatusIcon(withdrawal.status)}</span>
                    <span>{withdrawal.status.charAt(0).toUpperCase() + withdrawal.status.slice(1)}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {withdrawal.status.toLowerCase() === 'pending' && (
                    <>
                      <button
                        onClick={() => updateStatus(withdrawal.id, 'processing')}
                        disabled={processingId === withdrawal.id}
                        className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {processingId === withdrawal.id ? (
                          <div className="flex items-center gap-2">
                            <div className="w-4 h-4 border-2 border-blue-700 border-t-transparent rounded-full animate-spin"></div>
                            Processing...
                          </div>
                        ) : (
                          'Process'
                        )}
                      </button>
                      <button
                        onClick={() => updateStatus(withdrawal.id, 'completed')}
                        disabled={processingId === withdrawal.id}
                        className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Complete
                      </button>
                      <button
                        onClick={() => updateStatus(withdrawal.id, 'rejected')}
                        disabled={processingId === withdrawal.id}
                        className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Reject
                      </button>
                    </>
                  )}
                  
                  {withdrawal.status.toLowerCase() === 'processing' && (
                    <>
                      <button
                        onClick={() => updateStatus(withdrawal.id, 'completed')}
                        disabled={processingId === withdrawal.id}
                        className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Complete
                      </button>
                      <button
                        onClick={() => updateStatus(withdrawal.id, 'rejected')}
                        disabled={processingId === withdrawal.id}
                        className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Reject
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Bank Details */}
              {withdrawal.bankDetails && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">🏦</span>
                    <span className="font-medium text-gray-700">Bank Details</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Bank:</span>
                      <span className="ml-2 font-medium text-gray-800">{withdrawal.bankDetails.bankName || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Account:</span>
                      <span className="ml-2 font-medium text-gray-800 font-mono">{withdrawal.bankDetails.accountNumber || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Timestamps */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Requested: {formatDate(withdrawal.createdAt)}</span>
                  <span>Updated: {formatDate(withdrawal.updatedAt)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


