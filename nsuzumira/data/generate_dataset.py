# -*- coding: utf-8 -*-
"""
Generateur de dataset Nsuzumira - 10000+ exemples
Documents officiels burundais: diplomes, actes, attestations, certificats...
"""
import json
import random
import os

# --- Données de base burundaises --------------------------------------------

NOMS = [
    "NIYONZIMA","HAKIZIMANA","NDAYISHIMIYE","BIZIMANA","NKURUNZIZA","IRAKOZE",
    "HABIMANA","NTAKARUTIMANA","NIYONGABO","NSHIMIRIMANA","HAVYARIMANA","NZEYIMANA",
    "BARAKAMFITIYE","NIYONKURU","NKURUNZIZA","SINDAYIGAYA","NTIRANDEKURA","NIYOMUGABO",
    "BIGIRIMANA","NKESHIMANA","NIYONSENGA","NZABAHIMANA","NKURUNZIZA","NIYONKURU",
    "NSHIMIRIMANA","NIYOMUGABO","BARAKAMFITIYE","NTAKARUTIMANA","HAVYARIMANA","NZEYIMANA",
    "KAYITESI","UWIMANA","MUKAMANA","UWASE","INGABIRE","UWINEZA","UWERA","MUKESHIMANA",
    "NIYIBIZI","UWIMANA","GASANA","MURENZI","HABIMANA","NKURUNZIZA","NIYONZIMA",
    "NDIKUMANA","NSHIMIRIMANA","NIYONGABO","BIGIRIMANA","NKESHIMANA"
]

PRENOMS_M = [
    "Jean","Pierre","Emmanuel","Joseph","Patrick","Christian","Eric","Olivier",
    "Thierry","Fabrice","Cedric","Didier","Alain","Bruno","Claude","Denis",
    "Francois","Gerard","Henri","Innocent","Jacques","Kevin","Laurent","Michel",
    "Nicolas","Oscar","Paul","Quentin","Robert","Samuel","Thomas","Urbain",
    "Victor","William","Xavier","Yves","Zacharie","Alexis","Bernard","Charles"
]

PRENOMS_F = [
    "Marie","Alice","Sandrine","Christine","Beatrice","Claudine","Denise","Esperance",
    "Francoise","Grace","Helene","Immaculee","Jocelyne","Karine","Laetitia","Martine",
    "Nadine","Odette","Patricia","Rachel","Solange","Therese","Ursule","Valerie",
    "Wivine","Xaverie","Yvonne","Zoe","Aline","Brigitte","Cecile","Diane"
]

VILLES = [
    "Bujumbura","Gitega","Ngozi","Rumonge","Bururi","Kayanza","Muyinga","Kirundo",
    "Makamba","Rutana","Ruyigi","Cankuzo","Karuzi","Muramvya","Bubanza","Cibitoke",
    "Bujumbura Rural","Mwaro","Isale","Kiganda","Gihanga","Mutimbuzi","Kabezi"
]

UNIVERSITES = [
    "Universite du Burundi","Universite Lumiere de Bujumbura","Universite Hope Africa",
    "Universite Polytechnique de Gitega","Universite Sagesse d Afrique",
    "Institut Superieur de Gestion des Entreprises","Universite Adventiste de Lukanga",
    "Universite Catholique de Bujumbura","Ecole Normale Superieure","ISCO Bujumbura"
]

FACULTES = [
    "Faculte des Sciences","Faculte de Droit","Faculte de Medecine",
    "Faculte des Lettres et Sciences Humaines","Faculte des Sciences Economiques",
    "Faculte d Informatique","Faculte d Agronomie","Faculte de Pedagogie",
    "Faculte de Theologie","Ecole Polytechnique","Institut de Gestion"
]

FILIERES = [
    "Informatique","Droit","Medecine","Economie","Gestion","Agronomie",
    "Pedagogie","Lettres Modernes","Sciences Biologiques","Chimie","Physique",
    "Mathematiques","Geographie","Histoire","Sociologie","Psychologie",
    "Comptabilite","Finance","Marketing","Ressources Humaines","Audit",
    "Genie Civil","Genie Electrique","Architecture","Pharmacie","Dentisterie"
]

MENTIONS = ["Tres Grande Distinction","Grande Distinction","Distinction","Satisfaction","Passable"]

MINISTERES = [
    "Ministere de la Fonction Publique","Ministere de l Education Nationale",
    "Ministere de la Sante Publique","Ministere des Finances",
    "Ministere de la Justice","Ministere de l Interieur",
    "Ministere des Travaux Publics","Ministere de l Agriculture",
    "Ministere du Commerce","Ministere des Transports",
    "Ministere de la Defense Nationale","Ministere des Affaires Etrangeres"
]

ENTREPRISES = [
    "Banque de la Republique du Burundi","REGIDESO","ONATEL","SOSUMO",
    "Brarudi","Interpetrol","Bancobu","BCB","Ecobank Burundi",
    "Societe Sucriere du Moso","Office du The du Burundi","OTRACO",
    "Societe Nationale d Assurances","COTEBU","VERRUNDI"
]

POSTES = [
    "Ingenieur Informaticien","Medecin","Juriste","Economiste","Comptable",
    "Enseignant","Infirmier","Technicien","Administrateur","Directeur",
    "Chef de Service","Secretaire","Caissier","Agent de Securite","Chauffeur",
    "Ingenieur Civil","Pharmacien","Agronome","Sociologue","Psychologue"
]

GRADES = ["A1","A2","B1","B2","C1","C2","D1","D2"]

NOTAIRES = [
    "Me NTAKARUTIMANA Joseph","Me NIYONZIMA Jean Pierre","Me HAKIZIMANA Marie",
    "Me NDAYISHIMIYE Emmanuel","Me BIZIMANA Pierre","Me NKURUNZIZA Alice",
    "Me HABIMANA Theodose","Me NIYONGABO Patrick","Me BIGIRIMANA Christian"
]

PROMPT_TEMPLATE = """<start_of_turn>user
Tu es Nsuzumira, un assistant IA specialise dans l analyse de documents officiels burundais.
Analyse le document suivant et fournis une reponse JSON structuree.

DOCUMENT:
{texte}
<end_of_turn>
<start_of_turn>model
{analyse}
<end_of_turn>"""


# --- Générateurs de documents ------------------------------------------------

def rand_date(y_start=1990, y_end=2005):
    j = random.randint(1,28); m = random.randint(1,12); y = random.randint(y_start,y_end)
    return f"{j:02d}/{m:02d}/{y}"

def rand_emit_date(y_start=2018, y_end=2024):
    j = random.randint(1,28); m = random.randint(1,12); y = random.randint(y_start,y_end)
    mois = ["janvier","fevrier","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","decembre"]
    return f"{j} {mois[m-1]} {y}"

def rand_person(genre=None):
    if genre is None: genre = random.choice(["M","F"])
    nom = random.choice(NOMS)
    prenom = random.choice(PRENOMS_M if genre=="M" else PRENOMS_F)
    return nom, prenom, genre

def rand_ref(prefix, year=None):
    if year is None: year = random.randint(2018,2024)
    return f"{prefix}/{year}/{random.randint(1000,9999)}"

def make_analyse(type_doc, beneficiaire, organisme, date_em, ref, infos, validite="Valide", obs=""):
    return {
        "summary": f"{type_doc} delivre a {beneficiaire} par {organisme} le {date_em}.",
        "type_document": type_doc,
        "beneficiaire": beneficiaire,
        "organisme_emetteur": organisme,
        "date_emission": date_em,
        "numero_reference": ref,
        "informations_cles": infos,
        "validite": validite,
        "langue": "Francais",
        "observations": obs or "Document officiel authentique"
    }

# --- 1. DIPLOMES UNIVERSITAIRES ----------------------------------------------

def gen_diplome():
    nom, prenom, genre = rand_person()
    univ = random.choice(UNIVERSITES)
    fac = random.choice(FACULTES)
    filiere = random.choice(FILIERES)
    mention = random.choice(MENTIONS)
    naissance = rand_date(1985,2002)
    ville_naiss = random.choice(VILLES)
    annee = random.randint(2015,2024)
    date_em = rand_emit_date(annee, annee)
    matricule = rand_ref("MAT", annee)
    niveau = random.choice(["Licence","Master","Doctorat","Baccalaureat","BTS","DUT"])
    titre = "M." if genre=="M" else "Mme"

    texte = f"""{univ.upper()}
{fac.upper()}
DIPLOME DE {niveau.upper()} EN {filiere.upper()}

Nous, Recteur de {univ}, certifions que
{titre} {nom} {prenom}
Ne(e) le {naissance} a {ville_naiss}
A satisfait aux epreuves du {niveau} en {filiere}
Avec la mention: {mention}
Annee academique {annee-1}-{annee}
Delivre a Bujumbura, le {date_em}
N Matricule: {matricule}"""

    analyse = make_analyse(
        f"Diplome de {niveau} en {filiere}",
        f"{nom} {prenom}",
        univ,
        date_em,
        matricule,
        [f"{niveau} en {filiere}", f"Mention: {mention}", f"Ne(e) le {naissance} a {ville_naiss}", f"Annee: {annee-1}-{annee}"]
    )
    return texte, analyse

# --- 2. ATTESTATIONS DE TRAVAIL ----------------------------------------------

def gen_attestation_travail():
    nom, prenom, genre = rand_person()
    org = random.choice(MINISTERES + ENTREPRISES)
    poste = random.choice(POSTES)
    grade = random.choice(GRADES)
    annee_debut = random.randint(2005,2020)
    date_em = rand_emit_date(2022,2024)
    ref = rand_ref("ATT")
    titre = "M." if genre=="M" else "Mme"

    texte = f"""REPUBLIQUE DU BURUNDI
{org.upper()}
ATTESTATION DE SERVICE

Nous soussignes, certifions que
{titre} {nom} {prenom}
Est employe(e) au sein de notre institution depuis le 01 janvier {annee_debut}
En qualite de: {poste}
Grade: {grade}
La presente attestation est delivree pour servir et valoir ce que de droit
Bujumbura, le {date_em}
Le Directeur des Ressources Humaines
Ref: {ref}"""

    analyse = make_analyse(
        "Attestation de travail",
        f"{nom} {prenom}",
        org,
        date_em,
        ref,
        [f"Poste: {poste}", f"Grade: {grade}", f"En service depuis: 01/01/{annee_debut}"]
    )
    return texte, analyse

# --- 3. ACTES NOTARIES -------------------------------------------------------

def gen_acte_notarie():
    nom1, prenom1, _ = rand_person()
    nom2, prenom2, _ = rand_person()
    notaire = random.choice(NOTAIRES)
    ville = random.choice(VILLES)
    parcelle = f"{random.randint(100,9999)}/{random.choice(['A','B','C','D'])}"
    prix = random.randint(5,500) * 1000000
    date_em = rand_emit_date(2020,2024)
    ref = rand_ref("NOT/BUJ")
    type_acte = random.choice(["Vente Immobiliere","Donation","Succession","Bail Commercial","Hypotheque","Partage"])

    texte = f"""REPUBLIQUE DU BURUNDI
CHAMBRE DES NOTAIRES
ACTE DE {type_acte.upper()}

Par devant {notaire}, Notaire a Bujumbura
Ont comparu:
VENDEUR/CEDANT: {nom1} {prenom1}
ACQUEREUR/BENEFICIAIRE: {nom2} {prenom2}
Objet: Parcelle N {parcelle} sise a {ville}
Valeur: {prix:,} BIF
Fait a Bujumbura, le {date_em}
N Acte: {ref}"""

    analyse = make_analyse(
        f"Acte notarie - {type_acte}",
        f"{nom2} {prenom2}",
        f"Chambre des Notaires - {notaire}",
        date_em,
        ref,
        [f"Parcelle N {parcelle} a {ville}", f"Valeur: {prix:,} BIF", f"Cedant: {nom1} {prenom1}"]
    )
    return texte, analyse

# --- 4. CERTIFICATS DE NAISSANCE ---------------------------------------------

def gen_naissance():
    nom, prenom, genre = rand_person()
    nom_pere, prenom_pere, _ = rand_person("M")
    nom_mere, prenom_mere, _ = rand_person("F")
    naissance = rand_date(1980,2023)
    ville = random.choice(VILLES)
    hopitaux = ["Hopital Prince Regent Charles","CHU Kamenge","Hopital Militaire","Clinique Prince Louis Rwagasore","Hopital de Gitega","Maternite de Ngozi"]
    hopital = random.choice(hopitaux)
    date_em = rand_emit_date(2018,2024)
    ref = rand_ref("NAISS/BUJ")
    commune = random.choice(["Commune Urbaine de Bujumbura","Commune de Gitega","Commune de Ngozi","Mairie de Bujumbura"])

    texte = f"""REPUBLIQUE DU BURUNDI
{commune.upper()}
EXTRAIT D ACTE DE NAISSANCE

Nom: {nom}
Prenom: {prenom}
Sexe: {"Masculin" if genre=="M" else "Feminin"}
Date de naissance: {naissance}
Lieu de naissance: {hopital}, {ville}
Pere: {nom_pere} {prenom_pere}
Mere: {nom_mere} {prenom_mere}
N Acte: {ref}
Delivre le: {date_em}"""

    analyse = make_analyse(
        "Extrait d acte de naissance",
        f"{nom} {prenom}",
        commune,
        date_em,
        ref,
        [f"Ne(e) le {naissance}", f"Lieu: {hopital}, {ville}", f"Pere: {nom_pere} {prenom_pere}", f"Mere: {nom_mere} {prenom_mere}"]
    )
    return texte, analyse

# --- 5. CASIERS JUDICIAIRES ---------------------------------------------------

def gen_casier():
    nom, prenom, genre = rand_person()
    naissance = rand_date(1970,2000)
    ville = random.choice(VILLES)
    date_em = rand_emit_date(2022,2024)
    ref = rand_ref("CJ")
    resultat = random.choices(["NEANT","CONDAMNATION"], weights=[85,15])[0]
    titre = "M." if genre=="M" else "Mme"

    obs = "Casier vierge - aucune condamnation" if resultat=="NEANT" else "Condamnation enregistree - verifier details"
    texte = f"""REPUBLIQUE DU BURUNDI
MINISTERE DE LA JUSTICE
EXTRAIT DU CASIER JUDICIAIRE

Nom et Prenom: {nom} {prenom}
Date de naissance: {naissance}
Lieu de naissance: {ville}
Nationalite: Burundaise
RESULTAT: {resultat}
{"Aucune condamnation n a ete relevee dans les registres" if resultat=="NEANT" else "Une condamnation a ete enregistree"}
Delivre a Bujumbura, le {date_em}
N Ref: {ref}"""

    analyse = make_analyse(
        "Extrait de casier judiciaire",
        f"{nom} {prenom}",
        "Ministere de la Justice du Burundi",
        date_em,
        ref,
        [f"Resultat: {resultat}", f"Ne(e) le {naissance} a {ville}", "Nationalite: Burundaise"],
        validite="Valide",
        obs=obs
    )
    return texte, analyse


# --- 6. PERMIS DE CONDUIRE ----------------------------------------------------

def gen_permis():
    nom, prenom, genre = rand_person()
    naissance = rand_date(1975,2005)
    ville = random.choice(VILLES)
    categories = ["A","B","C","D","E","A+B","B+C","C+D"]
    cat = random.choice(categories)
    annee = random.randint(2015,2024)
    date_em = rand_emit_date(annee, annee)
    expiry_year = annee + 5
    ref = rand_ref("PC/BUJ", annee)

    texte = f"""REPUBLIQUE DU BURUNDI
MINISTERE DES TRANSPORTS
PERMIS DE CONDUIRE

Nom: {nom}
Prenom: {prenom}
Date de naissance: {naissance}
Lieu de naissance: {ville}
Categories autorisees: {cat}
Date de delivrance: {date_em}
Date d expiration: 31/12/{expiry_year}
N Permis: {ref}
Delivre par: Direction Nationale des Transports"""

    analyse = make_analyse(
        "Permis de conduire",
        f"{nom} {prenom}",
        "Ministere des Transports du Burundi",
        date_em,
        ref,
        [f"Categories: {cat}", f"Expire le: 31/12/{expiry_year}", f"Ne(e) le {naissance} a {ville}"],
        validite="Valide" if expiry_year >= 2024 else "Expire"
    )
    return texte, analyse

# --- 7. CERTIFICATS MEDICAUX --------------------------------------------------

def gen_certificat_medical():
    nom, prenom, genre = rand_person()
    naissance = rand_date(1970,2005)
    hopitaux = ["CHU Kamenge","Hopital Prince Regent Charles","Clinique Ngozi","Hopital Militaire de Bujumbura","Centre de Sante Rohero"]
    hopital = random.choice(hopitaux)
    medecins = ["Dr NIYONZIMA Jean","Dr HAKIZIMANA Marie","Dr NDAYISHIMIYE Paul","Dr BIZIMANA Alice","Dr HABIMANA Emmanuel"]
    medecin = random.choice(medecins)
    date_em = rand_emit_date(2022,2024)
    ref = rand_ref("CM")
    type_cert = random.choice(["Aptitude physique","Bonne sante","Vaccination","Incapacite temporaire","Conge maladie"])

    texte = f"""REPUBLIQUE DU BURUNDI
{hopital.upper()}
CERTIFICAT MEDICAL

Je soussigne, {medecin}, certifie avoir examine
{nom} {prenom}, ne(e) le {naissance}
Et atteste que l etat de sante est compatible avec: {type_cert}
Delivre a Bujumbura, le {date_em}
N Ref: {ref}
Cachet et signature du medecin"""

    analyse = make_analyse(
        f"Certificat medical - {type_cert}",
        f"{nom} {prenom}",
        hopital,
        date_em,
        ref,
        [f"Type: {type_cert}", f"Medecin: {medecin}", f"Ne(e) le {naissance}"]
    )
    return texte, analyse

# --- 8. CONTRATS DE TRAVAIL ---------------------------------------------------

def gen_contrat_travail():
    nom, prenom, genre = rand_person()
    org = random.choice(ENTREPRISES + MINISTERES)
    poste = random.choice(POSTES)
    salaire = random.randint(200,2000) * 1000
    type_contrat = random.choice(["CDI","CDD","Stage","Consultant","Temps partiel"])
    duree = "" if type_contrat=="CDI" else f"Duree: {random.randint(3,24)} mois"
    date_em = rand_emit_date(2020,2024)
    ref = rand_ref("CONT")

    texte = f"""REPUBLIQUE DU BURUNDI
{org.upper()}
CONTRAT DE TRAVAIL - {type_contrat}

Entre: {org} (Employeur)
Et: {nom} {prenom} (Employe)
Poste: {poste}
Salaire mensuel brut: {salaire:,} BIF
{duree}
Date de prise de service: {date_em}
N Contrat: {ref}
Signe a Bujumbura"""

    analyse = make_analyse(
        f"Contrat de travail - {type_contrat}",
        f"{nom} {prenom}",
        org,
        date_em,
        ref,
        [f"Poste: {poste}", f"Salaire: {salaire:,} BIF/mois", f"Type: {type_contrat}", duree]
    )
    return texte, analyse

# --- 9. CERTIFICATS DE MARIAGE ------------------------------------------------

def gen_mariage():
    nom1, prenom1, _ = rand_person("M")
    nom2, prenom2, _ = rand_person("F")
    naissance1 = rand_date(1975,2000)
    naissance2 = rand_date(1978,2003)
    ville = random.choice(VILLES)
    date_em = rand_emit_date(2015,2024)
    ref = rand_ref("MAR/BUJ")
    commune = random.choice(["Commune Urbaine de Bujumbura","Commune de Gitega","Mairie de Bujumbura"])

    texte = f"""REPUBLIQUE DU BURUNDI
{commune.upper()}
ACTE DE MARIAGE

Epoux: {nom1} {prenom1}, ne le {naissance1}
Epouse: {nom2} {prenom2}, nee le {naissance2}
Celebre a: {ville}
Date du mariage: {date_em}
N Acte: {ref}
Officier d etat civil: Le Maire de {ville}"""

    analyse = make_analyse(
        "Acte de mariage",
        f"{nom1} {prenom1} et {nom2} {prenom2}",
        commune,
        date_em,
        ref,
        [f"Epoux: {nom1} {prenom1} (ne le {naissance1})", f"Epouse: {nom2} {prenom2} (nee le {naissance2})", f"Celebre a {ville}"]
    )
    return texte, analyse

# --- 10. ATTESTATIONS SCOLAIRES -----------------------------------------------

def gen_attestation_scolaire():
    nom, prenom, genre = rand_person()
    naissance = rand_date(1995,2010)
    ecoles = ["Lycee du Saint Esprit","College du Sacre Coeur","Lycee Rohero","Ecole Primaire Centrale","College Stella Matutina","Lycee de Gitega","Ecole Secondaire de Ngozi"]
    ecole = random.choice(ecoles)
    classe = random.choice(["6eme","5eme","4eme","3eme","2eme","1ere","Terminale","CM2","CM1"])
    annee = random.randint(2015,2024)
    date_em = rand_emit_date(annee, annee)
    ref = rand_ref("SCOL", annee)

    texte = f"""REPUBLIQUE DU BURUNDI
MINISTERE DE L EDUCATION NATIONALE
{ecole.upper()}
ATTESTATION DE SCOLARITE

Nous certifions que {nom} {prenom}
Ne(e) le {naissance}
Est regulierement inscrit(e) en classe de {classe}
Annee scolaire {annee-1}-{annee}
Delivre a Bujumbura, le {date_em}
N Ref: {ref}
Le Directeur de l etablissement"""

    analyse = make_analyse(
        "Attestation de scolarite",
        f"{nom} {prenom}",
        ecole,
        date_em,
        ref,
        [f"Classe: {classe}", f"Annee: {annee-1}-{annee}", f"Ne(e) le {naissance}"]
    )
    return texte, analyse


# --- 11. TITRES FONCIERS ------------------------------------------------------

def gen_titre_foncier():
    nom, prenom, _ = rand_person()
    ville = random.choice(VILLES)
    quartiers = ["Rohero","Kinama","Cibitoke","Ngagara","Kamenge","Musaga","Buyenzi","Bwiza","Mutanga","Kiriri"]
    quartier = random.choice(quartiers)
    superficie = random.randint(200, 5000)
    parcelle = f"{random.randint(100,9999)}/{random.choice(['A','B','C','D','E'])}"
    date_em = rand_emit_date(2010,2024)
    ref = rand_ref("TF/BUJ")

    texte = f"""REPUBLIQUE DU BURUNDI
MINISTERE DE L URBANISME ET DE L HABITAT
TITRE FONCIER

Proprietaire: {nom} {prenom}
Parcelle N: {parcelle}
Quartier: {quartier}, {ville}
Superficie: {superficie} m2
Usage: Residentiel
Date d enregistrement: {date_em}
N Titre: {ref}
Conservateur des Titres Fonciers"""

    analyse = make_analyse(
        "Titre foncier",
        f"{nom} {prenom}",
        "Ministere de l Urbanisme et de l Habitat",
        date_em,
        ref,
        [f"Parcelle N {parcelle}", f"Quartier: {quartier}, {ville}", f"Superficie: {superficie} m2", "Usage: Residentiel"]
    )
    return texte, analyse

# --- 12. PASSEPORTS / CNI -----------------------------------------------------

def gen_cni():
    nom, prenom, genre = rand_person()
    naissance = rand_date(1970,2005)
    ville = random.choice(VILLES)
    annee = random.randint(2018,2024)
    date_em = rand_emit_date(annee, annee)
    expiry = annee + 10
    ref = f"BI{random.randint(1000000,9999999)}"

    texte = f"""REPUBLIQUE DU BURUNDI
CARTE NATIONALE D IDENTITE

Nom: {nom}
Prenom: {prenom}
Sexe: {"M" if genre=="M" else "F"}
Date de naissance: {naissance}
Lieu de naissance: {ville}
Nationalite: Burundaise
N CNI: {ref}
Date de delivrance: {date_em}
Date d expiration: 31/12/{expiry}
Delivree par: Direction Generale de l Immigration"""

    analyse = make_analyse(
        "Carte Nationale d Identite",
        f"{nom} {prenom}",
        "Direction Generale de l Immigration - Burundi",
        date_em,
        ref,
        [f"N CNI: {ref}", f"Ne(e) le {naissance} a {ville}", f"Expire le: 31/12/{expiry}", "Nationalite: Burundaise"],
        validite="Valide" if expiry >= 2024 else "Expire"
    )
    return texte, analyse

# --- 13. QUITTANCES / REÇUS ---------------------------------------------------

def gen_quittance():
    nom, prenom, _ = rand_person()
    org = random.choice(["REGIDESO","ONATEL","OBR","Mairie de Bujumbura","RTNB","OTRACO"])
    montant = random.randint(5,500) * 1000
    motif = random.choice(["Paiement facture eau","Paiement facture electricite","Taxe fonciere","Impot sur le revenu","Frais scolaires","Cotisation sociale"])
    date_em = rand_emit_date(2022,2024)
    ref = rand_ref("QUIT")

    texte = f"""REPUBLIQUE DU BURUNDI
{org.upper()}
QUITTANCE DE PAIEMENT

Recu de: {nom} {prenom}
Motif: {motif}
Montant: {montant:,} BIF
Mode de paiement: {random.choice(["Especes","Virement","Mobile Money","Cheque"])}
Date: {date_em}
N Quittance: {ref}
Caissier: {random.choice(PRENOMS_M)} {random.choice(NOMS)}"""

    analyse = make_analyse(
        "Quittance de paiement",
        f"{nom} {prenom}",
        org,
        date_em,
        ref,
        [f"Motif: {motif}", f"Montant: {montant:,} BIF", f"Date: {date_em}"]
    )
    return texte, analyse

# --- 14. LETTRES DE RECOMMANDATION --------------------------------------------

def gen_recommandation():
    nom, prenom, genre = rand_person()
    org = random.choice(UNIVERSITES + MINISTERES + ENTREPRISES)
    signataire = f"{random.choice(['Prof.','Dr.','M.','Mme'])} {random.choice(PRENOMS_M)} {random.choice(NOMS)}"
    date_em = rand_emit_date(2022,2024)
    ref = rand_ref("REC")
    qualites = ["serieux","competent","rigoureux","dynamique","ponctuel","innovant","fiable"]
    q1, q2 = random.sample(qualites, 2)

    texte = f"""REPUBLIQUE DU BURUNDI
{org.upper()}
LETTRE DE RECOMMANDATION

Je soussigne, {signataire}, certifie avoir travaille avec
{nom} {prenom} au sein de notre institution.
Je le/la recommande vivement pour ses qualites de {q1} et {q2}.
Cette lettre est delivree pour servir et valoir ce que de droit.
Bujumbura, le {date_em}
Ref: {ref}"""

    analyse = make_analyse(
        "Lettre de recommandation",
        f"{nom} {prenom}",
        org,
        date_em,
        ref,
        [f"Signataire: {signataire}", f"Qualites: {q1}, {q2}"]
    )
    return texte, analyse

# --- GÉNÉRATEUR PRINCIPAL -----------------------------------------------------

GENERATORS = [
    (gen_diplome, 1500),
    (gen_attestation_travail, 1500),
    (gen_acte_notarie, 1000),
    (gen_naissance, 1000),
    (gen_casier, 800),
    (gen_permis, 800),
    (gen_certificat_medical, 700),
    (gen_contrat_travail, 700),
    (gen_mariage, 600),
    (gen_attestation_scolaire, 600),
    (gen_titre_foncier, 500),
    (gen_cni, 500),
    (gen_quittance, 400),
    (gen_recommandation, 400),
]

def generate_dataset(output_dir="."):
    all_entries = []
    total = 0

    for gen_fn, count in GENERATORS:
        print(f"Generation {count} exemples: {gen_fn.__name__}...")
        for _ in range(count):
            try:
                texte, analyse = gen_fn()
                analyse_str = json.dumps(analyse, ensure_ascii=False)
                entry = {
                    "text": PROMPT_TEMPLATE.format(texte=texte, analyse=analyse_str)
                }
                all_entries.append(entry)
                total += 1
            except Exception as e:
                print(f"  Erreur: {e}")

    random.shuffle(all_entries)

    # Split 90% train / 10% eval
    split = int(len(all_entries) * 0.9)
    train_data = all_entries[:split]
    eval_data = all_entries[split:]

    train_path = os.path.join(output_dir, "train.jsonl")
    eval_path = os.path.join(output_dir, "eval.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(eval_path, "w", encoding="utf-8") as f:
        for item in eval_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\nDataset Nsuzumira genere:")
    print(f"  Total  : {total} exemples")
    print(f"  Train  : {len(train_data)} exemples -> {train_path}")
    print(f"  Eval   : {len(eval_data)} exemples -> {eval_path}")
    print(f"  Types  : {len(GENERATORS)} types de documents")
    return train_path, eval_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default=".")
    args = parser.parse_args()
    generate_dataset(args.output_dir)

