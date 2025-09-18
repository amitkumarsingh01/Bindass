import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function HowToPlay() {
  const [english, setEnglish] = useState('')
  const [hindi, setHindi] = useState('')
  const [kannada, setKannada] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [activeTab, setActiveTab] = useState<'english' | 'hindi' | 'kannada'>('english')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/admin/how-to-play')
      setEnglish(res.data.english || '')
      setHindi(res.data.hindi || '')
      setKannada(res.data.kannada || '')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load how to play content')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      await api.put('/admin/how-to-play', { english, hindi, kannada })
      setSuccess('How to play content saved successfully')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  const getCurrentContent = () => {
    switch (activeTab) {
      case 'english': return english
      case 'hindi': return hindi
      case 'kannada': return kannada
      default: return ''
    }
  }

  const setCurrentContent = (value: string) => {
    switch (activeTab) {
      case 'english': setEnglish(value); break
      case 'hindi': setHindi(value); break
      case 'kannada': setKannada(value); break
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading how to play content...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
          How to Play Content
        </h1>
        <p className="text-gray-600 mt-1">Manage multilingual how to play instructions for users</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-red-700">{error}</div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4 text-green-700">{success}</div>
      )}

      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Language Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex">
            {[
              { key: 'english', label: 'English', flag: '🇺🇸' },
              { key: 'hindi', label: 'हिंदी', flag: '🇮🇳' },
              { key: 'kannada', label: 'ಕನ್ನಡ', flag: '🇮🇳' }
            ].map((lang) => (
              <button
                key={lang.key}
                onClick={() => setActiveTab(lang.key as any)}
                className={`flex-1 px-6 py-4 text-center font-medium transition-all duration-200 ${
                  activeTab === lang.key
                    ? 'bg-gradient-to-r from-primary to-yellow-500 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <span className="text-xl mr-2">{lang.flag}</span>
                {lang.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Editor */}
        <div className="p-8">
          <form onSubmit={onSubmit} className="space-y-6">
            <div>
              <label className="block text-lg font-semibold text-gray-800 mb-3">
                Content ({activeTab === 'english' ? 'English' : activeTab === 'hindi' ? 'Hindi' : 'Kannada'})
              </label>
              <div className="relative">
                <span className="absolute left-4 top-4 text-gray-400 text-xl">📝</span>
                <textarea
                  className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg min-h-[400px] font-mono text-sm"
                  value={getCurrentContent()}
                  onChange={(e) => setCurrentContent(e.target.value)}
                  placeholder={`Enter how to play content in ${activeTab === 'english' ? 'English' : activeTab === 'hindi' ? 'Hindi' : 'Kannada'}...`}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                <span>💡</span>
                <span>Use line breaks to format the content. The text will be displayed as-is to users.</span>
              </p>
            </div>

            <div className="flex justify-between items-center pt-4">
              <div className="text-sm text-gray-500">
                Characters: {getCurrentContent().length}
              </div>
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-4 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium text-lg disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save All Content'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
