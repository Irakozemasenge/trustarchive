import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'
import { FiCpu, FiRefreshCw, FiCheckCircle, FiAlertCircle, FiClock, FiChevronDown, FiChevronUp } from 'react-icons/fi'

const statusIcon = {
  completed: <FiCheckCircle className="text-green-500" />,
  failed: <FiAlertCircle className="text-red-500" />,
  processing: <FiClock className="text-yellow-500 animate-spin" />,
  pending: <FiClock className="text-gray-400" />,
}

export default function AIAnalysis({ docId }) {
  const qc = useQueryClient()
  const [expanded, setExpanded] = useState(false)

  const { data: analysis, isLoading } = useQuery({
    queryKey: ['analysis', docId],
    queryFn: () => api.get(`/ai/result/${docId}/`).then(r => r.data).catch(() => null),
    retry: false,
  })

  const analyzeMutation = useMutation({
    mutationFn: () => api.post(`/ai/analyze/${docId}/`),
    onSuccess: () => qc.invalidateQueries(['analysis', docId]),
  })

  const keyInfo = analysis?.key_information || {}

  return (
    <div className="border rounded-xl overflow-hidden">
      <div
        className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-primary/5 to-purple-50 cursor-pointer"
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex items-center gap-2">
          <FiCpu className="text-primary text-lg" />
          <span className="font-semibold text-sm text-gray-700">Analyse Nsuzumira IA</span>
          {analysis && statusIcon[analysis.status]}
        </div>
        <div className="flex items-center gap-2">
          {(!analysis || analysis.status === 'failed') && (
            <button
              onClick={(e) => { e.stopPropagation(); analyzeMutation.mutate() }}
              disabled={analyzeMutation.isPending}
              className="flex items-center gap-1 text-xs bg-primary text-white px-3 py-1 rounded-lg hover:bg-primary-600 disabled:opacity-50"
            >
              <FiRefreshCw className={analyzeMutation.isPending ? 'animate-spin' : ''} />
              {analyzeMutation.isPending ? 'Analyse...' : 'Analyser'}
            </button>
          )}
          {expanded ? <FiChevronUp className="text-gray-400" /> : <FiChevronDown className="text-gray-400" />}
        </div>
      </div>

      {expanded && (
        <div className="p-4 bg-white">
          {isLoading ? (
            <p className="text-gray-400 text-sm">Chargement...</p>
          ) : !analysis ? (
            <div className="text-center py-4">
              <FiCpu className="text-gray-300 text-4xl mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Aucune analyse disponible</p>
              <button
                onClick={() => analyzeMutation.mutate()}
                disabled={analyzeMutation.isPending}
                className="mt-3 btn-primary text-sm px-4 py-1.5"
              >
                {analyzeMutation.isPending ? 'Analyse en cours...' : 'Lancer l analyse Nsuzumira'}
              </button>
            </div>
          ) : analysis.status === 'failed' ? (
            <div className="text-red-500 text-sm">
              <p className="font-medium">Analyse echouee</p>
              <p className="text-xs text-gray-400 mt-1">{analysis.error_message}</p>
            </div>
          ) : analysis.status === 'completed' ? (
            <div className="space-y-4">
              {/* Résumé */}
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-xs font-semibold text-blue-700 mb-1">Resume Nsuzumira</p>
                <p className="text-sm text-gray-700">{analysis.summary}</p>
              </div>

              {/* Infos clés */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                {[
                  { label: 'Type document', key: 'type_document' },
                  { label: 'Beneficiaire', key: 'beneficiaire' },
                  { label: 'Organisme', key: 'organisme_emetteur' },
                  { label: 'Date emission', key: 'date_emission' },
                  { label: 'Reference', key: 'numero_reference' },
                  { label: 'Validite', key: 'validite' },
                  { label: 'Langue', key: 'langue' },
                ].map(({ label, key }) => keyInfo[key] ? (
                  <div key={key}>
                    <p className="text-gray-400">{label}</p>
                    <p className="font-medium text-gray-700">{keyInfo[key]}</p>
                  </div>
                ) : null)}
              </div>

              {/* Informations clés */}
              {keyInfo.informations_cles?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1">Informations cles</p>
                  <ul className="space-y-1">
                    {keyInfo.informations_cles.map((info, i) => (
                      <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                        <span className="text-primary mt-0.5">•</span> {info}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Observations */}
              {keyInfo.observations && (
                <div className="bg-yellow-50 rounded-lg p-2">
                  <p className="text-xs font-semibold text-yellow-700 mb-0.5">Observations</p>
                  <p className="text-xs text-gray-600">{keyInfo.observations}</p>
                </div>
              )}

              {/* Texte extrait */}
              {analysis.extracted_text && (
                <details className="text-xs">
                  <summary className="text-gray-400 cursor-pointer hover:text-gray-600">
                    Texte extrait (OCR)
                  </summary>
                  <pre className="mt-2 bg-gray-50 p-2 rounded text-xs text-gray-500 whitespace-pre-wrap max-h-32 overflow-y-auto">
                    {analysis.extracted_text}
                  </pre>
                </details>
              )}

              <div className="flex items-center justify-between text-xs text-gray-300 pt-2 border-t">
                <span>Modele: {analysis.model_used}</span>
                <span>{analysis.tokens_used > 0 ? `${analysis.tokens_used} tokens` : ''}</span>
                <button
                  onClick={() => analyzeMutation.mutate()}
                  className="text-primary hover:underline"
                >
                  Re-analyser
                </button>
              </div>
            </div>
          ) : (
            <p className="text-yellow-600 text-sm">Analyse en cours...</p>
          )}
        </div>
      )}
    </div>
  )
}
