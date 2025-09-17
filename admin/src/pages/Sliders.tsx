import { useEffect, useState } from 'react'
import { api } from '../lib/api'

type Slider = { 
  id: string
  title: string
  imageUrl: string
  linkUrl?: string
  description?: string
  order: number
  isActive: boolean
  createdAt?: string
  updatedAt?: string
}

export default function Sliders() {
  const [items, setItems] = useState<Slider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingSlider, setEditingSlider] = useState<Slider | null>(null)
  const [saving, setSaving] = useState(false)

  // Form state
  const [title, setTitle] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [linkUrl, setLinkUrl] = useState('')
  const [description, setDescription] = useState('')
  const [order, setOrder] = useState<number>(1)
  const [isActive, setIsActive] = useState(true)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/admin/home-sliders')
      setItems(res.data.sliders)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load sliders')
    } finally {
      setLoading(false)
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

  useEffect(() => { load() }, [])

  useEffect(() => {
    // Prefill form when opening modal
    if (editingSlider) {
      setTitle(editingSlider.title || '')
      setImageUrl(editingSlider.imageUrl || '')
      setImageFile(null)
      setLinkUrl(editingSlider.linkUrl || '')
      setDescription(editingSlider.description || '')
      setOrder(editingSlider.order || 1)
      setIsActive(editingSlider.isActive ?? true)
    } else if (showCreateForm) {
      setTitle('')
      setImageUrl('')
      setImageFile(null)
      setLinkUrl('')
      setDescription('')
      setOrder(Math.max(1, items.length + 1))
      setIsActive(true)
    }
  }, [editingSlider, showCreateForm])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      if (editingSlider) {
        // Update (edit) path - backend update accepts only fields (no file upload here)
        await api.put(`/admin/home-sliders/${editingSlider.id}`, {
          title,
          image_url: imageUrl || undefined,
          link_url: linkUrl || undefined,
          description: description || undefined,
          order,
          is_active: isActive,
        })
      } else {
        // Create path - supports file upload via multipart/form-data
        const form = new FormData()
        form.append('title', title)
        if (imageFile) {
          form.append('image', imageFile)
        } else if (imageUrl) {
          form.append('image_url', imageUrl)
        }
        if (linkUrl) form.append('link_url', linkUrl)
        if (description) form.append('description', description)
        form.append('order', String(order))
        await api.post('/admin/home-sliders', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      }
      await load()
      setShowCreateForm(false)
      setEditingSlider(null)
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to save slider')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading sliders...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-red-800 mb-2">Error Loading Sliders</h3>
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
            Home Sliders
          </h1>
          <p className="text-gray-600 mt-1">Manage banner images and promotional content</p>
        </div>
        
        <button 
          onClick={() => setShowCreateForm(true)}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium"
        >
          <span className="text-xl">➕</span>
          Add New Slider
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-blue-600">🖼️</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Sliders</p>
              <p className="text-2xl font-bold text-gray-800">{items.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-green-600">✅</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Active Sliders</p>
              <p className="text-2xl font-bold text-gray-800">{items.filter(s => s.isActive).length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl text-purple-600">📊</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Inactive Sliders</p>
              <p className="text-2xl font-bold text-gray-800">{items.filter(s => !s.isActive).length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sliders Grid */}
      {items.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🖼️</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No sliders yet</h3>
          <p className="text-gray-600 mb-4">Create your first home slider to get started</p>
          <button 
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium"
          >
            <span className="text-xl">➕</span>
            Create First Slider
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((slider, index) => (
            <div
              key={slider.id}
              className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Image Preview */}
              <div className="relative h-48 bg-gray-100">
                {slider.imageUrl ? (
                  <img 
                    src={slider.imageUrl.startsWith('http') ? slider.imageUrl : `https://server.bindassgrand.com${slider.imageUrl}`}
                    alt={slider.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.style.display = 'none'
                      target.nextElementSibling?.classList.remove('hidden')
                    }}
                  />
                ) : null}
                <div className={`absolute inset-0 flex items-center justify-center ${slider.imageUrl ? 'hidden' : ''}`}>
                  <span className="text-6xl text-gray-400">🖼️</span>
                </div>
                
                {/* Status Badge */}
                <div className="absolute top-3 right-3">
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    slider.isActive 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {slider.isActive ? 'Active' : 'Inactive'}
                  </div>
                </div>
                
                {/* Order Badge */}
                <div className="absolute top-3 left-3">
                  <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {slider.order}
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-2">{slider.title}</h3>
                
                {slider.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{slider.description}</p>
                )}
                
                {slider.linkUrl && (
                  <a 
                    href={slider.linkUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-primary hover:text-yellow-600 transition-colors"
                  >
                    <span>🔗</span>
                    <span className="truncate max-w-32">{slider.linkUrl}</span>
                  </a>
                )}
                
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Created: {formatDate(slider.createdAt)}</span>
                    <span>Order: {slider.order}</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="px-6 pb-6">
                <div className="flex gap-2">
                  <button 
                    onClick={() => setEditingSlider(slider)}
                    className="flex-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => {
                      // Toggle active status
                      const updatedSliders = items.map(s => 
                        s.id === slider.id ? { ...s, isActive: !s.isActive } : s
                      )
                      setItems(updatedSliders)
                    }}
                    className={`flex-1 px-3 py-2 rounded-lg transition-colors text-sm font-medium ${
                      slider.isActive 
                        ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' 
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {slider.isActive ? 'Deactivate' : 'Activate'}
                  </button>
                  <button 
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this slider?')) {
                        setItems(items.filter(s => s.id !== slider.id))
                      }
                    }}
                    className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Form Modal */}
      {(showCreateForm || editingSlider) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="bg-gradient-to-r from-primary to-yellow-500 p-6 rounded-t-3xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                    <span className="text-2xl text-white">🖼️</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">
                      {editingSlider ? 'Edit Slider' : 'Create New Slider'}
                    </h2>
                    <p className="text-white/80 text-sm">
                      {editingSlider ? 'Update slider information' : 'Add a new home slider'}
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => {
                    setShowCreateForm(false)
                    setEditingSlider(null)
                  }}
                  className="p-3 text-white/80 hover:text-white hover:bg-white/20 rounded-xl transition-all duration-200"
                >
                  <span className="text-2xl">✕</span>
                </button>
              </div>
            </div>
            
            <div className="p-8">
              <form className="space-y-6" onSubmit={handleSubmit}>
                <div>
                  <label className="block text-lg font-semibold text-gray-800 mb-3">
                    Slider Title
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">📝</span>
                    <input 
                      type="text" 
                      className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                      placeholder="Enter an attractive slider title"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      required
                    />
                  </div>
                </div>
                
                {/* Upload Image (create supports file upload; edit uses URL update) */}
                <div>
                  <label className="block text-lg font-semibold text-gray-800 mb-3">
                    Upload Image {editingSlider ? <span className="text-sm text-gray-500">(upload supported only on create)</span> : null}
                  </label>
                  <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                    <label className="inline-flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
                      <input 
                        type="file" 
                        accept="image/*"
                        className="hidden"
                        disabled={!!editingSlider}
                        onChange={(e) => {
                          const file = e.target.files?.[0] || null
                          setImageFile(file || null)
                        }}
                      />
                      <span className="text-xl">📤</span>
                      <span className="text-gray-800 font-medium">Choose Image</span>
                    </label>
                    {imageFile && (
                      <span className="text-sm text-gray-600">{imageFile.name}</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                    <span>💡</span>
                    <span>Upload a high-quality image (1920x1080 recommended). Or provide a URL below.</span>
                  </p>
                </div>

                <div>
                  <label className="block text-lg font-semibold text-gray-800 mb-3">
                    Image URL
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">🖼️</span>
                    <input 
                      type="url" 
                      className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                      placeholder="https://example.com/image.jpg"
                      value={imageUrl}
                      onChange={(e) => setImageUrl(e.target.value)}
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                    <span>💡</span>
                    <span>Use high-quality images (1920x1080 recommended)</span>
                  </p>
                </div>
                
                <div>
                  <label className="block text-lg font-semibold text-gray-800 mb-3">
                    Link URL (Optional)
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">🔗</span>
                    <input 
                      type="url" 
                      className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                      placeholder="https://example.com"
                      value={linkUrl}
                      onChange={(e) => setLinkUrl(e.target.value)}
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                    <span>💡</span>
                    <span>Where users will be redirected when they click the slider</span>
                  </p>
                </div>
                
                <div>
                  <label className="block text-lg font-semibold text-gray-800 mb-3">
                    Description (Optional)
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-4 text-gray-400 text-xl">📄</span>
                    <textarea 
                      className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                      rows={4}
                      placeholder="Enter a brief description for the slider"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-lg font-semibold text-gray-800 mb-3">
                      Display Order
                    </label>
                    <div className="relative">
                      <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">🔢</span>
                      <input 
                        type="number" 
                        className="w-full border border-gray-200 rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-lg" 
                        placeholder="1"
                        value={order}
                        onChange={(e) => setOrder(parseInt(e.target.value || '1', 10))}
                        min="1"
                      />
                    </div>
                    <p className="text-sm text-gray-500 mt-2">Lower numbers appear first</p>
                  </div>
                  
                  <div className="flex items-center justify-center">
                    <label className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors">
                      <input 
                        type="checkbox" 
                        className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary"
                        checked={isActive}
                        onChange={(e) => setIsActive(e.target.checked)}
                      />
                      <div>
                        <span className="text-lg font-medium text-gray-800">Active Status</span>
                        <p className="text-sm text-gray-500">Show this slider on the home page</p>
                      </div>
                    </label>
                  </div>
                </div>
                
                <div className="flex gap-4 pt-6">
                  <button 
                    type="button"
                    onClick={() => {
                      setShowCreateForm(false)
                      setEditingSlider(null)
                    }}
                    className="flex-1 px-6 py-4 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium text-lg"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    disabled={saving}
                    className="flex-1 px-6 py-4 bg-gradient-to-r from-primary to-yellow-500 text-white rounded-xl hover:shadow-lg transition-all duration-200 font-medium text-lg disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {saving ? (editingSlider ? 'Updating...' : 'Creating...') : (editingSlider ? 'Update Slider' : 'Create Slider')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


