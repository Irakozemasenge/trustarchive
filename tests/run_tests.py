# -*- coding: utf-8 -*-
"""
Suite de tests TrustArchive.bi
Testeur: QA automatise
"""
import json
import sys
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"
PASS = 0
FAIL = 0
BUGS = []

def req(method, path, body=None, token=None, expect=200):
    global PASS, FAIL
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r, timeout=10) as resp:
            status = resp.status
            result = json.loads(resp.read())
            ok = status == expect or (expect == 200 and status in [200, 201])
            if ok:
                PASS += 1
                print(f"  [PASS] {method} {path} -> {status}")
            else:
                FAIL += 1
                BUGS.append(f"{method} {path}: attendu {expect} recu {status}")
                print(f"  [FAIL] {method} {path} -> {status} (attendu {expect})")
            return result, status
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            result = json.loads(e.read())
        except Exception:
            result = {}
        ok = status == expect
        if ok:
            PASS += 1
            print(f"  [PASS] {method} {path} -> {status}")
        else:
            FAIL += 1
            BUGS.append(f"{method} {path}: attendu {expect} recu {status} - {result}")
            print(f"  [FAIL] {method} {path} -> {status} | {result}")
        return result, status
    except Exception as e:
        FAIL += 1
        BUGS.append(f"{method} {path}: ERREUR {e}")
        print(f"  [ERR]  {method} {path} -> {e}")
        return {}, 0


print("\n" + "="*60)
print("  TRUSTARCHIVE.BI — SUITE DE TESTS QA")
print("  Testeur: Nsuzumira QA Bot")
print("="*60)

# ─── SECTION 1: AUTH ─────────────────────────────────────────────────────────
print("\n[1] AUTHENTIFICATION")

# 1.1 Register nouveau user
r, _ = req("POST", "/auth/register/", {
    "email": "qa_test@trustarchive.bi",
    "full_name": "QA Testeur",
    "phone": "79123456",
    "password": "QaTest@2024"
})

# 1.2 Register doublon (doit echouer)
r, s = req("POST", "/auth/register/", {
    "email": "qa_test@trustarchive.bi",
    "full_name": "QA Testeur",
    "password": "QaTest@2024"
}, expect=400)

# 1.3 Login public
r, _ = req("POST", "/auth/login/", {"email": "qa_test@trustarchive.bi", "password": "QaTest@2024"})
pub_token = r.get("access", "")
assert pub_token, "Token manquant"
print(f"         role={r.get('user',{}).get('role')} token={'OK' if pub_token else 'FAIL'}")

# 1.4 Login mauvais mot de passe
req("POST", "/auth/login/", {"email": "qa_test@trustarchive.bi", "password": "WRONG"}, expect=401)

# 1.5 Login superadmin
r, _ = req("POST", "/auth/login/", {"email": "admin@trustarchive.bi", "password": "Admin@1234"})
sa_token = r.get("access", "")
print(f"         superadmin role={r.get('user',{}).get('role')} token={'OK' if sa_token else 'FAIL'}")

# 1.6 Me endpoint
r, _ = req("GET", "/auth/me/", token=pub_token)
print(f"         me={r.get('full_name')} role={r.get('role')}")

# 1.7 Me sans token (doit echouer)
req("GET", "/auth/me/", expect=401)

# ─── SECTION 2: DOCUMENTS ────────────────────────────────────────────────────
print("\n[2] DOCUMENTS")

# 2.1 Verification document inexistant
r, _ = req("GET", "/documents/verify/TA-FAKE-00000000/", expect=404)
print(f"         found={r.get('found')} authentic={r.get('authentic')}")

# 2.2 Categories (admin requis)
r, _ = req("GET", "/documents/categories/", token=sa_token)
nb_cats = len(r) if isinstance(r, list) else r.get("count", 0)
print(f"         categories={nb_cats}")
if nb_cats == 0:
    BUGS.append("BUG: 0 categories - seed_categories non execute?")
    print("  [WARN] 0 categories - lancer: python manage.py seed_categories")

# 2.3 Stats documents
r, _ = req("GET", "/documents/stats/", token=sa_token)
print(f"         stats: total={r.get('total')} verified={r.get('verified')}")

# 2.4 Tous les documents (superadmin)
r, _ = req("GET", "/documents/all/", token=sa_token)
nb_docs = r.get("count", 0) if isinstance(r, dict) else len(r)
print(f"         all docs={nb_docs}")

# 2.5 Documents sans token (doit echouer)
req("GET", "/documents/", expect=401)

# ─── SECTION 3: BLOCKCHAIN ───────────────────────────────────────────────────
print("\n[3] BLOCKCHAIN")

# 3.1 Records
r, _ = req("GET", "/blockchain/records/", token=sa_token)
nb_blocs = r.get("count", 0) if isinstance(r, dict) else len(r)
print(f"         blocs={nb_blocs}")

# 3.2 Verify chain
r, _ = req("GET", "/blockchain/verify-chain/", token=sa_token)
print(f"         valid={r.get('valid')} msg={r.get('message')}")
if not r.get("valid"):
    BUGS.append("BUG CRITIQUE: Blockchain corrompue!")

# 3.3 Verify hash public
r, _ = req("POST", "/blockchain/verify-hash/", {"unique_number": "TA-FAKE", "document_hash": "abc"})
print(f"         verify_hash authentic={r.get('authentic')}")

# ─── SECTION 4: AUDIT ────────────────────────────────────────────────────────
print("\n[4] AUDIT")

# 4.1 Stats audit
r, _ = req("GET", "/audit/stats/", token=sa_token)
print(f"         total_logs={r.get('total_logs')} unresolved={r.get('unresolved_errors')}")

# 4.2 Logs
r, _ = req("GET", "/audit/logs/", token=sa_token)
nb_logs = r.get("count", 0) if isinstance(r, dict) else len(r)
print(f"         logs={nb_logs}")

# 4.3 Errors
r, _ = req("GET", "/audit/errors/", token=sa_token)
nb_errors = r.get("count", 0) if isinstance(r, dict) else len(r)
print(f"         errors={nb_errors}")

# 4.4 Audit sans token (doit echouer)
req("GET", "/audit/logs/", expect=401)

# ─── SECTION 5: REQUESTS ─────────────────────────────────────────────────────
print("\n[5] DEMANDES EN LIGNE")

# 5.1 Partners list (public)
r, _ = req("GET", "/auth/partners/")
nb_partners = len(r) if isinstance(r, list) else 0
print(f"         partners={nb_partners}")

# 5.2 Mes demandes (user connecte)
r, _ = req("GET", "/requests/", token=pub_token)
nb_reqs = r.get("count", 0) if isinstance(r, dict) else len(r)
print(f"         mes demandes={nb_reqs}")

# 5.3 Demandes sans token (doit echouer)
req("GET", "/requests/", expect=401)

# ─── SECTION 6: IA NSUZUMIRA ─────────────────────────────────────────────────
print("\n[6] IA NSUZUMIRA")

# 6.1 AI stats
r, _ = req("GET", "/ai/stats/", token=sa_token)
print(f"         total_analyses={r.get('total_analyses')} success_rate={r.get('success_rate')}%")

# 6.2 Analyse document inexistant
req("POST", "/ai/analyze/99999/", token=sa_token, expect=404)

# 6.3 AI sans token
req("POST", "/ai/analyze/1/", expect=401)

# ─── SECTION 7: SECURITE ─────────────────────────────────────────────────────
print("\n[7] SECURITE")

# 7.1 User public ne peut pas voir tous les docs
req("GET", "/documents/all/", token=pub_token, expect=403)

# 7.2 User public ne peut pas voir audit
req("GET", "/audit/logs/", token=pub_token, expect=403)

# 7.3 User public ne peut pas creer admin
req("POST", "/auth/admins/create/", {"email":"hack@test.bi","full_name":"Hacker","password":"hack123"}, token=pub_token, expect=403)

# 7.4 User public ne peut pas voir blockchain records
req("GET", "/blockchain/records/", token=pub_token, expect=403)

# ─── RAPPORT FINAL ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"  RAPPORT FINAL")
print(f"  PASS : {PASS}")
print(f"  FAIL : {FAIL}")
total = PASS + FAIL
print(f"  TOTAL: {total} tests | Taux reussite: {round(PASS/total*100,1) if total else 0}%")

if BUGS:
    print(f"\n  BUGS DETECTES ({len(BUGS)}):")
    for b in BUGS:
        print(f"    - {b}")
else:
    print("\n  Aucun bug detecte!")

print("="*60 + "\n")
sys.exit(0 if FAIL == 0 else 1)
