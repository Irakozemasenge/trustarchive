const map = {
  verified:   { label: 'Vérifié',    cls: 'badge-verified' },
  pending:    { label: 'En attente', cls: 'badge-pending' },
  revoked:    { label: 'Révoqué',    cls: 'badge-revoked' },
  rejected:   { label: 'Rejeté',     cls: 'badge-revoked' },
  processing: { label: 'En cours',   cls: 'badge-pending' },
  approved:   { label: 'Approuvée',  cls: 'badge-verified' },
}

export default function StatusBadge({ status }) {
  const { label, cls } = map[status] || { label: status, cls: 'badge-pending' }
  return <span className={cls}>{label}</span>
}
