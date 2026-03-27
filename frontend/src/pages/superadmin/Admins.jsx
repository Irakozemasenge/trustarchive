import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import toast from 'react-hot-toast'
import { FiHome, FiUsers, FiFileText, FiLink, FiTag, FiActivity, FiPlusCircle, FiToggleLeft, FiToggleRight } from 'react-icons/fi'

const links = [
  { to: "/superadmin", icon: FiHome, label: "Tableau de bord" },
  { to: "/superadmin/admins", icon: FiUsers, label: "Admins partenaires" },
  { to: "/superadmin/documents", icon: FiFileText, label: "Tous les documents" },
  { to: "/superadmin/categories", icon: FiTag, label: "Categories" },
  { to: "/superadmin/blockchain", icon: FiLink, label: "Blockchain" },
  { to: "/superadmin/audit", icon: FiActivity, label: "Journal d audit" },
]

const emptyForm = { email: '', full_name: '', phone: '', password: '', partner_type: 'universite', organization_name: '' }

export default function SuperAdmins() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const { data: admins, isLoading } = useQuery({ queryKey: ['admins'], queryFn: () => api.get('/auth/admins/').then(r => r.data) })
  const adminList = admins?.results ?? admins ?? []

  const createMutation = useMutation({
    mutationFn: (data) => {
      // Envoyer en JSON simple sans le logo
      const { organization_logo, ...payload } = data
      return api.post('/auth/admins/create/', payload)
    },
    onSuccess: () => { toast.success('Admin cree avec succes'); qc.invalidateQueries(['admins']); setShowForm(false); setForm(emptyForm) },
    onError: (err) => {
      const msg = err.response?.data
        ? Object.entries(err.response.data).map(([k,v]) => `${k}: ${v}`).join(' | ')
        : 'Erreur lors de la creation'
      toast.error(msg)
    }
  })

  const toggleMutation = useMutation({
    mutationFn: (id) => api.patch(`/auth/admins/${id}/toggle/`),
    onSuccess: () => { toast.success('Statut mis a jour'); qc.invalidateQueries(['admins']) }
  })

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Admins Partenaires</h1>
          <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
            <FiPlusCircle /> Creer un admin
          </button>
        </div>

        <div className="card overflow-x-auto">
          {isLoading ? <p className="text-gray-400">Chargement...</p> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4">Nom</th>
                  <th className="pb-3 pr-4">Email</th>
                  <th className="pb-3 pr-4">Organisation</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Statut</th>
                  <th className="pb-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {adminList?.map(admin => (
                  <tr key={admin.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 pr-4 font-medium">{admin.full_name}</td>
                    <td className="py-3 pr-4 text-gray-500">{admin.email}</td>
                    <td className="py-3 pr-4">{admin.organization_name || '-'}</td>
                    <td className="py-3 pr-4 capitalize">{admin.partner_type || '-'}</td>
                    <td className="py-3 pr-4">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${admin.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {admin.is_active ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="py-3">
                      <button onClick={() => toggleMutation.mutate(admin.id)} className="text-primary hover:text-primary-600">
                        {admin.is_active ? <FiToggleRight className="text-xl text-green-500" /> : <FiToggleLeft className="text-xl text-gray-400" />}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
              <h2 className="font-bold text-lg mb-4">Creer un admin partenaire</h2>
              <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form) }} className="space-y-3">
                {[
                  { label: 'Nom complet', key: 'full_name', type: 'text' },
                  { label: 'Email', key: 'email', type: 'email' },
                  { label: 'Telephone', key: 'phone', type: 'tel' },
                  { label: 'Mot de passe', key: 'password', type: 'password' },
                  { label: 'Organisation', key: 'organization_name', type: 'text' },
                ].map(({ label, key, type }) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <input type={type} className="input-field" value={form[key]} onChange={set(key)} required />
                  </div>
                ))}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type de partenaire</label>
                  <select className="input-field" value={form.partner_type} onChange={set('partner_type')}>
                    <option value="notaire">Notaire</option>
                    <option value="universite">Universite</option>
                    <option value="entreprise">Entreprise</option>
                    <option value="gouvernement">Gouvernement</option>
                    <option value="autre">Autre</option>
                  </select>
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">Annuler</button>
                  <button type="submit" disabled={createMutation.isPending} className="btn-primary flex-1">
                    {createMutation.isPending ? 'Creation...' : 'Creer'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

