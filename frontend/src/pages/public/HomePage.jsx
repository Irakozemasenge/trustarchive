import { Link } from "react-router-dom"
import Navbar from "../../components/Navbar"
import { FiShield, FiSearch, FiLock, FiFileText, FiCheckCircle, FiUsers, FiAward } from "react-icons/fi"

const partners = [
  { name: "Universites", icon: FiAward, desc: "Diplomes et attestations" },
  { name: "Notaires", icon: FiFileText, desc: "Actes notaries" },
  { name: "Entreprises", icon: FiUsers, desc: "Certificats professionnels" },
  { name: "Gouvernement", icon: FiShield, desc: "Documents administratifs" },
]

const steps = [
  { n: "01", title: "Enregistrement", desc: "L admin partenaire enregistre le document sur la plateforme" },
  { n: "02", title: "Numero unique", desc: "Le systeme genere un identifiant TA-YYYY-XXXXXXXX et un QR code" },
  { n: "03", title: "Blockchain", desc: "Le document est ancre sur la blockchain locale de facon immuable" },
  { n: "04", title: "Verification", desc: "N importe qui peut verifier l authenticite en quelques secondes" },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      {/* Hero */}
      <section className="relative bg-primary text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 rounded-full bg-accent blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-blue-400 blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 py-24 flex flex-col lg:flex-row items-center gap-12">
          <div className="flex-1 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 bg-white/10 rounded-full px-4 py-1.5 text-sm mb-6">
              <FiShield className="text-accent" />
              <span>Plateforme officielle du Burundi</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold mb-4 leading-tight">
              Trust<span className="text-accent">Archive</span>
              <span className="text-accent">.bi</span>
            </h1>
            <p className="text-xl text-blue-200 mb-3 max-w-xl">
              Plateforme nationale de gestion, d authentification et de verification des documents professionnels, academiques et administratifs.
            </p>
            <p className="text-sm text-blue-300 mb-8 italic">
              Developpe dans le cadre de la formation des formateurs <span className="text-accent font-semibold">BuruDigi</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link to="/verify" className="bg-accent hover:bg-accent-dark text-white px-8 py-3.5 rounded-xl font-semibold text-lg transition-colors flex items-center justify-center gap-2">
                <FiSearch /> Verifier un document
              </Link>
              <Link to="/register" className="bg-white/10 hover:bg-white/20 border border-white/30 text-white px-8 py-3.5 rounded-xl font-semibold text-lg transition-colors">
                Creer un compte
              </Link>
            </div>
          </div>
          <div className="flex-shrink-0">
            <div className="relative w-64 h-64 lg:w-80 lg:h-80">
              <div className="absolute inset-0 bg-accent/20 rounded-3xl rotate-6" />
              <div className="absolute inset-0 bg-white/10 rounded-3xl -rotate-3" />
              <div className="relative bg-white/10 backdrop-blur rounded-3xl p-8 flex flex-col items-center justify-center h-full gap-4">
                <FiShield className="text-accent text-7xl" />
                <div className="text-center">
                  <p className="font-bold text-lg">Document Verifie</p>
                  <p className="text-blue-200 text-sm">Protege par Blockchain</p>
                </div>
                <div className="flex items-center gap-2 bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-xs">
                  <FiCheckCircle /> Authentique
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-primary-600 text-white py-8">
        <div className="max-w-6xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { label: "Documents enregistres", value: "100%" },
            { label: "Securite Blockchain", value: "SHA-256" },
            { label: "Verification", value: "< 2s" },
            { label: "Disponibilite", value: "24/7" },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-3xl font-bold text-accent">{value}</p>
              <p className="text-blue-200 text-sm mt-1">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-800 mb-3">Pourquoi TrustArchive.bi ?</h2>
            <p className="text-gray-500 max-w-xl mx-auto">Une solution complete pour garantir l authenticite de vos documents officiels</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: FiShield, title: "Securite Blockchain", desc: "Chaque document est ancre sur une blockchain immuable. Toute tentative de falsification est immediatement detectee.", color: "text-blue-600 bg-blue-50" },
              { icon: FiSearch, title: "Verification Instantanee", desc: "Verifiez l authenticite de n importe quel document en quelques secondes via son numero unique ou en scannant son QR code.", color: "text-green-600 bg-green-50" },
              { icon: FiLock, title: "Numero Unique", desc: "Chaque document recoit un identifiant TA-YYYY-XXXXXXXX infalsifiable genere automatiquement et lie a la blockchain.", color: "text-purple-600 bg-purple-50" },
            ].map(({ icon: Icon, title, desc, color }) => (
              <div key={title} className="card text-center hover:shadow-md transition-shadow">
                <div className={`inline-flex p-4 rounded-2xl ${color} mb-4`}>
                  <Icon className="text-3xl" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comment ca marche */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-800 mb-3">Comment ca fonctionne ?</h2>
            <p className="text-gray-500">Un processus simple et securise en 4 etapes</p>
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {steps.map(({ n, title, desc }) => (
              <div key={n} className="relative text-center">
                <div className="w-14 h-14 bg-primary text-white rounded-2xl flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {n}
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Partenaires */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-800 mb-3">Nos Partenaires</h2>
            <p className="text-gray-500">Les institutions qui font confiance a TrustArchive.bi</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {partners.map(({ name, icon: Icon, desc }) => (
              <div key={name} className="card text-center hover:shadow-md transition-shadow">
                <Icon className="text-primary text-3xl mx-auto mb-3" />
                <p className="font-semibold text-gray-800">{name}</p>
                <p className="text-gray-400 text-xs mt-1">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-primary text-white text-center">
        <div className="max-w-2xl mx-auto">
          <FiFileText className="text-accent text-5xl mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">Besoin d un document officiel ?</h2>
          <p className="text-blue-200 mb-8">Faites votre demande en ligne et suivez son traitement en temps reel aupres de nos partenaires.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/request" className="bg-accent hover:bg-accent-dark text-white px-8 py-3.5 rounded-xl font-semibold transition-colors">
              Faire une demande
            </Link>
            <Link to="/verify" className="bg-white/10 hover:bg-white/20 border border-white/30 text-white px-8 py-3.5 rounded-xl font-semibold transition-colors">
              Verifier un document
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-10 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <FiShield className="text-accent text-2xl" />
              <span className="font-bold text-white text-lg">TrustArchive<span className="text-accent">.bi</span></span>
            </div>
            <p className="text-sm text-center">
              Developpe dans le cadre de la formation des formateurs{" "}
              <span className="text-accent font-semibold">BuruDigi</span> — Burundi Digital
            </p>
            <p className="text-sm">© 2024 TrustArchive.bi</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
