# TrustArchive.bi

> Plateforme nationale de gestion et d'authentification des documents burundais.
> Developpe dans le cadre de la **formation des formateurs BuruDigi**.

## Stack

| Couche | Technologie |
|--------|-------------|
| Backend | Django 4.2 + DRF + MySQL |
| Frontend | ReactJS 18 + TailwindCSS + Vite |
| Blockchain | SHA-256 proof-of-work local |
| IA | **Nsuzumira** (Gemma-7b QLoRA) |
| Auth | JWT SimpleJWT |

## Structure

```
trustarchive/
├── backend/       Django DRF API
├── frontend/      ReactJS + TailwindCSS
└── nsuzumira/     Modele IA Nsuzumira
    ├── api/       Serveur FastAPI LLM
    ├── data/      Dataset 11000 exemples
    ├── scripts/   Fine-tuning QLoRA
    └── model/     Poids LoRA
```

## Demarrage

### Backend
```bash
cd trustarchive/backend
pip install -r requirements.txt
# Creer DB: CREATE DATABASE trustarchive_db CHARACTER SET utf8mb4;
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd trustarchive/frontend
npm install
npm run dev
```

### Nsuzumira LLM API
```bash
cd trustarchive/nsuzumira/api
pip install -r requirements.txt
# Mode demo sans GPU:
NSUZUMIRA_MOCK=true python main.py
# Mode GPU apres fine-tuning:
HF_TOKEN=hf_xxx python main.py
```

### Fine-tuning Nsuzumira (GPU 16GB+)
```bash
cd trustarchive/nsuzumira
pip install -r requirements.txt
python data/generate_dataset.py        # 11000 exemples
python scripts/train.py --hf_token hf_xxx --epochs 3
python scripts/push_to_hub.py --token hf_xxx
```

## Variables .env

```env
SECRET_KEY=...
DB_NAME=trustarchive_db
DB_USER=root
DB_PASSWORD=...
GEMINI_API_KEY=          # Google AI (optionnel)
NSUZUMIRA_API_URL=http://localhost:8001
HF_TOKEN=                # HuggingFace
```

## Espaces utilisateurs

| Espace | URL | Role |
|--------|-----|------|
| Public | / | Verification, demandes |
| Admin | /admin | Notaires, universites |
| SuperAdmin | /superadmin | Gestion globale + IA |

## API Nsuzumira (port 8001)

```bash
# Analyser un document
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "DIPLOME DE LICENCE...", "max_tokens": 512}'

# Sante
curl http://localhost:8001/health
```

## Dataset Nsuzumira
- 11 000 exemples, 14 types de documents burundais
- Format instruction-following Gemma
- 9900 train / 1100 eval

*TrustArchive.bi — BuruDigi — Burundi Digital*
