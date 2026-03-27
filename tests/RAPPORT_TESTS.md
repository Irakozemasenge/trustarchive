# Rapport de Tests TrustArchive.bi
Date: 2026-03-28 00:03

## Resultats

| Test | Statut |
|------|--------|
| Login superadmin | PASS |
| Login public | PASS |
| Register nouveau user | PASS |
| Register doublon -> 400 | PASS |
| Me endpoint | PASS |
| Me sans token -> 401 | PASS |
| Categories (11 categories) | PASS |
| Stats documents | PASS |
| All documents (pagination) | PASS |
| Blockchain valid=True | PASS |
| Audit logs | PASS |
| AI stats | PASS |
| Partners list | PASS |
| Admins list | PASS |
| Verify inexistant -> 404 | PASS |
| Public bloque sur audit | PASS |
| Public bloque sur all docs | PASS |
| Public bloque creation doc | PASS |
| Audit sans token -> 401 | PASS |

## Bugs corriges
- Double SPECTACULAR_SETTINGS dans settings.py
- Serveur Django tombe apres modification settings
- Categories retournait 0 pour user public (normal - admin requis)

## Analyse CNI IRAKOZE
- Type: Carte Nationale d Identite
- Beneficiaire: IRAKOZE Jean De Dieu
- N MIFP: 531.01802/14.6298
- Delivree: 16/02/2018 a Bujumbura
- Validite: Valide

## Score: 19/19 tests passes (100%)
