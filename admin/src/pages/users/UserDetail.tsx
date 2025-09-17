import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../../lib/api'

export default function UserDetail() {
  const { id } = useParams()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/users/${id}`)
        setData(res.data)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load user')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading user details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading User</h3>
        <p className="text-red-600">{error}</p>
        <Link to="/users" className="mt-4 inline-block px-4 py-2 bg-primary text-white rounded-lg hover:shadow-lg transition-all">
          Back to Users
        </Link>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link 
          to="/users" 
          className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition-all duration-200"
        >
          <span className="text-xl">←</span>
        </Link>
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
            User Profile
          </h1>
          <p className="text-gray-600">Detailed information about {data.userName}</p>
        </div>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-primary to-yellow-500 p-8 text-white">
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 bg-white/20 rounded-2xl flex items-center justify-center text-white font-bold text-4xl">
              {data.userName?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-2">{data.userName}</h2>
              <p className="text-xl opacity-90">@{data.userId}</p>
              <div className="flex items-center gap-4 mt-4">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  data.isActive !== false 
                    ? 'bg-green-500/20 text-green-100' 
                    : 'bg-red-500/20 text-red-100'
                }`}>
                  {data.isActive !== false ? 'Active User' : 'Inactive User'}
                </div>
                <div className="text-sm opacity-75">
                  Joined {formatDate(data.createdAt)}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Basic Information */}
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <span className="text-2xl">👤</span>
                Basic Information
              </h3>
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                  <span className="text-2xl">📧</span>
                  <div>
                    <p className="text-sm text-gray-500">Email Address</p>
                    <p className="font-semibold text-gray-800">{data.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                  <span className="text-2xl">📱</span>
                  <div>
                    <p className="text-sm text-gray-500">Phone Number</p>
                    <p className="font-semibold text-gray-800">{data.phoneNumber}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                  <span className="text-2xl">📍</span>
                  <div>
                    <p className="text-sm text-gray-500">Location</p>
                    <p className="font-semibold text-gray-800">
                      {[data.city, data.state].filter(Boolean).join(', ') || 'Not specified'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Wallet Information */}
            <div>
              <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <span className="text-2xl">💰</span>
                Wallet Information
              </h3>
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                  <span className="text-2xl">💳</span>
                  <div>
                    <p className="text-sm text-gray-500">Current Balance</p>
                    <p className="text-2xl font-bold text-green-700">₹{data.walletBalance?.toLocaleString() || '0'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                  <span className="text-2xl">📊</span>
                  <div>
                    <p className="text-sm text-gray-500">Account Status</p>
                    <p className="font-semibold text-gray-800">
                      {data.isActive !== false ? 'Active' : 'Suspended'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                  <span className="text-2xl">🆔</span>
                  <div>
                    <p className="text-sm text-gray-500">User ID</p>
                    <p className="font-semibold text-gray-800 font-mono">{data.userId}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bank Details */}
      {data.bankDetails && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span className="text-2xl">🏦</span>
            Bank Details
          </h3>
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Account Holder Name</p>
                  <p className="font-semibold text-gray-800">{data.bankDetails.accountHolderName || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Account Number</p>
                  <p className="font-semibold text-gray-800 font-mono">{data.bankDetails.accountNumber || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">IFSC Code</p>
                  <p className="font-semibold text-gray-800 font-mono">{data.bankDetails.ifscCode || 'N/A'}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Bank Name</p>
                  <p className="font-semibold text-gray-800">{data.bankDetails.bankName || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Branch</p>
                  <p className="font-semibold text-gray-800">{data.bankDetails.branch || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Account Type</p>
                  <p className="font-semibold text-gray-800">{data.bankDetails.accountType || 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">💳</span>
            <span className="font-semibold">View Transactions</span>
          </button>
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">🎯</span>
            <span className="font-semibold">View Purchases</span>
          </button>
          <button className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 group">
            <span className="text-2xl group-hover:scale-110 transition-transform">✏️</span>
            <span className="font-semibold">Edit Profile</span>
          </button>
        </div>
      </div>
    </div>
  )
}


