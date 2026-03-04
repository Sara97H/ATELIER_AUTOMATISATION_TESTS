# API Choice

- **Étudiant :** sarahaddad
- **API choisie :** IPSTACK
- **URL base :** https://api.ipstack.com/
- **Documentation officielle / README :** https://ipstack.com/documentation
- **Auth :** API Key (variable d'environnement)
- **Endpoints testés :**
  - GET /check (without IP - uses client IP)
  - GET /{ip} (specific IP lookup)
  - GET /{ip} with query params (language, security=1, hostname=1)
  
- **Hypothèses de contrat (champs attendus, types, codes) :**
  - HTTP 200 attendu pour IPs valides
  - Champs obligatoires: `ip` (string), `country_code` (string), `country_name` (string), `city` (string), `latitude` (float), `longitude` (float)
  - Types: strings pour adresses, floats pour coordonnées
  - 400 pour IP invalide, 403 pour clé API invalide
  
- **Limites / rate limiting connu :**
  - 150 requêtes/minute pour plan gratuit (429 possible)
  - Risk de rate limiting → implémentation de retry avec backoff
  
- **Risques (instabilité, downtime, CORS, etc.) :**
  - API tierce externe → possibilité de timeout
  - Clé API à protéger (variable d'environnement)
  - CORS possible en appel direct depuis navigateur (utiliser Proxy if needed)