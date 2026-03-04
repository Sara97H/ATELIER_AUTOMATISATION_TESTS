------------------------------------------------------------------------------------------------------
🎯Atelier “Testing as Code & API Monitoring”
------------------------------------------------------------------------------------------------------
Aujourd’hui, vous allez passer du rôle de développeur au rôle d’ingénieur qualité.  
  
Internet est rempli d’API publiques : météo, devises, citations, géolocalisation, données statistiques…
Mais une API, ce n’est pas juste une URL qui répond. C’est un service.
Et un service doit être fiable, mesurable et surveillé.  
  
Votre mission :  
  
👉 Choisir une API publique.  
👉 Concevoir et implémenter une solution d’automatisation des tests.  
👉 Déployer votre solution sur PythonAnywhere.  
👉 Mesurer et exposer des indicateurs de qualité de service.    

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- pip
- IPSTACK API Key: `7ead199380666b8913f0ecf608ff9996`

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file (optional - already included)
# cp .env.example .env
# Edit .env and set your IPSTACK_API_KEY

# 3. Run local tests
python run_tests_local.py

# 4. Start Flask app locally
python flask_app.py
# Then visit: http://localhost:5000/dashboard
```

### Project Structure

```
.
├── flask_app.py           # Flask app with /dashboard, /api/run endpoints
├── storage.py             # SQLite storage for test runs
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API key)
├── tester/
│   ├── __init__.py
│   ├── client.py         # HTTP client wrapper (timeout, retry)
│   ├── tests.py          # 7 test cases (contract + robustness)
│   └── runner.py         # Test runner + QoS metrics
├── templates/
│   ├── consignes.html    # Instructions page
│   └── dashboard.html    # Beautiful test dashboard
└── API_CHOICE.md         # API documentation
```

### API Features

✅ **7 Test Cases:**
- Valid IP returns 200
- Required fields present
- Field types correct
- Latitude/Longitude validation
- Invalid IP error detection
- QoS latency threshold
- Content-Type JSON

✅ **Robustness:**
- 5s timeout
- 1 retry on failure
- Rate limit handling (429)
- 20 requests max per run

✅ **QoS Metrics:**
- Average latency
- P95 latency
- Availability %
- Error rate

✅ **Dashboard:**
- Beautiful real-time UI
- Test results display
- Historical data table
- Run execution button

### Endpoints

```
GET  /                  # Home page with instructions
GET  /dashboard         # Test results dashboard  
POST /api/run           # Execute tests (JSON response)
GET  /api/dashboard     # Get dashboard data (JSON)
GET  /health            # Service health check (Bonus)
```

### Example Response

```json
{
  "api": "IPSTACK",
  "timestamp": "2026-03-04T16:00:00.000000",
  "summary": {
    "passed": 7,
    "failed": 0,
    "total": 7,
    "error_rate": 0.0,
    "latency_ms_avg": 245.3,
    "latency_ms_p95": 380.5,
    "availability_percent": 100.0
  },
  "tests": [...]
}
```

## 🌐 Deployment on PythonAnywhere

### 1. Create Account
- Go to https://www.pythonanywhere.com
- Sign up (your username: `sarahaddad`)
- Click "Beginner account" (free tier)

### 2. Upload Code
```bash
# Via Git Clone:
git clone <your-repo-url> ~/mysite
cd ~/mysite

# Or upload via Web
```

### 3. Configure Web App
1. Go to Web tab
2. Create new web app
3. Choose "Manual configuration"
4. Select Python 3.10
5. Set source directory to your project folder

### 4. Configure WSGI File
Edit `/var/www/sarahaddad_pythonanywhere_com_wsgi.py`:

```python
import sys
import os

path = '/home/sarahaddad/mysite'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from flask_app import app
application = app
```

### 5. Configure Virtual Environment
```bash
# In PythonAnywhere bash:
mkvirtualenv --python=/usr/bin/python3.10 myenv
pip install -r requirements.txt
pip install python-dotenv
```

### 6. Add Scheduled Task (Bonus - Auto-Run Tests)
In PythonAnywhere Web tab → Scheduled tasks:
```
Daily 2:00 AM: wget https://sarahaddad.pythonanywhere.com/api/run?token=secret
```

### 7. Verify Deployment
- Visit: https://sarahaddad.pythonanywhere.com/
- Check logs: https://sarahaddad.pythonanywhere.com.error.log

## 📊 Evaluation Checklist (20 points)

- [ ] **API Choice + Contract** (2 pts) - API_CHOICE.md completed
- [ ] **Test Quality** (6 pts) - 7 tests (not 6), pertinent assertions
- [ ] **Robustness** (4 pts) - Timeout/retry/429 handling
- [ ] **QoS Metrics** (4 pts) - Latency + error rate + availability
- [ ] **Dashboard** (4 pts) - Beautiful, clear, historical data

**Bonus (+2 pts):**
- [ ] Scheduled execution (cron task)
- [ ] `/health` endpoint
- [ ] Export JSON feature

## 🐛 Troubleshooting

### Error Logs Location
```
Access log: https://sarahaddad.pythonanywhere.com.access.log
Error log:  https://sarahaddad.pythonanywhere.com.error.log  
Server log: https://sarahaddad.pythonanywhere.com.server.log
```

### Common Issues

**"ModuleNotFoundError: No module named 'tester'"**
- Ensure PYTHONPATH includes project folder
- Check virtualenv activation in WSGI

**"IPSTACK_API_KEY not found"**
- Add `.env` file with `IPSTACK_API_KEY=<your-key>`
- Or set in PythonAnywhere Web settings

**"connection timeout"**
- IPSTACK might be slow/down
- Check latency in dashboard
- Increase timeout in `client.py` if needed

-------------------------------------------------------------------------------------------------------
🧩 Séquence 1 : GitHUB
-------------------------------------------------------------------------------------------------------
Objectif : Création d'un Repository GitHUB pour travailler avec son projet  
Difficulté : Très facile (~10 minutes)
-------------------------------------------------------------------------------------------------------
**Faites un Fork de ce projet**. Si besoin, voici une vidéo d'accompagnement pour vous aider à "Forker" un Repository Github : [Forker ce projet](https://youtu.be/p33-7XQ29zQ)  

---------------------------------------------------
🧩 Séquence 2 : Création d'un site chez Pythonanywhere
---------------------------------------------------
Objectif : Créer un hébergement sur Pythonanywhere  
Difficulté : Faible (~10 minutes)
---------------------------------------------------

Rendez-vous sur **https://www.pythonanywhere.com/** et créez vous un compte.  
  
---------------------------------------------------------------------------------------------
🧩 Séquence 3 : Les Actions GitHUB (Industrialisation Continue)
---------------------------------------------------------------------------------------------
Objectif : Automatiser la mise à jour de votre hébergement Pythonanywhere  
Difficulté : Moyenne (~15 minutes)
---------------------------------------------------------------------------------------------
Dans le Repository GitHUB que vous venez de créer précédemment lors de la séquence 1, vous avez un fichier intitulé deploy-pythonanywhere.yml et qui est déposé dans le répertoire .github/workflows. Ce fichier a pour objectif d'automatiser le déploiement de votre code sur votre site Pythonanywhere. Pour information, c'est ce que l'on appel des Actions GitHUB. Ce sont des scripts qui s'exécutent automatiquement lors de chaque Commit dans votre projet (C'est à dire à chaque modification de votre code). Ces scripts (appelés actions) sont au format yml qui est un format structuré proche de celui d'XML.  

Pour utiliser cette Action (deploy-pythonanywhere.yml), **vous avez besoin de créer des secrets dans GitHUB** afin de ne pas divulguer des informations sensibles aux internautes de passage dans votre Repository comme vos login et password par exemple.  

Pour cet atelier, **vous avez 4 secrets à créer** dans votre Repository GitHUB : **Settings → Secrets and variables → Actions → New repository secret**  
  
**PA_USERNAME** = votre username PythonAnywhere.  
**PA_TOKEN** = votre API token. Token à créer dans pythonanywhere (Acount → API Token).  
**PA_TARGET_DIR** = Web → Source code (ex: /home/monuser/myapp).  
**PA_WEBAPP_DOMAIN** = votre site (ex: monuser.pythonanywhere.com).  
  
**Dernière étape :** Pour engager l'automatisation de votre première Action, vous devez cliquer sur le gros boutton vert dans l'onglet supérieur [Actions] dans votre Repository Github. Le boutton s'intitule "I understand my workflows, go ahead and enable them"   

Notions acquises de cette séquence :  
Vous avez vu dans cette séquence comment créer des secrets GiHUB afin de mettre en place de l'industrialisation continue.   
  
---------------------------------------------------
🔹 Séquence 4 : Atelier
---------------------------------------------------
Objectif : Travailler sur l'automatisation de vos tests  
Difficulté : Moyenne (~120 minutes)
---------------------------------------------------
**Consignes : Retrouvez les consignes de votre atelier sur votre site pythonanywhere**    
Vous pouvez retrouver le travail demandé dans le cadre de cet atelier directement sur votre site pythonanywhere (ex: monuser.pythonanywhere.com).    
   
--------------------------------------------------------------------
🧠 Troubleshooting :
---------------------------------------------------
Objectif : Visualiser ses logs et découvrir ses erreurs
---------------------------------------------------
Lors de vos développements, vous serez peut-être confronté à des erreurs systèmes car vous avez faits des erreurs de syntaxes dans votre code, faits de mauvaises déclarations de fonctions, appelez des modules inexistants, mal renseigner vos secrets, etc…  
Les causes d'erreurs sont quasi illimitées. **Vous devez donc vous tourner vers les logs de votre système pour comprendre d'où vient le problème** :  

Vos log sont accéssible via les URL suivantes :  
* Access log : {site}.pythonanywhere.com.access.log
* Error log : {site}.pythonanywhere.com.error.log
* Server log: {site}.pythonanywhere.com.server.log
