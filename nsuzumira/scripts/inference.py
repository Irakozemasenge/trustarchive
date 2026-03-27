"""
Inférence avec Nsuzumira — chargement local ou depuis HuggingFace Hub

Usage:
    python scripts/inference.py --text "DIPLOME DE LICENCE..."
    python scripts/inference.py --file /path/to/document.txt
    python scripts/inference.py --mode api  # Lance un serveur FastAPI
"""
import os
import json
import argparse
import torch


PROMPT_TEMPLATE = """<start_of_turn>user
Tu es Nsuzumira, un assistant IA specialise dans l'analyse de documents officiels burundais.
Analyse le document suivant et fournis une reponse JSON structuree avec:
- summary: Resume essentiel en 2-3 phrases
- type_document: Type du document
- beneficiaire: Nom du beneficiaire
- organisme_emetteur: Organisation emettrice
- date_emission: Date d'emission
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


def load_nsuzumira(model_path=None, hf_token=None):
    """Charge Nsuzumira depuis le chemin local ou HuggingFace"""
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel

    if model_path is None:
        model_path = os.environ.get("NSUZUMIRA_PATH", "../model/nsuzumira-lora")

    base_model_name = "google/gemma-7b"
    hf_token = hf_token or os.environ.get("HF_TOKEN", "")

    print(f"Chargement de Nsuzumira depuis: {model_path}")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path, token=hf_token)

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
        token=hf_token,
    )

    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()

    return model, tokenizer


def analyze(text, model, tokenizer, max_new_tokens=512):
    """Analyse un texte de document avec Nsuzumira"""
    prompt = PROMPT_TEMPLATE.format(texte=text)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    # Parser le JSON
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    return {"summary": response, "raw": True}


def run_api_server(model_path=None, port=8001):
    """Lance un serveur FastAPI pour Nsuzumira"""
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn

        app = FastAPI(title="Nsuzumira API", description="Analyse IA de documents burundais")
        model, tokenizer = load_nsuzumira(model_path)

        class DocumentRequest(BaseModel):
            text: str
            max_tokens: int = 512

        @app.get("/")
        def root():
            return {"model": "Nsuzumira", "status": "ready", "base": "google/gemma-7b"}

        @app.post("/analyze")
        def analyze_document(req: DocumentRequest):
            result = analyze(req.text, model, tokenizer, req.max_tokens)
            return {"success": True, "analysis": result}

        @app.get("/health")
        def health():
            return {"status": "ok"}

        print(f"Nsuzumira API demarree sur http://localhost:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)

    except ImportError:
        print("Installez fastapi et uvicorn: pip install fastapi uvicorn")


def main():
    parser = argparse.ArgumentParser(description="Nsuzumira - Inference")
    parser.add_argument("--text", type=str, help="Texte du document a analyser")
    parser.add_argument("--file", type=str, help="Fichier texte a analyser")
    parser.add_argument("--model_path", type=str, default=None)
    parser.add_argument("--mode", choices=["cli", "api"], default="cli")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--hf_token", default=os.environ.get("HF_TOKEN", ""))
    args = parser.parse_args()

    if args.mode == "api":
        run_api_server(args.model_path, args.port)
        return

    # Mode CLI
    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()

    if not text:
        print("Fournissez --text ou --file")
        return

    model, tokenizer = load_nsuzumira(args.model_path, args.hf_token)
    result = analyze(text, model, tokenizer)

    print("\n=== Analyse Nsuzumira ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
