# Guide de Déploiement PythonAnywhere

## 📋 Avant de commencer

- Vous : **sarahaddad** (username PythonAnywhere)
- URL : **https://sarahaddad.pythonanywhere.com**
- API Key : **7ead199380666b8913f0ecf608ff9996**

## 🚀 Étapes de déploiement

### 1️⃣ Créer le compte & site PythonAnywhere

```
1. Allez à https://www.pythonanywhere.com
2. Sign up avec l'email (ou login si compte exists)
3. Cliquez sur "Beginner account" (gratuit, 1 web app)
4. Complétez l'inscription
```

### 2️⃣ Uploader le code

**Option A: Via Bash Console (recommandé)**

```bash
# Open Bash Console in PythonAnywhere Web Interface
cd ~
git clone <your-github-repo-url> mysite
cd mysite
```

**Option B: Via Upload Direct**

```bash
# Upload via Web UI
# Dashboard → Files → Upload files...
# Upload le zip du projet
```

### 3️⃣ Configuration du Web App

#### 3.1 Dans PythonAnywhere Dashboard:

```
1. Allez à: Web
2. Cliquez: Add a new web app
3. Choose: Manual configuration
4. Select Python: 3.10
5. Cliquez: Next
```

#### 3.2 Configuration Source:

```
Dans Web → Code section:
- Source code: /home/sarahaddad/mysite
- Working directory: /home/sarahaddad/mysite
- WSGI configuration file: /var/www/sarahaddad_pythonanywhere_com_wsgi.py
```

### 4️⃣ Créer le virtualenv

```bash
# En Bash dans PythonAnywhere:
mkvirtualenv --python=/usr/bin/python3.10 myenv
workon myenv
cd ~/mysite
pip install -r requirements.txt
pip install python-dotenv
```

### 5️⃣ Configuration WSGI

**Éditez** `/var/www/sarahaddad_pythonanywhere_com_wsgi.py`:

```python
import sys
import os

# Add project to path
path = '/home/sarahaddad/mysite'
if path not in sys.path:
    sys.path.append(path)

# Change working directory
os.chdir(path)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Import Flask app
from flask_app import app
application = app
```

### 6️⃣ Ajouter les Variables d'Environnement

**Méthode 1: Fichier .env**

```bash
# Dans ~/mysite/.env:
IPSTACK_API_KEY=7ead199380666b8913f0ecf608ff9996
FLASK_ENV=production
```

**Méthode 2: Variables PythonAnywhere (Web → Environment variables)**

```
IPSTACK_API_KEY = 7ead199380666b8913f0ecf608ff9996
FLASK_ENV = production
```

### 7️⃣ Recharger l'app

```
Web → Reload [sarahaddad.pythonanywhere.com]
```

### 8️⃣ Vérifier que ça fonctionne

Visitez:
- 🏠 **Home**: https://sarahaddad.pythonanywhere.com/
- 📊 **Dashboard**: https://sarahaddad.pythonanywhere.com/dashboard
- 🏥 **Health**: https://sarahaddad.pythonanywhere.com/health

## 🐛 Troubleshooting

### Erreur 404 / 500

**Vérifiez les logs:**

```
https://sarahaddad.pythonanywhere.com.error.log
https://sarahaddad.pythonanywhere.com.access.log
```

### "ModuleNotFoundError: No module named 'tester'"

**Solution:** Assurez que PYTHONPATH contient le projet:

```python
# Dans WSGI, avant l'import:
sys.path.insert(0, '/home/sarahaddad/mysite')
```

### "IPSTACK_API_KEY not found"

**Vérifiez:**

1. Le `.env` existe et contient la clé
2. Ou la variable est définie dans PythonAnywhere Web → Environment variables
3. Ou dans le WSGI: `os.environ['IPSTACK_API_KEY'] = 'votre_clé'`

### Rate Limit 429

**Normal:** L'API gratuite IPSTACK a limite de 150 req/min.

**Solution:**
- Attendez 1-2 min et relancez les tests
- Ou achetez un plan payant

### "ModuleNotFoundError: No module named 'requests'"

```bash
# Assurez que virtualenv est activé:
workon myenv
pip install requests
```

### Les tests ne s'exécutent pas

```bash
# Testez localement en Bash:
workon myenv
cd ~/mysite
python -c "from tester.runner import TestRunner; r = TestRunner(); print(r.run())"
```

## ⏰ Ajouter une Tâche Planifiée (Bonus)

Pour exécuter les tests automatiquement chaque jour:

```
Web → Scheduled tasks → Create new scheduled task
Time: 02:00 (UTC)
Command: 
  curl https://sarahaddad.pythonanywhere.com/api/run || true
```

Cela exécutera les tests à 2h du matin tous les jours.

## 📊 Vérifier le Dashboard

Une fois déployé, visitez:

```
https://sarahaddad.pythonanywhere.com/dashboard
```

Le dashboard affichera:
- ✅ Derniers résultats de tests
- 📊 Métriques QoS (latence, disponibilité)
- 📜 Historique des runs
- 🔄 Bouton "Exécuter Tests"

## 🎯 Endpoints disponibles

```
GET  /                  → Instructions (consignes.html)
GET  /dashboard         → Dashboard des tests
POST /api/run           → Exécute les tests
GET  /api/dashboard     → Données JSON du dashboard
GET  /health            → État de santé du service
```

## Exemple de réponse `/api/run`

```json
{
  "api": "IPSTACK",
  "timestamp": "2026-03-04T12:00:00",
  "summary": {
    "passed": 7,
    "failed": 0,
    "error_rate": 0.0,
    "latency_ms_avg": 245.3,
    "latency_ms_p95": 380.5,
    "availability_percent": 100.0
  },
  "tests": [...]
}
```

## ✅ Checklist Final

- [ ] Repo GitHub créé
- [ ] Code uploadé sur PythonAnywhere
- [ ] Virtualenv créé avec dépendances
- [ ] WSGI configuré
- [ ] `.env` avec `IPSTACK_API_KEY`
- [ ] Web app reloadée
- [ ] Dashboard accessible
- [ ] Tests s'exécutent via `/api/run`
- [ ] Historique sauvegardé en SQLite
- [ ] [Bonus] Tâche planifiée configurée
- [ ] [Bonus] `/health` endpoint teste

## 🎓 Points de grading

✅ **20 points max:**

- 2 pts: API_CHOICE.md bien rempli
- 6 pts: Tests de qualité (7 tests, assertions pertinentes)
- 4 pts: Robustesse (timeout, retry, 429 handling)
- 4 pts: QoS métriques (latence, erreur, availabilité)
- 4 pts: Dashboard clair + historique 

🎁 **Bonus +2 pts:**
- Tâche planifiée stable
- Export JSON
- `/health` endpoint
- Visualisation trends

Bonne chance! 🚀
