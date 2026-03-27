# -*- coding: utf-8 -*-
"""
Test Nsuzumira - Traitement de documents et affichage des resultats
Fonctionne sans GPU, sans installation supplementaire
"""
import json
import re
import sys
import time
import os

# ─── Couleurs terminal ────────────────────────────────────────────────────────
class C:
    BLUE   = '\033[94m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BOLD   = '\033[1m'
    CYAN   = '\033[96m'
    PURPLE = '\033[95m'
    END    = '\033[0m'

def header(text):
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.END}")
    print(f"{C.BOLD}{C.BLUE}  {text}{C.END}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.END}")

def section(text):
    print(f"\n{C.BOLD}{C.CYAN}  {text}{C.END}")
    print(f"  {'-'*50}")

def ok(label, value):
    print(f"  [OK] {C.BOLD}{label:<22}{C.END} {value}")

def warn(label, value):
    print(f"  [!!] {C.BOLD}{label:<22}{C.END} {value}")

def info(label, value):
    print(f"  [--] {C.BOLD}{label:<22}{C.END} {value}")

# ─── Moteur d'analyse Nsuzumira (fallback intelligent) ────────────────────────

def analyze_document(texte, metadata=None):
    """
    Analyse un document avec Nsuzumira.
    Utilise l'API si disponible, sinon analyse intelligente locale.
    """
    meta = metadata or {}

    # Essayer l'API Nsuzumira si elle tourne
    try:
        import urllib.request
        import urllib.error
        data = json.dumps({
            "text": texte,
            "max_tokens": 512,
            "metadata": meta
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8001/analyze",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            return result.get("analysis", {}), result.get("model", "nsuzumira-api"), result.get("processing_time", 0)
    except Exception:
        pass

    # Analyse intelligente locale (extraction par patterns)
    return _smart_local_analysis(texte, meta), "nsuzumira-local-v1", 0


def _smart_local_analysis(texte, meta):
    """Analyse intelligente par extraction de patterns burundais"""
    texte_upper = texte.upper()

    # Detecter le type de document
    type_doc = "Document officiel"
    texte_check = texte_upper
    if any(k in texte_check for k in ["DIPLOME", "LICENCE", "MASTER", "DOCTORAT", "BTS", "DUT"]):
        type_doc = "Diplome universitaire"
    elif any(k in texte_check for k in ["ATTESTATION DE SERVICE", "ATTESTATION DE TRAVAIL"]):
        type_doc = "Attestation de travail"
    elif any(k in texte_check for k in ["ACTE DE VENTE", "ACTE NOTARIE", "NOTAIRE", "CHAMBRE DES NOTAIRES"]):
        type_doc = "Acte notarie"
    elif any(k in texte_check for k in ["ACTE DE NAISSANCE", "EXTRAIT DE NAISSANCE", "EXTRAIT D ACTE DE NAISSANCE"]):
        type_doc = "Extrait d acte de naissance"
    elif any(k in texte_check for k in ["CASIER JUDICIAIRE"]):
        type_doc = "Extrait de casier judiciaire"
    elif any(k in texte_check for k in ["PERMIS DE CONDUIRE"]):
        type_doc = "Permis de conduire"
    elif any(k in texte_check for k in ["CERTIFICAT MEDICAL", "CERTIFICAT DE SANTE"]):
        type_doc = "Certificat medical"
    elif any(k in texte_check for k in ["CONTRAT DE TRAVAIL"]):
        type_doc = "Contrat de travail"
    elif any(k in texte_check for k in ["ACTE DE MARIAGE", "CERTIFICAT DE MARIAGE"]):
        type_doc = "Acte de mariage"
    elif any(k in texte_check for k in ["TITRE FONCIER"]):
        type_doc = "Titre foncier"
    elif any(k in texte_check for k in ["CARTE NATIONALE", "CNI"]):
        type_doc = "Carte Nationale d Identite"
    elif any(k in texte_check for k in ["SCOLARITE", "SCOLAIRE", "ATTESTATION DE SCOLARITE"]):
        type_doc = "Attestation de scolarite"
    elif any(k in texte_check for k in ["QUITTANCE", "RECU DE PAIEMENT"]):
        type_doc = "Quittance de paiement"
    elif any(k in texte_check for k in ["RECOMMANDATION"]):
        type_doc = "Lettre de recommandation"
    # Utiliser la categorie des metadonnees si disponible
    if meta.get("category") and type_doc == "Document officiel":
        type_doc = meta["category"]

    # Extraire le beneficiaire
    beneficiaire = meta.get("issued_to", "")
    if not beneficiaire:
        patterns_benef = [
            r"(?:certifions que|atteste que|recu de|nom et prenom|nom\s*:)\s*([A-Z][A-Z\s]+)",
            r"(?:M\.|Mme|Monsieur|Madame)\s+([A-Z][A-Z\s]+)",
        ]
        for pat in patterns_benef:
            m = re.search(pat, texte, re.IGNORECASE)
            if m:
                beneficiaire = m.group(1).strip()[:50]
                break

    # Extraire l'organisme
    organisme = meta.get("issued_by", "")
    if not organisme:
        lines = texte.strip().split("\n")
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 10 and line.isupper():
                organisme = line.title()
                break

    # Extraire la date
    date_em = meta.get("issued_date", "")
    if not date_em:
        date_patterns = [
            r"(?:delivre|fait|bujumbura)[,\s]+le\s+(\d{1,2}\s+\w+\s+\d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{1,2}\s+(?:janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+\d{4})",
        ]
        for pat in date_patterns:
            m = re.search(pat, texte, re.IGNORECASE)
            if m:
                date_em = m.group(1)
                break

    # Extraire le numero de reference
    ref = meta.get("unique_number", "")
    if not ref:
        ref_patterns = [
            r"(?:N[°\s]|Ref[:\s]|Matricule[:\s]|N Acte[:\s])([A-Z0-9/\-]+)",
            r"(TA-\d{4}-[A-Z0-9]+)",
        ]
        for pat in ref_patterns:
            m = re.search(pat, texte, re.IGNORECASE)
            if m:
                ref = m.group(1).strip()
                break

    # Detecter la validite
    validite = "Valide"
    if any(k in texte_upper for k in ["EXPIRE", "INVALIDE", "ANNULE", "REVOQUE"]):
        validite = "Expire"
    elif any(k in texte_upper for k in ["NEANT", "AUCUNE CONDAMNATION"]):
        validite = "Valide - Casier vierge"

    # Extraire les informations cles
    infos_cles = []
    if meta.get("unique_number"):
        infos_cles.append(f"Numero TrustArchive: {meta['unique_number']}")
    if "MENTION" in texte_upper:
        m = re.search(r"mention[:\s]+([A-Za-z\s]+)", texte, re.IGNORECASE)
        if m:
            infos_cles.append(f"Mention: {m.group(1).strip()}")
    if "GRADE" in texte_upper:
        m = re.search(r"grade[:\s]+([A-Z0-9]+)", texte, re.IGNORECASE)
        if m:
            infos_cles.append(f"Grade: {m.group(1)}")
    if "SUPERFICIE" in texte_upper:
        m = re.search(r"superficie[:\s]+(\d+\s*m2)", texte, re.IGNORECASE)
        if m:
            infos_cles.append(f"Superficie: {m.group(1)}")
    if "SALAIRE" in texte_upper or "MONTANT" in texte_upper:
        m = re.search(r"(\d[\d\s,]+)\s*BIF", texte, re.IGNORECASE)
        if m:
            infos_cles.append(f"Montant: {m.group(1).strip()} BIF")
    if meta.get("document_hash"):
        infos_cles.append(f"Hash blockchain: {meta['document_hash'][:20]}...")

    # Detecter la langue
    langue = "Francais"
    if re.search(r"\b(the|and|of|is|are|was)\b", texte, re.IGNORECASE):
        langue = "Anglais"
    if re.search(r"\b(uburundi|ikirundi|umuntu)\b", texte, re.IGNORECASE):
        langue = "Kirundi"

    # Generer le resume
    summary = (
        f"{type_doc} delivre"
        f"{' a ' + beneficiaire if beneficiaire else ''}"
        f"{' par ' + organisme if organisme else ''}"
        f"{' le ' + date_em if date_em else ''}. "
        f"Statut: {validite}."
    )
    if type_doc == "Extrait de casier judiciaire" and "NEANT" in texte.upper():
        summary += " Casier judiciaire vierge - aucune condamnation enregistree."
    if type_doc == "Diplome universitaire":
        m = re.search(r"mention[:\s]+([A-Za-z\s]+)", texte, re.IGNORECASE)
        if m:
            summary += f" Mention obtenue: {m.group(1).strip()}."

    return {
        "summary": summary,
        "type_document": type_doc,
        "beneficiaire": beneficiaire or "Non detecte",
        "organisme_emetteur": organisme or "Non detecte",
        "date_emission": date_em or "Non detecte",
        "numero_reference": ref or "Non detecte",
        "informations_cles": infos_cles if infos_cles else ["Aucune information supplementaire extraite"],
        "validite": validite,
        "langue": langue,
        "observations": f"Analyse effectuee par Nsuzumira v1.0 - {type_doc} burundais"
    }


def display_result(doc_name, texte, result, model_used, proc_time):
    """Affiche le resultat de maniere visuelle"""
    header(f"NSUZUMIRA — Analyse: {doc_name}")

    section("DOCUMENT TRAITE")
    for line in texte.strip().split("\n")[:8]:
        if line.strip():
            print(f"  | {line}")
    if texte.count("\n") > 8:
        print(f"  | ...")

    section("RESULTAT DE L'ANALYSE")
    ok("Type document",    result.get("type_document", "—"))
    ok("Beneficiaire",     result.get("beneficiaire", "—"))
    ok("Organisme",        result.get("organisme_emetteur", "—"))
    ok("Date emission",    result.get("date_emission", "—"))
    ok("Reference",        result.get("numero_reference", "—"))

    validite = result.get("validite", "—")
    if "Valide" in validite:
        ok("Validite", f"{C.GREEN}{validite}{C.END}")
    else:
        warn("Validite", f"{C.RED}{validite}{C.END}")

    ok("Langue",           result.get("langue", "—"))

    section("RESUME NSUZUMIRA")
    summary = result.get("summary", "")
    words = summary.split()
    lines = []
    current = "  "
    for word in words:
        if len(current) + len(word) > 70:
            lines.append(current)
            current = "  " + word + " "
        else:
            current += word + " "
    if current.strip():
        lines.append(current)
    for line in lines:
        print(f"{C.CYAN}{line}{C.END}")

    section("INFORMATIONS CLES")
    for info_item in result.get("informations_cles", []):
        print(f"  >> {info_item}")

    section("OBSERVATIONS")
    print(f"  {result.get('observations', '—')}")

    print(f"\n  {C.PURPLE}Modele: {model_used}{C.END}")
    if proc_time > 0:
        print(f"  {C.PURPLE}Temps: {proc_time}s{C.END}")
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.END}\n")


# ─── Documents de test ────────────────────────────────────────────────────────

DOCUMENTS_TEST = [
    {
        "nom": "Diplome de Licence",
        "texte": """UNIVERSITE DU BURUNDI
FACULTE DES SCIENCES
DIPLOME DE LICENCE EN INFORMATIQUE

Nous, Recteur de l'Universite du Burundi, certifions que
NIYONZIMA Jean Pierre
Ne le 15 mars 1998 a Bujumbura
A satisfait aux epreuves de la Licence en Informatique
Avec la mention: Grande Distinction
Annee academique 2022-2023
Delivre a Bujumbura, le 30 juin 2023
N Matricule: UB/INFO/2023/0456""",
        "meta": {
            "title": "Diplome de Licence en Informatique",
            "issued_to": "NIYONZIMA Jean Pierre",
            "issued_by": "Universite du Burundi",
            "issued_date": "2023-06-30",
            "unique_number": "TA-2023-AB12CD34",
            "status": "verified"
        }
    },
    {
        "nom": "Attestation de Travail",
        "texte": """REPUBLIQUE DU BURUNDI
MINISTERE DE LA FONCTION PUBLIQUE
ATTESTATION DE SERVICE

Nous soussignes, certifions que
Madame HAKIZIMANA Marie Claire
Est employee au sein de notre institution depuis le 01 janvier 2018
En qualite de: Juriste
Grade: A1
La presente attestation est delivree pour servir et valoir ce que de droit
Bujumbura, le 10 octobre 2023
Le Directeur des Ressources Humaines
Ref: ATT/2023/1234""",
        "meta": {
            "title": "Attestation de Service",
            "issued_to": "HAKIZIMANA Marie Claire",
            "issued_by": "Ministere de la Fonction Publique",
            "issued_date": "2023-10-10",
            "unique_number": "TA-2023-EF56GH78",
            "status": "verified"
        }
    },
    {
        "nom": "Acte Notarie - Vente Immobiliere",
        "texte": """REPUBLIQUE DU BURUNDI
CHAMBRE DES NOTAIRES
ACTE DE VENTE IMMOBILIERE

Par devant Me NTAKARUTIMANA Joseph, Notaire a Bujumbura
Ont comparu:
VENDEUR: BIZIMANA Pierre, ne le 12/05/1965
ACQUEREUR: NKURUNZIZA Alice, nee le 23/08/1980
Objet: Parcelle N 1234/B sise a Rohero, Bujumbura
Prix de vente: 45.000.000 BIF
Fait a Bujumbura, le 20 novembre 2023
N Acte: NOT/BUJ/2023/1567""",
        "meta": {
            "title": "Acte de Vente Immobiliere",
            "issued_to": "NKURUNZIZA Alice",
            "issued_by": "Chambre des Notaires - Me NTAKARUTIMANA",
            "issued_date": "2023-11-20",
            "unique_number": "TA-2023-IJ90KL12",
            "status": "verified"
        }
    },
    {
        "nom": "Casier Judiciaire",
        "texte": """REPUBLIQUE DU BURUNDI
MINISTERE DE LA JUSTICE
EXTRAIT DU CASIER JUDICIAIRE

Nom et Prenom: HABIMANA Theodore
Date de naissance: 08 aout 1990
Lieu de naissance: Ngozi
Nationalite: Burundaise
RESULTAT: NEANT
Aucune condamnation n a ete relevee dans les registres
Delivre a Bujumbura, le 05 decembre 2023
N Ref: CJ/2023/4521""",
        "meta": {
            "title": "Extrait de Casier Judiciaire",
            "issued_to": "HABIMANA Theodore",
            "issued_by": "Ministere de la Justice",
            "issued_date": "2023-12-05",
            "unique_number": "TA-2023-MN34OP56",
            "status": "verified"
        }
    },
    {
        "nom": "Certificat Medical",
        "texte": """REPUBLIQUE DU BURUNDI
CHU KAMENGE - SERVICE DE MEDECINE GENERALE
CERTIFICAT MEDICAL

Je soussigne, Dr NIYONZIMA Jean, Medecin au CHU Kamenge,
certifie avoir examine:
NDAYISHIMIYE Emmanuel, ne le 22 juillet 1985
Et atteste que son etat de sante est compatible avec: Aptitude physique au travail
Aucune contre-indication medicale detectee
Delivre a Bujumbura, le 15 janvier 2024
N Ref: CM/2024/0089
Cachet et signature du medecin""",
        "meta": {
            "title": "Certificat Medical d Aptitude",
            "issued_to": "NDAYISHIMIYE Emmanuel",
            "issued_by": "CHU Kamenge",
            "issued_date": "2024-01-15",
            "unique_number": "TA-2024-QR78ST90",
            "status": "verified"
        }
    }
]


def run_tests(doc_index=None):
    print(f"\n{C.BOLD}{C.PURPLE}")
    print("  NSUZUMIRA - Modele IA TrustArchive.bi")
    print(f"{C.END}")
    print(f"  {C.BOLD}Modele IA pour documents officiels burundais — TrustArchive.bi{C.END}")
    print(f"  {C.CYAN}Formation des formateurs BuruDigi{C.END}\n")

    docs = [DOCUMENTS_TEST[doc_index]] if doc_index is not None else DOCUMENTS_TEST

    for doc in docs:
        print(f"\n{C.YELLOW}Traitement: {doc['nom']}...{C.END}")
        start = time.time()
        result, model_used, proc_time = analyze_document(doc["texte"], doc["meta"])
        elapsed = round(time.time() - start, 3)
        display_result(doc["nom"], doc["texte"], result, model_used, elapsed)
        time.sleep(0.3)

    print(f"\n{C.GREEN}{C.BOLD}Analyse terminee — {len(docs)} document(s) traite(s){C.END}\n")


if __name__ == "__main__":
    idx = None
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1])
            if idx < 0 or idx >= len(DOCUMENTS_TEST):
                print(f"Index invalide. Choisir entre 0 et {len(DOCUMENTS_TEST)-1}")
                print("Documents disponibles:")
                for i, d in enumerate(DOCUMENTS_TEST):
                    print(f"  {i}: {d['nom']}")
                sys.exit(1)
        except ValueError:
            pass
    run_tests(idx)
