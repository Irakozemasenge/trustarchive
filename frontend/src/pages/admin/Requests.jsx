import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import StatusBadge from '../../components/StatusBadge'
import toast from 'react-hot-toast'
import { FiHome, FiFileText, FiInbox, FiPlusCircle, FiGrid } from 'react-icons/fi'

const links = [
  { to: '/admin', icon: FiHome, label: 'Tableau de bord' },
  { to: '/admin/documents', icon: FiFileText, label: 'Documents' },
  { to: '/admin/documents/add', icon: FiPlusCircle, label: 'Ajouter document' },
  { to: '/admin/qrcodes', icon: FiGrid, label: 'QR Codes' },
  { to: '/admin/requests', icon: FiInbox, label: 'Demandes' },
]

export default function AdminRequests() {
  const qc = useQueryClient()
  const [selected, setSelected] = useState(null)
  const [notes, setNotes] = useState('')
  const [newStatus, setNewStatus] = useState('processing')

  const { data: requests, isLoading } = useQuery({ queryKey: ['adminRequests'], queryFn: () => api.get('/requests/admin/').then(r => r.data) })
  const reqList = requests?.results ?? requests ?? []

  const mutation = useMutation({
    mutationFn: ({ id, payload }) => api.patch(`/requests/${id}/update/`, payload),
    onSuccess: () => { toast.success('Demande mise a jour'); qc.invalidateQueries(['adminRequests']); setSelected(null) }
  })

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Demandes en ligne</h1>
        <div className="card overflow-x-auto">
          {isLoading ? <p className="text-gray-400">Chargement...</p> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4">#</th>
                  <th className="pb-3 pr-4">Demandeur</th>
                  <th className="pb-3 pr-4">Document</th>
                  <th className="pb-3 pr-4">Type</th>
                  <th className="pb-3 pr-4">Statut</th>
                  <th className="pb-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {reqList?.map(req => (
                  <tr key={req.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 pr-4 text-gray-400">#{req.id}</td>
                    <td className="py-3 pr-4">{req.requester_info?.full_name}</td>
                    <td className="py-3 pr-4">{req.document_title}</td>
                    <td className="py-3 pr-4">{req.request_type}</td>
                    <td className="py-3 pr-4"><StatusBadge status={req.status} /></td>
                    <td className="py-3">
                      <button onClick={() => { setSelected(req); setNotes(req.admin_notes || ''); setNewStatus(req.status) }}
                        className="text-primary text-xs hover:underline">Traiter</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {selected && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
              <h2 className="font-bold text-lg mb-4">Traiter la demande #{selected.id}</h2>
              <p className="text-sm text-gray-500 mb-1">Document: <span className="text-gray-800">{selected.document_title}</span></p>
              <p className="text-sm text-gray-500 mb-4">Description: <span className="text-gray-800">{selected.description}</span></p>
              <div className="mb-3">
                <label className="block text-sm font-medium mb-1">Nouveau statut</label>
                <select className="input-field" value={newStatus} onChange={e => setNewStatus(e.target.value)}>
                  <option value="pending">En attente</option>
                  <option value="processing">En traitement</option>
                  <option value="approved">Approuvee</option>
                  <option value="rejected">Rejetee</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Notes admin</label>
                <textarea className="input-field" rows={3} value={notes} onChange={e => setNotes(e.target.value)} />
              </div>
              <div className="flex gap-3">
                <button onClick={() => setSelected(null)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={() => mutation.mutate({ id: selected.id, payload: { status: newStatus, admin_notes: notes } })}
                  className="btn-primary flex-1">Enregistrer</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

