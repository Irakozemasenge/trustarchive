import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import toast from 'react-hot-toast'
import { FiHome, FiFileText, FiInbox, FiPlusCircle, FiGrid } from 'react-icons/fi'

const links = [
  { to: '/admin', icon: FiHome, label: 'Tableau de bord' },
  { to: '/admin/documents', icon: FiFileText, label: 'Documents' },
  { to: '/admin/documents/add', icon: FiPlusCircle, label: 'Ajouter document' },
  { to: '/admin/requests', icon: FiInbox, label: 'Demandes' },
]

export default function AdminAddDocument() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', category: '', description: '', issued_to: '', issued_to_id: '', issued_date: '', expiry_date: '' })
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [created, setCreated] = useState(null)

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get('/documents/categories/').then(r => r.data)
  })
  // Sans pagination : l'API retourne directement un tableau
  const categories = Array.isArray(categoriesData) ? categoriesData : (categoriesData?.results ?? [])

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.category) return toast.error('Veuillez choisir une categorie')
    setLoading(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => { if (v) fd.append(k, v) })
      if (file) fd.append('document_file', file)
      const { data } = await api.post('/documents/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setCreated(data)
      toast.success('Document enregistre avec succes')
    } catch (err) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : 'Erreur lors de l enregistrement'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Enregistrer un document</h1>
        {created ? (
          <div className="card max-w-lg">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <FiFileText className="text-green-600 text-xl" />
              </div>
              <div>
                <p className="text-green-600 font-bold">Document cree avec succes</p>
                <p className="text-xs text-gray-400">Enregistre sur la blockchain</p>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-xs text-gray-500 mb-1">Numero unique</p>
              <p className="font-mono text-xl font-bold text-primary">{created.unique_number}</p>
            </div>
            {created.qr_code_url && (
              <div className="mb-4 text-center">
                <p className="text-sm text-gray-500 mb-2">QR Code du document</p>
                <img src={created.qr_code_url} alt="QR Code" className="w-40 h-40 border rounded-lg mx-auto" />
              </div>
            )}
            <p className="text-xs text-gray-400 break-all mb-4">Hash blockchain: {created.document_hash}</p>
            <div className="flex gap-3">
              <button onClick={() => setCreated(null)} className="btn-secondary flex-1">Nouveau document</button>
              <button onClick={() => navigate('/admin/documents')} className="btn-primary flex-1">Voir les documents</button>
            </div>
          </div>
        ) : (
          <div className="card max-w-2xl">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Titre du document <span className="text-red-500">*</span></label>
                  <input type="text" className="input-field" value={form.title} onChange={set('title')} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categorie <span className="text-red-500">*</span></label>
                  <select className="input-field" value={form.category} onChange={set('category')} required>
                    <option value="">-- Choisir une categorie --</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Delivre a <span className="text-red-500">*</span></label>
                  <input type="text" className="input-field" value={form.issued_to} onChange={set('issued_to')} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">CNI / Passeport</label>
                  <input type="text" className="input-field" value={form.issued_to_id} onChange={set('issued_to_id')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date d emission <span className="text-red-500">*</span></label>
                  <input type="date" className="input-field" value={form.issued_date} onChange={set('issued_date')} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date expiration</label>
                  <input type="date" className="input-field" value={form.expiry_date} onChange={set('expiry_date')} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea className="input-field" rows={3} value={form.description} onChange={set('description')} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fichier document (PDF/Image)</label>
                  <input type="file" className="input-field" accept=".pdf,.jpg,.jpeg,.png" onChange={e => setFile(e.target.files[0])} />
                </div>
              </div>
              <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
                {loading ? 'Enregistrement en cours...' : 'Enregistrer et generer QR Code'}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  )
}

