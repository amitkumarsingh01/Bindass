import { useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { api } from '../../lib/api'

export default function Draw() {
  const { id } = useParams()
  const nav = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)
  const [showConfirm, setShowConfirm] = useState(false)

  const announce = async () => {
    if (!id) return
    setError('')
    setLoading(true)
    try {
      const res = await api.post(`/admin/contests/${id}/announce-prize`)
      setResult(res.data)
      setShowConfirm(false)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to announce prize winners')
    } finally {
      setLoading(false)
    }
  }

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
            Announce Prize Winners
          </h1>
          <p className="text-gray-600 mt-1">Announce winners and credit prize money for contest #{id}</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Draw Control */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <div className="text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-primary to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">🏆</span>
            </div>
            
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Ready to Announce Prizes?</h2>
            <p className="text-gray-600 mb-8">
              This will announce the prize winners and automatically credit the winning amounts to their wallets based on the prize structure. 
              This action cannot be undone.
            </p>

            {!result ? (
              <div className="space-y-4">
                {!showConfirm ? (
                  <button
                    onClick={() => setShowConfirm(true)}
                    className="w-full px-8 py-4 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-bold text-lg"
                  >
                    <div className="flex items-center justify-center gap-3">
                      <span className="text-2xl">🏆</span>
                      Announce Prize Winners
                    </div>
                  </button>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">⚠️</span>
                        <span className="font-semibold text-yellow-800">Confirm Prize Announcement</span>
                      </div>
                      <p className="text-yellow-700 text-sm">
                        Are you sure you want to announce the prize winners? This will credit prize money to winners' wallets and cannot be undone.
                      </p>
                    </div>
                    
                    <div className="flex gap-4">
                      <button
                        onClick={() => setShowConfirm(false)}
                        className="flex-1 px-6 py-3 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={announce}
                        disabled={loading}
                        className="flex-1 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? (
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Announcing Prizes...
                          </div>
                        ) : (
                          <div className="flex items-center justify-center gap-2">
                            <span className="text-xl">🏆</span>
                            Confirm Announcement
                          </div>
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-3xl">🎉</span>
                    <span className="text-xl font-bold text-green-800">Prizes Announced!</span>
                  </div>
                  <p className="text-green-700">
                    Prize winners have been announced and winning amounts have been automatically credited to their wallets.
                  </p>
                </div>
                
                <button
                  onClick={() => nav('/contests')}
                  className="w-full px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium"
                >
                  Back to Contests
                </button>
              </div>
            )}

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-center gap-2">
                  <span className="text-red-500 text-xl">⚠️</span>
                  <p className="text-red-700 font-medium">{error}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Draw Information */}
        <div className="space-y-6">
          {/* Contest Info */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">📋</span>
              Contest Information
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Contest ID:</span>
                <span className="font-semibold text-gray-800">#{id}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Status:</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                  {result ? 'Prizes Announced' : 'Ready for Announcement'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Draw Time:</span>
                <span className="font-semibold text-gray-800">
                  {result ? formatDate(result.announceTime) : 'Not announced'}
                </span>
              </div>
            </div>
          </div>

          {/* Draw Process */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">⚙️</span>
              Prize Announcement Process
            </h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm font-bold">1</span>
                </div>
                <span className="text-gray-700">Select winners based on prize structure</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm font-bold">2</span>
                </div>
                <span className="text-gray-700">Automatically credit prize money to winners' wallets</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm font-bold">3</span>
                </div>
                <span className="text-gray-700">Update contest status and notify winners</span>
              </div>
            </div>
          </div>

          {/* Important Notes */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">📝</span>
              Important Notes
            </h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start gap-2">
                <span className="text-red-500 mt-1">•</span>
                <span>This action cannot be undone once completed</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-red-500 mt-1">•</span>
                <span>Prize money will be automatically credited to winners' wallets</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-red-500 mt-1">•</span>
                <span>Contest will be marked as completed after announcement</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-red-500 mt-1">•</span>
                <span>Winners will be notified and can withdraw their winnings</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Draw Results */}
      {result && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span className="text-3xl">🏆</span>
            Prize Announcement Results
          </h3>
          
          <div className="bg-gray-50 rounded-xl p-6">
            <pre className="text-sm text-gray-700 overflow-auto whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}


