import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Contact() {
  const [contactNo, setContactNo] = useState('')
  const [email, setEmail] = useState('')
  const [website, setWebsite] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // How to Play content
  const [howToPlay, setHowToPlay] = useState({
    english: '',
    hindi: '',
    kannada: ''
  })
  const [howToPlayLoading, setHowToPlayLoading] = useState(true)
  const [activeLanguage, setActiveLanguage] = useState<'english' | 'hindi' | 'kannada'>('english')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/admin/contact')
      setContactNo(res.data.contactNo || '')
      setEmail(res.data.email || '')
      setWebsite(res.data.website || '')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load contact info')
    } finally {
      setLoading(false)
    }
  }

  const loadHowToPlay = async () => {
    setHowToPlayLoading(true)
    try {
      const res = await api.get('/admin/how-to-play')
      setHowToPlay({
        english: res.data.english || '',
        hindi: res.data.hindi || '',
        kannada: res.data.kannada || ''
      })
    } catch (e: any) {
      console.error('Failed to load how to play content:', e)
    } finally {
      setHowToPlayLoading(false)
    }
  }

  useEffect(() => { 
    load()
    loadHowToPlay()
  }, [])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      await api.put('/admin/contact', { contactNo, email, website })
      setSuccess('Contact information saved successfully')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading contact details...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          Contact Information
        </h1>
        <p className="text-gray-600 mt-1">Manage support contact details and how to play content displayed to users</p>
      </div>

      {/* How to Play Preview Section */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-primary to-yellow-500 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <span className="text-2xl text-white">📖</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">How to Play Content</h2>
                <p className="text-white/80 text-sm">Preview of game instructions shown to users</p>
              </div>
            </div>
            <a 
              href="/how-to-play"
              className="px-4 py-2 bg-white/20 text-white rounded-xl hover:bg-white/30 transition-all duration-200 font-medium"
            >
              Edit Content
            </a>
          </div>
        </div>
        
        <div className="p-6">
          {/* Language Tabs */}
          <div className="flex mb-6 border-b border-gray-200">
            {[
              { key: 'english', label: 'English', flag: '🇺🇸' },
              { key: 'hindi', label: 'हिंदी', flag: '🇮🇳' },
              { key: 'kannada', label: 'ಕನ್ನಡ', flag: '🇮🇳' }
            ].map((lang) => (
              <button
                key={lang.key}
                onClick={() => setActiveLanguage(lang.key as any)}
                className={`px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2 ${
                  activeLanguage === lang.key
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <span className="text-lg mr-2">{lang.flag}</span>
                {lang.label}
              </button>
            ))}
          </div>

          {/* Content Preview */}
          {howToPlayLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-xl p-6 max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-gray-700 text-sm leading-relaxed font-sans">
                {howToPlay[activeLanguage] || 'No content available for this language...'}
              </pre>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700">{error}</div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4 text-green-700">{success}</div>
      )}

      <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
        <form className="space-y-6" onSubmit={onSubmit}>
          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">Contact No</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">📞</span>
              <input
                className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg"
                value={contactNo}
                onChange={(e) => setContactNo(e.target.value)}
                placeholder="e.g., +91 90000 00000"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">Email Id</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">✉️</span>
              <input
                type="email"
                className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="support@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-lg font-semibold text-gray-800 mb-3">Website Link</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">🔗</span>
              <input
                type="url"
                className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                placeholder="https://yourdomain.com"
                required
              />
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-4 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium text-lg disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Save Contact Details'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


