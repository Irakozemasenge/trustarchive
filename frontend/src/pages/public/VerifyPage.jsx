import { useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../api/axios'
import Navbar from '../../components/Navbar'
import StatusBadge from '../../components/StatusBadge'
import { FiSearch, FiCheckCircle, FiXCircle, FiShield } from 'react-icons/fi'

export default function VerifyPage() {
  const { uniqueNumber } = useParams()
  const [query, setQuery] = useState(uniqueNumber || '')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleVerify = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    try {
      const { data } = await api.get(`/documents/verify/${query.trim()}/`)
      setResult(data)
    } catch {
      setResult({ found: false, authentic: false })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-16">
        <div className="text-center mb-10">
          <FiShield className="text-primary text-5xl mx-auto mb-3" />
          <h1 className="text-3xl font-bold text-gray-800">Verifier un document</h1>
          <p className="text-gray-500 mt-2">Entrez le numero unique (ex: TA-2024-AB12CD34)</p>
        </div>
        <form onSubmit={handleVerify} className="flex gap-2 mb-8">
          <input type="text" className="input-field flex-1" placeholder="TA-2024-XXXXXXXX"
            value={query} onChange={e => setQuery(e.target.value)} />
          <button type="submit" disabled={loading} className="btn-primary px-6 flex items-center gap-2">
            <FiSearch /> {loading ? '...' : 'Verifier'}
          </button>
        </form>

        {result && (
          <div className={`card border-2 ${result.authentic ? 'border-green-400' : 'border-red-400'}`}>
            <div className="flex items-center gap-3 mb-4">
              {result.authentic
                ? <FiCheckCircle className="text-green-500 text-4xl" />
                : <FiXCircle className="text-red-500 text-4xl" />}
              <div>
                <p className="text-lg font-bold">{result.authentic ? 'Document Authentique' : 'Document Non Trouve ou Invalide'}</p>
                {result.found && <StatusBadge status={result.document.status} />}
              </div>
            </div>
            {result.found && result.document && (
              <div className="grid grid-cols-2 gap-3 text-sm mt-4 border-t pt-4">
                <div><p className="text-gray-400">Numero unique</p><p className="font-medium">{result.document.unique_number}</p></div>
                <div><p className="text-gray-400">Titre</p><p className="font-medium">{result.document.title}</p></div>
                <div><p className="text-gray-400">Delivre a</p><p className="font-medium">{result.document.issued_to}</p></div>
                <div><p className="text-gray-400">Date emission</p><p className="font-medium">{result.document.issued_date}</p></div>
                <div><p className="text-gray-400">Categorie</p><p className="font-medium">{result.document.category_name}</p></div>
                <div><p className="text-gray-400">Emis par</p><p className="font-medium">{result.document.issued_by_org}</p></div>
                {result.document.expiry_date && (
                  <div><p className="text-gray-400">Expiration</p><p className="font-medium">{result.document.expiry_date}</p></div>
                )}
                <div className="col-span-2"><p className="text-gray-400">Hash blockchain</p>
                  <p className="font-mono text-xs break-all text-gray-600">{result.document.document_hash}</p></div>
                {result.document.qr_code_url && (
                  <div className="col-span-2 flex justify-center mt-2">
                    <img src={result.document.qr_code_url} alt="QR Code" className="w-32 h-32" />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
