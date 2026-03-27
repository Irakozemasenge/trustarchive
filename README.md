# TrustArchive.bi

Plateforme nationale de gestion et d'authentification des documents professionnels, academiques et administratifs du Burundi.

> Developpe dans le cadre de la **formation des formateurs BuruDigi** — Burundi Digital

## Stack
- Backend: Django 4.2 + DRF + MySQL/MariaDB + Blockchain locale
- Frontend: ReactJS 18 + TailwindCSS + Vite

---

## Demarrage Backend

```bash
cd trustarchive/backend

# Installer les dependances (utiliser python3.13t.exe si Python 3.13 free-threaded)
$p = "C:\Program Files\Python313\python3.13t.exe"
& $p -m pip install -r requirements.txt

# Creer la base MySQL
# CREATE DATABASE trustarchive_db CHARACTER SET utf8mb4;

# Configurer .env (DB_NAME, DB_USER, DB_PASSWORD...)

# Migrations
& $p manage.py makemigrations accounts documents blockchain requests audit
& $p manage.py migrate

# Creer le super admin
& $p manage.py createsuperuser

# Lancer le serveur
& $p manage.py runserver
```

## Demarrage Frontend

```bash
cd trustarchive/frontend
npm install
npm run dev
```

---

## 3 Espaces

| Espace | URL | Role |
|--------|-----|------|
| Public | / | Verification, demande en ligne |
| Admin partenaire | /admin | Notaires, universites, entreprises |
| Super Admin | /superadmin | Gestion globale + blockchain + audit |

## APIs disponibles

| Endpoint | Description |
|----------|-------------|
| POST /api/auth/login/ | Connexion |
| GET /api/documents/verify/{num}/ | Verification publique |
| POST /api/documents/ | Enregistrer un document |
| GET /api/audit/logs/ | Journal d audit (superadmin) |
| GET /api/audit/errors/ | Erreurs systeme (superadmin) |
| GET /api/blockchain/verify-chain/ | Integrite blockchain |
