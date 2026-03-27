# Nsuzumira

**Nsuzumira** (Kirundi: "Verifier / Authentifier") — Modele LLM fine-tune sur Gemma-7b
pour l'analyse de documents officiels burundais.

Developpe pour **TrustArchive.bi** dans le cadre de la formation BuruDigi.

## Architecture

```
google/gemma-7b (base)
    + QLoRA 4-bit (bitsandbytes)
    + LoRA adapters (rank=16, alpha=32)
    + Dataset 11000 docs burundais
    = Nsuzumira v1.0
```

## Demarrage rapide

```bash
pip install -r requirements.txt

# 1. Generer le dataset
python data/generate_dataset.py

# 2. Fine-tuning (GPU 16GB+)
python scripts/train.py --hf_token hf_xxx

# 3. Lancer l API LLM
cd api && python main.py

# 4. Tester
curl -X POST http://localhost:8001/analyze \
  -d '{"text": "DIPLOME DE LICENCE..."}'
```

## API Endpoints

| Route | Description |
|-------|-------------|
| GET / | Info modele |
| GET /health | Statut |
| POST /analyze | Analyser un document |
| POST /chat | Chat |
| GET /models | Modeles |

## Dataset

- 11 000 exemples generes
- 14 types: diplomes, actes notaries, attestations, casiers, permis, CNI, mariages...
- Noms, villes, organisations burundaises reels
- Format Gemma instruction-following

## Variables d environnement

```env
PORT=8001
NSUZUMIRA_MODEL_PATH=../model/nsuzumira-lora
NSUZUMIRA_BASE_MODEL=google/gemma-7b
HF_TOKEN=hf_votre_token
NSUZUMIRA_MOCK=false   # true pour tester sans GPU
```

## Publication HuggingFace

```bash
python scripts/push_to_hub.py --token hf_xxx --hub_id VotreNom/nsuzumira
```

Modele disponible sur: https://huggingface.co/Irakozemasenge/nsuzumira
