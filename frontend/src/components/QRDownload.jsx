import { FiDownload } from 'react-icons/fi'

/**
 * Télécharge un QR code depuis son URL en forçant le download
 */
export function downloadQR(url, filename) {
  fetch(url)
    .then(res => res.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = filename || 'qrcode.png'
      a.click()
      URL.revokeObjectURL(a.href)
    })
    .catch(() => {
      // Fallback : ouvrir dans un nouvel onglet
      window.open(url, '_blank')
    })
}

export default function QRDownload({ url, filename, size = 'sm' }) {
  if (!url) return null

  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-20 h-20',
  }

  return (
    <div className="flex items-center gap-2">
      <img src={url} alt="QR Code" className={`${sizes[size]} rounded border`} />
      <button
        onClick={() => downloadQR(url, filename)}
        title="Telecharger le QR code"
        className="p-1.5 text-primary hover:bg-primary/10 rounded-lg transition-colors"
      >
        <FiDownload className="text-sm" />
      </button>
    </div>
  )
}
