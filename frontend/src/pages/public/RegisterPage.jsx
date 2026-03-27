import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import toast from 'react-hot-toast'
import { FiShield } from 'react-icons/fi'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', full_name: '', phone: '', password: '', confirm: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm) return toast.error('Les mots de passe ne correspondent pas')
    setLoading(true)
    try {
      await api.post('/auth/register/', { email: form.email, full_name: form.full_name, phone: form.phone, password: form.password })
      toast.success('Compte créé avec succès')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.email?.[0] || 'Erreur inscription')
    } finally {
      setLoading(false)
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <FiShield className="text-primary text-5xl mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-primary">TrustArchive<span className="text-accent">.bi</span></h1>
          <p className="text-gray-500 mt-1">Créer votre compte</p>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { label: 'Nom complet', key: 'full_name', type: 'text' },
              { label: 'Email', key: 'email', type: 'email' },
              { label: 'Téléphone', key: 'phone', type: 'tel' },
              { label: 'Mot de passe', key: 'password', type: 'password' },
              { label: 'Confirmer le mot de passe', key: 'confirm', type: 'password' },
            ].map(({ label, key, type }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input type={type} className="input-field" value={form[key]} onChange={set(key)} required />
              </div>
            ))}
            <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
              {loading ? 'Création...' : 'Créer mon compte'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Déjà un compte ? <Link to="/login" className="text-primary font-medium hover:underline">Se connecter</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
