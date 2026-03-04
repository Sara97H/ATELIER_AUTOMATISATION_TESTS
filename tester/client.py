"""
HTTP Client wrapper pour IPSTACK API
- Gère timeout, retry, mesure de latence
- Anti-spam: max 20 requêtes par run
"""

import requests
import time
from typing import Dict, Any, Optional
import os

class IPStackClient:
    """Client HTTP pour IPSTACK API avec timeout et retry"""
    
    BASE_URL = "https://api.ipstack.com"
    TIMEOUT_SECONDS = 5  # Timeout strict
    MAX_RETRIES = 1
    RETRY_DELAY = 2  # Attendre 2s avant retry
    MAX_REQUESTS_PER_RUN = 20
    
    def __init__(self, api_key: str):
        """
        Initialise le client
        
        Args:
            api_key: Clé API IPSTACK (from env variable IPSTACK_API_KEY)
        """
        self.api_key = api_key
        self.request_count = 0
        self.session = requests.Session()
    
    def _check_rate_limit(self) -> None:
        """Vérifie si on approche du limit de requêtes"""
        if self.request_count >= self.MAX_REQUESTS_PER_RUN:
            raise Exception(f"Rate limit local atteint: {self.MAX_REQUESTS_PER_RUN} requests")
        self.request_count += 1
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None, 
            should_retry: bool = True) -> Dict[str, Any]:
        """
        GET request avec timeout, retry simple, et mesure de latence
        
        Args:
            path: Chemin de l'endpoint (ex: "/1.1.1.1" ou "/check")
            params: Paramètres de query supplémentaires
            should_retry: Si True, réessaye une fois en cas d'erreur
            
        Returns:
            Dict avec: {
                'status_code': int,
                'latency_ms': float,
                'body': dict or None,
                'error': str or None,
                'headers': dict
            }
        """
        self._check_rate_limit()
        
        # Prépare les paramètres
        if params is None:
            params = {}
        params['access_key'] = self.api_key
        
        url = self.BASE_URL + path
        latency_ms = None
        
        try:
            # Mesure le temps
            start = time.time()
            response = self.session.get(
                url, 
                params=params,
                timeout=self.TIMEOUT_SECONDS
            )
            latency_ms = (time.time() - start) * 1000
            
            return {
                'status_code': response.status_code,
                'latency_ms': round(latency_ms, 2),
                'body': response.json() if response.text else None,
                'error': None,
                'headers': dict(response.headers)
            }
            
        except requests.exceptions.Timeout:
            if should_retry:
                time.sleep(self.RETRY_DELAY)
                return self.get(path, params, should_retry=False)
            return {
                'status_code': None,
                'latency_ms': latency_ms,
                'body': None,
                'error': 'Timeout',
                'headers': {}
            }
        except requests.exceptions.ConnectionError as e:
            if should_retry:
                time.sleep(self.RETRY_DELAY)
                return self.get(path, params, should_retry=False)
            return {
                'status_code': None,
                'latency_ms': latency_ms,
                'body': None,
                'error': f'Connection Error: {str(e)}',
                'headers': {}
            }
        except Exception as e:
            return {
                'status_code': None,
                'latency_ms': latency_ms,
                'body': None,
                'error': str(e),
                'headers': {}
            }
    
    def reset_count(self) -> None:
        """Réinitialise le compteur de requêtes"""
        self.request_count = 0
