# Nsuzumira — Modèle IA pour TrustArchive.bi

**Nsuzumira** signifie "Vérifier / Authentifier" en Kirundi.

Modèle de langage fine-tuné sur Gemma-7b, spécialisé dans l'analyse et
l'authentification des documents officiels burundais.

## Architecture
- Base: google/gemma-7b
- Fine-tuning: QLoRA (4-bit quantization + LoRA adapters)
- Domaine: Documents officiels (diplômes, actes notariés, certificats...)
- Langues: Français, Kirundi, Anglais

## Structure
```
nsuzumira/
├── data/
│   ├── train.jsonl          # Dataset d'entraînement
│   ├── eval.jsonl           # Dataset d'évaluation
│   └── generate_dataset.py  # Script génération données
├── scripts/
│   ├── train.py             # Script fine-tuning QLoRA
│   ├── inference.py         # Inférence locale
│   └── push_to_hub.py       # Publier sur HuggingFace
├── model/                   # Poids LoRA sauvegardés
└── requirements.txt
```

## Utilisation rapide
```bash
pip install -r requirements.txt
python scripts/train.py
python scripts/inference.py --doc "Diplome de licence..."
```
