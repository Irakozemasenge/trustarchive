import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import Sidebar from '../../components/Sidebar'
import { FiHome, FiUsers, FiFileText, FiLink, FiTag, FiActivity, FiCheckCircle, FiXCircle, FiShield } from 'react-icons/fi'

const links = [
  { to: "/superadmin", icon: FiHome, label: "Tableau de bord" },
  { to: "/superadmin/admins", icon: FiUsers, label: "Admins partenaires" },
  { to: "/superadmin/documents", icon: FiFileText, label: "Tous les documents" },
  { to: "/superadmin/categories", icon: FiTag, label: "Categories" },
  { to: "/superadmin/blockchain", icon: FiLink, label: "Blockchain" },
  { to: "/superadmin/audit", icon: FiActivity, label: "Journal d audit" },
]

export default function SuperBlockchain() {
  const [chainResult, setChainResult] = useState(null)
  const [verifying, setVerifying] = useState(false)

  const { data: records, isLoading } = useQuery({ queryKey: ['blockchainRecords'], queryFn: () => api.get('/blockchain/records/').then(r => r.data) })
  const recordList = records?.results ?? records ?? []

  const verifyChain = async () => {
    setVerifying(true)
    try {
      const { data } = await api.get('/blockchain/verify-chain/')
      setChainResult(data)
    } catch {
      setChainResult({ valid: false, message: 'Erreur de verification' })
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar links={links} />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Registre Blockchain</h1>
            <p className="text-gray-500 text-sm">Chaque document enregistre cree un bloc immuable</p>
          </div>
          <button onClick={verifyChain} disabled={verifying} className="btn-primary flex items-center gap-2">
            <FiShield /> {verifying ? 'Verification...' : 'Verifier la chaine'}
          </button>
        </div>

        {chainResult && (
          <div className={`card mb-6 flex items-center gap-3 border-2 ${chainResult.valid ? 'border-green-400 bg-green-50' : 'border-red-400 bg-red-50'}`}>
            {chainResult.valid
              ? <FiCheckCircle className="text-green-500 text-3xl" />
              : <FiXCircle className="text-red-500 text-3xl" />}
            <div>
              <p className="font-bold">{chainResult.valid ? 'Chaine integre' : 'Chaine corrompue'}</p>
              <p className="text-sm text-gray-600">{chainResult.message}</p>
            </div>
          </div>
        )}

        <div className="card overflow-x-auto">
          <h2 className="font-semibold text-gray-700 mb-4">Blocs enregistres ({recordList?.length ?? 0})</h2>
          {isLoading ? <p className="text-gray-400">Chargement...</p> : (
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-3">Bloc #</th>
                  <th className="pb-3 pr-3">Numero document</th>
                  <th className="pb-3 pr-3">Hash du bloc</th>
                  <th className="pb-3 pr-3">Hash precedent</th>
                  <th className="pb-3">Date</th>
                </tr>
              </thead>
              <tbody>
                {recordList?.map(r => (
                  <tr key={r.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 pr-3 font-bold text-primary">#{r.block_index}</td>
                    <td className="py-2 pr-3 font-mono text-primary">{r.document_unique_number}</td>
                    <td className="py-2 pr-3 font-mono text-gray-500 max-w-xs truncate">{r.block_hash}</td>
                    <td className="py-2 pr-3 font-mono text-gray-400 max-w-xs truncate">{r.previous_hash}</td>
                    <td className="py-2 text-gray-500">{new Date(r.created_at).toLocaleDateString('fr-FR')}</td>
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

