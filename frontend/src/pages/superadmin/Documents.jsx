import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import StatusBadge from '../../components/StatusBadge'
import toast from 'react-hot-toast'
import { FiHome, FiUsers, FiFileText, FiLink, FiTag, FiActivity, FiXCircle } from 'react-icons/fi'

const links = [
  { to: "/superadmin", icon: FiHome, label: "Tableau de bord" },
  { to: "/superadmin/admins", icon: FiUsers, label: "Admins partenaires" },
  { to: "/superadmin/documents", icon: FiFileText, label: "Tous les documents" },
  { to: "/superadmin/categories", icon: FiTag, label: "Categories" },
  { to: "/superadmin/blockchain", icon: FiLink, label: "Blockchain" },
  { to: "/superadmin/audit", icon: FiActivity, label: "Journal d audit" },
]

export default function SuperDocuments() {
  const qc = useQueryClient()
  const { data: docs, isLoading } = useQuery({ queryKey: ['allDocs'], queryFn: () => api.get('/documents/all/').then(r => r.data) })
  const list = docs?.results ?? docs ?? []

  const revokeMutation = useMutation({
    mutationFn: (id) => api.patch(`/documents/${id}/revoke/`),
    onSuccess: () => { toast.success('Document revoque'); qc.invalidateQueries(['allDocs']) }
  })

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Tous les Documents</h1>
        <div className="card overflow-x-auto">
          {isLoading ? <p className="text-gray-400">Chargement...</p> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-3">Numero unique</th>
                  <th className="pb-3 pr-3">Titre</th>
                  <th className="pb-3 pr-3">Delivre a</th>
                  <th className="pb-3 pr-3">Emis par</th>
                  <th className="pb-3 pr-3">Date</th>
                  <th className="pb-3 pr-3">Statut</th>
                  <th className="pb-3 pr-3">QR</th>
                  <th className="pb-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {list?.map(doc => (
                  <tr key={doc.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 pr-3 font-mono text-xs text-primary font-bold">{doc.unique_number}</td>
                    <td className="py-2 pr-3">{doc.title}</td>
                    <td className="py-2 pr-3">{doc.issued_to}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{doc.issued_by_info?.organization_name || doc.issued_by_info?.full_name}</td>
                    <td className="py-2 pr-3">{doc.issued_date}</td>
                    <td className="py-2 pr-3"><StatusBadge status={doc.status} /></td>
                    <td className="py-2 pr-3">{doc.qr_code_url && <img src={doc.qr_code_url} alt="qr" className="w-8 h-8" />}</td>
                    <td className="py-2">
                      {doc.status !== 'revoked' && (
                        <button onClick={() => revokeMutation.mutate(doc.id)} className="text-red-500 hover:text-red-700 flex items-center gap-1 text-xs">
                          <FiXCircle /> Revoquer
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  )
}

