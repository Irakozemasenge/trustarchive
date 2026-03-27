import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import { FiShield } from 'react-icons/fi'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const user = await login(form.email, form.password)
      toast.success('Connexion réussie')
      if (user.role === 'superadmin') navigate('/superadmin')
      else if (user.role === 'admin') navigate('/admin')
      else navigate('/')
    } catch {
      toast.error('Email ou mot de passe incorrect')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <FiShield className="text-primary text-5xl mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-primary">TrustArchive<span className="text-accent">.bi</span></h1>
          <p className="text-gray-500 mt-1">Connectez-vous à votre compte</p>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                className="input-field"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
              <input
                type="password"
                className="input-field"
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                required
              />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Pas de compte ?{' '}
            <Link to="/register" className="text-primary font-medium hover:underline">S'inscrire</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
