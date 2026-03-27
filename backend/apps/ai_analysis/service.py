# -*- coding: utf-8 -*-
"""
Service Nsuzumira pour TrustArchive.bi
Pipeline: 1) Nsuzumira LLM API  2) Google Gemma AI  3) Fallback
"""
import os
import re
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """<start_of_turn>user
Tu es Nsuzumira, un assistant IA specialise dans l analyse de documents officiels burundais.
Analyse le document suivant et fournis une reponse JSON structuree.

Informations connues:
- Titre: {title}
- Categorie: {category}
- Delivre a: {issued_to}
- Date emission: {issued_date}
- Emis par: {issued_by}

DOCUMENT:
{texte}
<end_of_turn>
<start_of_turn>model
"""


def extract_text_from_file(file_path):
    try:
        import pytesseract
        from PIL import Image
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            try:
                from pdf2image import convert_from_path
                pages = convert_from_path(file_path, dpi=200)
                return "\n".join(pytesseract.image_to_string(p, lang="fra+eng") for p in pages).strip()
            except Exception:
                return ""
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return pytesseract.image_to_string(Image.open(file_path), lang="fra+eng").strip()
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"OCR error: {e}")
    return ""


def _call_nsuzumira_api(text, metadata=None):
    """Appelle l API Nsuzumira LLM"""
    import requests
    url = getattr(settings, "NSUZUMIRA_API_URL", os.environ.get("NSUZUMIRA_API_URL", "http://localhost:8001"))
    try:
        resp = requests.post(
            f"{url}/analyze",
            json={"text": text, "max_tokens": 512, "temperature": 0.2, "metadata": metadata or {}},
            timeout=120
        )
        if resp.status_code == 200:
            data = resp.json()
            analysis = data.get("analysis", {})
            tokens = data.get("tokens_used", 0)
            model_used = data.get("model", "nsuzumira")
            return analysis, tokens, model_used
    except Exception as e:
        logger.warning(f"Nsuzumira API non disponible: {e}")
    return None, 0, None


def _call_google_gemma(prompt, document):
    """Fallback: Google AI Studio"""
    api_key = getattr(settings, "GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        return None, 0
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemma-3-27b-it")
        content = [prompt]
        if document.document_file:
            try:
                from PIL import Image as PILImage
                ext = os.path.splitext(document.document_file.path)[1].lower()
                if ext in [".jpg", ".jpeg", ".png"]:
                    content.append(PILImage.open(document.document_file.path))
            except Exception:
                pass
        response = model.generate_content(content, generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=1024))
        tokens = getattr(response.usage_metadata, "total_token_count", 0)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group()), tokens
            except Exception:
                pass
        return {"summary": response.text[:300]}, tokens
    except Exception as e:
        logger.warning(f"Google AI error: {e}")
    return None, 0


def _fallback(document):
    return {
        "type_document": document.category.name if document.category else "Non defini",
        "beneficiaire": document.issued_to,
        "organisme_emetteur": document.issued_by.organization_name if document.issued_by else "",
        "date_emission": str(document.issued_date),
        "date_expiration": str(document.expiry_date) if document.expiry_date else "Non definie",
        "numero_reference": document.unique_number,
        "validite": "Valide" if document.status == "verified" else document.status,
        "informations_cles": [
            f"Numero unique: {document.unique_number}",
            f"Hash blockchain: {document.document_hash[:20]}...",
            f"Statut: {document.get_status_display()}",
        ],
        "langue": "Francais",
        "observations": "Analyse fallback - lancez Nsuzumira API ou configurez GEMINI_API_KEY",
    }


def analyze_document_with_gemma(document):
    extracted_text = ""
    if document.document_file:
        try:
            extracted_text = extract_text_from_file(document.document_file.path)
        except Exception:
            pass

    metadata = {
        "title": document.title,
        "category": document.category.name if document.category else "",
        "issued_to": document.issued_to,
        "issued_date": str(document.issued_date),
        "issued_by": document.issued_by.organization_name if document.issued_by else "",
        "unique_number": document.unique_number,
        "status": document.status,
    }

    # 1. Nsuzumira LLM API
    result, tokens, model_used = _call_nsuzumira_api(
        extracted_text or f"Document: {document.title}. Delivre a: {document.issued_to}.",
        metadata
    )

    # 2. Google Gemma
    if result is None:
        prompt = PROMPT_TEMPLATE.format(
            title=document.title,
            category=metadata["category"],
            issued_to=document.issued_to,
            issued_date=document.issued_date,
            issued_by=metadata["issued_by"],
            texte=extracted_text or "(Texte non extrait)"
        )
        result, tokens = _call_google_gemma(prompt, document)
        model_used = "gemma-3-27b-it"

    # 3. Fallback
    if result is None:
        result = _fallback(document)
        tokens = 0
        model_used = "fallback"

    summary = result.pop("summary", f"Document {document.title} delivre a {document.issued_to}.")
    result["model_used"] = model_used
    return summary, result, extracted_text, tokens
