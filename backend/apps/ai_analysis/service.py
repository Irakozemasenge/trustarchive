"""
Service Nsuzumira pour TrustArchive.bi
Priorité: 1) Nsuzumira local  2) Nsuzumira API  3) Gemma via Google AI  4) Fallback
"""
import os
import re
import json
import logging
import base64
from django.conf import settings

logger = logging.getLogger(__name__)

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
    """Extrait le texte d'un fichier via OCR"""
    try:
        import pytesseract
        from PIL import Image

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            try:
                from pdf2image import convert_from_path
                pages = convert_from_path(file_path, dpi=200)
                return "\n".join(
                    pytesseract.image_to_string(p, lang='fra+eng') for p in pages
                ).strip()
            except Exception:
                return ""
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return pytesseract.image_to_string(Image.open(file_path), lang='fra+eng').strip()
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"OCR error: {e}")
    return ""


def _parse_json_response(raw_text):
    """Extrait le JSON d'une réponse texte"""
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None


def _call_nsuzumira_api(prompt):
    """Appelle Nsuzumira via son API locale (FastAPI sur port 8001)"""
    import requests
    nsuzumira_url = getattr(settings, 'NSUZUMIRA_API_URL',
                            os.environ.get('NSUZUMIRA_API_URL', 'http://localhost:8001'))
    try:
        resp = requests.post(
            f"{nsuzumira_url}/analyze",
            json={"text": prompt, "max_tokens": 512},
            timeout=60
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('analysis', {}), 0
    except Exception as e:
        logger.warning(f"Nsuzumira API non disponible: {e}")
    return None, 0


def _call_gemma_google(prompt, document):
    """Appelle Gemma via Google AI Studio"""
    api_key = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY', ''))
    if not api_key:
        return None, 0
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemma-3-27b-it')

        content = [prompt]
        if document.document_file:
            try:
                from PIL import Image as PILImage
                ext = os.path.splitext(document.document_file.path)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png']:
                    content.append(PILImage.open(document.document_file.path))
            except Exception:
                pass

        response = model.generate_content(
            content,
            generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=1024)
        )
        tokens = getattr(response.usage_metadata, 'total_token_count', 0)
        return _parse_json_response(response.text), tokens
    except Exception as e:
        logger.warning(f"Google AI error: {e}")
    return None, 0


def analyze_document_with_gemma(document):
    """
    Pipeline d'analyse:
    1. Nsuzumira API locale
    2. Google AI (Gemma)
    3. Fallback structuré
    """
    # Extraction OCR
    extracted_text = ""
    if document.document_file:
        try:
            extracted_text = extract_text_from_file(document.document_file.path)
        except Exception:
            pass

    # Construire le prompt
    prompt = PROMPT_TEMPLATE.format(
        title=document.title,
        category=document.category.name if document.category else 'Non definie',
        issued_to=document.issued_to,
        issued_date=document.issued_date,
        issued_by=document.issued_by.organization_name if document.issued_by else 'Inconnu',
        texte=extracted_text or "(Texte non extrait - analyse basee sur les metadonnees)"
    )

    # 1. Essayer Nsuzumira API locale
    result, tokens = _call_nsuzumira_api(prompt)
    model_used = 'nsuzumira-local'

    # 2. Essayer Google AI
    if result is None:
        result, tokens = _call_gemma_google(prompt, document)
        model_used = 'gemma-3-27b-it'

    # 3. Fallback
    if result is None:
        result, tokens = _fallback_analysis(document), 0
        model_used = 'fallback'

    summary = result.pop('summary', f"Document {document.title} delivre a {document.issued_to}")
    result['model_used'] = model_used

    return summary, result, extracted_text, tokens


def _fallback_analysis(document):
    return {
        'type_document': document.category.name if document.category else 'Non defini',
        'beneficiaire': document.issued_to,
        'organisme_emetteur': document.issued_by.organization_name if document.issued_by else '',
        'date_emission': str(document.issued_date),
        'date_expiration': str(document.expiry_date) if document.expiry_date else 'Non definie',
        'numero_reference': document.unique_number,
        'validite': 'Valide' if document.status == 'verified' else document.status,
        'informations_cles': [
            f"Numero unique: {document.unique_number}",
            f"Hash blockchain: {document.document_hash[:20]}...",
            f"Statut: {document.get_status_display()}",
        ],
        'langue': 'Français',
        'observations': 'Analyse generee automatiquement — configurez GEMINI_API_KEY ou lancez Nsuzumira API',
    }
