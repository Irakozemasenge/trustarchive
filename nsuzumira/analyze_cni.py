# -*- coding: utf-8 -*-
"""Analyse de la CNI IRAKOZE Jean De Dieu avec Nsuzumira"""
import sys, time
sys.path.insert(0, ".")
from test_nsuzumira import analyze_document, display_result

texte = (
    "REPUBLIKA Y'UBURUNDI\n"
    "IKARATA KARANGAMUNTU\n"
    "(Carte Nationale d Identite)\n\n"
    "IZINA       : IRAKOZE\n"
    "AMATAZIRANO : JEAN DE DIEU\n"
    "IGITSINA    : Masculin\n"
    "SE          : BUCUMI\n"
    "NYINA       : NSANANIKIYE\n"
    "PROVENSI    : BUBANZA\n"
    "KOMINE      : MUSIGATI\n"
    "YAVUKIYE    : DONDI\n"
    "ITALIKI     : 2000\n"
    "ARUBATSE    : CEL.\n"
    "AKAZI AKORA : ELEVE\n\n"
    "N MIFP      : 531.01802/14.6298\n"
    "ITANGIWE I  : BUJUMBURA\n"
    "ITALIKI     : 16/02/2018\n"
    "UWUYITANZEI : ADMINISTRATEUR DE LA COMMUNE MUKAZA\n"
    "              MAZIMPAKA ISSA DESIRE"
)

meta = {
    "title": "Carte Nationale d Identite",
    "category": "Carte Nationale d Identite",
    "issued_to": "IRAKOZE Jean De Dieu",
    "issued_by": "Commune Mukaza - Bujumbura",
    "issued_date": "2018-02-16",
    "unique_number": "MIFP-531.01802/14.6298",
    "status": "verified",
    "document_hash": "sha256:cni_irakoze_jean_de_dieu_2018"
}

start = time.time()
result, model_used, proc_time = analyze_document(texte, meta)
elapsed = round(time.time() - start, 3)
display_result("CNI IRAKOZE Jean De Dieu", texte, result, model_used, elapsed)
