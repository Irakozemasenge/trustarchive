# -*- coding: utf-8 -*-
"""
Nsuzumira LLM API - Serveur FastAPI
Modele: google/gemma-7b fine-tune pour documents burundais
"""
import os
import re
import json
import time
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nsuzumira")

# ─── Modele global ────────────────────────────────────────────────────────────
model = None
tokenizer = None
MODEL_LOADED = False

PROMPT_TEMPLATE = """<start_of_turn>user
Tu es Nsuzumira, un assistant IA specialise dans l analyse de documents officiels burundais.
Analyse le document suivant et fournis une reponse JSON structuree avec:
- summary: Resume essentiel en 2-3 phrases
- type_document: Type du document
- beneficiaire: Nom du beneficiaire
- organisme_emetteur: Organisation emettrice
- date_emission: Date d emission
- numero_reference: Numero de reference
- informations_cles: Liste des informations importantes
- validite: Valide/Expire/Indetermine
- langue: Langue du document
- observations: Observations importantes

DOCUMENT:
{texte}
<end_of_turn>
<start_of_turn>model
"""


def load_model():
    global model, tokenizer, MODEL_LOADED
    model_path = os.environ.get("NSUZUMIRA_MODEL_PATH", "./model/nsuzumira-lora")
    base_model = os.environ.get("NSUZUMIRA_BASE_MODEL", "google/gemma-7b")
    hf_token = os.environ.get("HF_TOKEN", "")
    use_mock = os.environ.get("NSUZUMIRA_MOCK", "false").lower() == "true"

    if use_mock:
        logger.info("Mode MOCK active - pas de chargement GPU")
        MODEL_LOADED = True
        return

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        logger.info(f"Chargement tokenizer depuis {model_path}...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path if os.path.exists(model_path) else base_model,
            token=hf_token
        )

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        logger.info(f"Chargement modele de base: {base_model}...")
        base = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            token=hf_token,
        )

        if os.path.exists(model_path):
            from peft import PeftModel
            logger.info(f"Application adaptateurs LoRA depuis {model_path}...")
            model = PeftModel.from_pretrained(base, model_path)
        else:
            logger.warning("Adaptateurs LoRA non trouves - utilisation modele de base")
            model = base

        model.eval()
        MODEL_LOADED = True
        logger.info("Nsuzumira charge avec succes")

    except Exception as e:
        logger.error(f"Erreur chargement modele: {e}")
        logger.info("Passage en mode fallback")
        MODEL_LOADED = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield
    logger.info("Nsuzumira API arretee")


# ─── Application FastAPI ──────────────────────────────────────────────────────
app = FastAPI(
    title="Nsuzumira API",
    description="LLM API pour analyse de documents officiels burundais - TrustArchive.bi",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Schemas ──────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text: str
    max_tokens: int = 512
    temperature: float = 0.2
    metadata: Optional[dict] = None


class AnalyzeResponse(BaseModel):
    success: bool
    analysis: dict
    model: str
    processing_time: float
    tokens_used: int


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    max_tokens: int = 256


# ─── Helpers ──────────────────────────────────────────────────────────────────
def parse_json_response(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"summary": text[:300], "raw_response": True}


def generate_mock_analysis(text: str, metadata: dict = None) -> dict:
    """Analyse de secours quand le modele GPU n est pas disponible"""
    meta = metadata or {}
    return {
        "summary": f"Document officiel burundais analyse par Nsuzumira. {meta.get('title', 'Document')} delivre a {meta.get('issued_to', 'beneficiaire')}.",
        "type_document": meta.get("category", "Document officiel"),
        "beneficiaire": meta.get("issued_to", "Non specifie"),
        "organisme_emetteur": meta.get("issued_by", "Organisation partenaire"),
        "date_emission": str(meta.get("issued_date", "Non specifie")),
        "numero_reference": meta.get("unique_number", ""),
        "informations_cles": [
            f"Numero unique: {meta.get('unique_number', 'N/A')}",
            f"Statut: {meta.get('status', 'verified')}",
            "Enregistre sur blockchain TrustArchive.bi",
        ],
        "validite": "Valide" if meta.get("status") == "verified" else "A verifier",
        "langue": "Francais",
        "observations": "Analyse generee en mode fallback - configurez GPU pour analyse complete",
        "mode": "fallback"
    }


def run_inference(text: str, max_tokens: int = 512, temperature: float = 0.2, metadata: dict = None):
    use_mock = os.environ.get("NSUZUMIRA_MOCK", "false").lower() == "true"

    if use_mock or model is None:
        return generate_mock_analysis(text, metadata), 0

    try:
        import torch
        prompt = PROMPT_TEMPLATE.format(texte=text[:2000])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )

        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )
        tokens = outputs.shape[1]
        return parse_json_response(response), tokens

    except Exception as e:
        logger.error(f"Erreur inference: {e}")
        return generate_mock_analysis(text, metadata), 0


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "model": "Nsuzumira",
        "version": "1.0.0",
        "base": "google/gemma-7b",
        "status": "ready" if MODEL_LOADED else "loading",
        "description": "LLM specialise documents officiels burundais - TrustArchive.bi",
        "project": "Formation des formateurs BuruDigi"
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL_LOADED}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_document(req: AnalyzeRequest):
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Modele en cours de chargement")

    start = time.time()
    result, tokens = run_inference(req.text, req.max_tokens, req.temperature, req.metadata)
    elapsed = round(time.time() - start, 3)

    model_name = "nsuzumira-mock" if result.get("mode") == "fallback" else "nsuzumira-gemma7b-lora"

    return AnalyzeResponse(
        success=True,
        analysis=result,
        model=model_name,
        processing_time=elapsed,
        tokens_used=tokens,
    )


@app.post("/chat")
def chat(req: ChatRequest):
    """Endpoint conversationnel pour questions sur les documents"""
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Modele en cours de chargement")

    context_str = f"\nContexte: {req.context}" if req.context else ""
    prompt = f"""<start_of_turn>user
Tu es Nsuzumira, assistant IA pour TrustArchive.bi.{context_str}
Question: {req.message}
<end_of_turn>
<start_of_turn>model
"""
    use_mock = os.environ.get("NSUZUMIRA_MOCK", "false").lower() == "true"
    if use_mock or model is None:
        return {"response": f"Nsuzumira (mode demo): Je suis specialise dans l analyse de documents officiels burundais. {req.message}", "model": "nsuzumira-mock"}

    try:
        import torch
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=req.max_tokens, temperature=0.7, do_sample=True, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return {"response": response, "model": "nsuzumira-gemma7b-lora"}
    except Exception as e:
        return {"response": f"Erreur: {str(e)}", "model": "error"}


@app.get("/models")
def list_models():
    return {
        "models": [
            {"id": "nsuzumira-gemma7b-lora", "base": "google/gemma-7b", "type": "causal-lm", "domain": "documents-burundais"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
