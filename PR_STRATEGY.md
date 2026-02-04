# Stratégie de PRs vers l'upstream

## Plan de découpage

### PR 1 : Zeroconf Discovery (Petite, facile à merger)
**Fichiers concernés :**
- `manifest.json` - ajout zeroconf
- `config_flow.py` - découverte automatique
- `__init__.py` - support discovery

**Valeur :** Feature visible et testable facilement

---

### PR 2 : Coordinator + Diagnostics (Architecture)
**Fichiers concernés :**
- `coordinator.py` (nouveau)
- `diagnostics.py` (nouveau)
- `__init__.py` - intégration coordinator
- `entity.py` - utilisation coordinator
- `const.py` - constantes

**Valeur :** Améliore performance et débogage

---

### PR 3 : Services & Select Entities (Features)
**Fichiers concernés :**
- `services.yaml` (nouveau)
- `select.py` (nouveau)
- `__init__.py` - register services
- Translations mises à jour

**Valeur :** Nouvelles fonctionnalités utilisateur

---

### PR 4 : CI/CD + Dev Tools (Infra)
**Fichiers concernés :**
- `.github/workflows/` complets
- `.pre-commit-config.yaml`
- `CONTRIBUTING.md`
- `SETUP_DEVELOPMENT.md`
- `Makefile`
- `requirements_test.txt`
- `CHANGELOG.md`

**Valeur :** Qualité et maintenance

---

## Ordre recommandé

1. **PR 1** (Zeroconf) → Facile, feature visible
2. **PR 2** (Coordinator) → Fondation technique
3. **PR 3** (Services) → Features utilisateur
4. **PR 4** (CI/CD) → Infrastructure

## Pourquoi pas tout en une ?

- ❌ Difficile à reviewer (1000+ lignes)
- ❌ Risque de conflits
- ❌ Une erreur bloque tout
- ✅ Petites PRs = merge rapide
- ✅ Feedback plus rapide
- ✅ Historique propre
