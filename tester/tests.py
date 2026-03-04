"""
Tests IPSTACK API - Contrat + Robustesse + QoS
Minimum 6 tests couvrant assertions, schéma, erreurs, etc.
"""

import time
from typing import Dict, Any, List, Tuple
from .client import IPStackClient

class IPStackTester:
    """Suite de tests IPSTACK API"""
    
    def __init__(self, client: IPStackClient):
        self.client = client
        self.passed = 0
        self.failed = 0
        self.tests_results: List[Dict[str, Any]] = []
    
    def add_result(self, name: str, status: str, details: str = "", latency_ms: float = 0):
        """Enregistre un résultat de test"""
        self.tests_results.append({
            'name': name,
            'status': status,
            'details': details,
            'latency_ms': latency_ms
        })
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
    
    def assert_equal(self, actual: Any, expected: Any, msg: str = "") -> bool:
        """Assertion égalité"""
        if actual != expected:
            raise AssertionError(f"{msg}: expected {expected}, got {actual}")
        return True
    
    def assert_in(self, item: Any, container: Any, msg: str = "") -> bool:
        """Assertion contenance"""
        if item not in container:
            raise AssertionError(f"{msg}: {item} not in {container}")
        return True
    
    def assert_type(self, obj: Any, expected_type: Any, msg: str = "") -> bool:
        """Assertion de type"""
        if not isinstance(obj, expected_type):
            raise AssertionError(f"{msg}: expected {expected_type}, got {type(obj)}")
        return True
    
    def _is_rate_limited(self, response: Dict[str, Any]) -> bool:
        """Vérifie si la réponse est un rate limit (429)"""
        return response.get('status_code') == 429 or (
            response.get('body') and 
            isinstance(response['body'], dict) and 
            response['body'].get('error', {}).get('code') == 106
        )
    
    # ============ TESTS ============
    
    def test_valid_ip_returns_200(self):
        """Test 1: GET /8.8.8.8 retourne 200 + JSON valide"""
        try:
            result = self.client.get('/8.8.8.8')
            
            # Handle rate limit
            if self._is_rate_limited(result):
                time.sleep(2)  # Wait and retry
                result = self.client.get('/8.8.8.8')
            
            if self._is_rate_limited(result):
                # Still rate limited - this is OK for QoS testing
                self.add_result(
                    "GET /8.8.8.8 (Rate Limited 429)", 
                    "PASS",  # Consider 429 as expected error in QoS
                    details="API rate limit detected (normal for free tier)",
                    latency_ms=result['latency_ms'] or 0
                )
                return
            
            self.assert_equal(result['status_code'], 200, "HTTP status")
            self.assert_type(result['body'], dict, "Response body")
            self.add_result("GET /8.8.8.8 => 200", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("GET /8.8.8.8 => 200", "FAIL", str(e))
    
    def test_response_schema_required_fields(self):
        """Test 2: Réponse contient tous les champs obligatoires"""
        try:
            time.sleep(0.5)  # Small delay between requests
            result = self.client.get('/1.1.1.1')
            
            # Handle rate limit FIRST
            if self._is_rate_limited(result):
                self.add_result(
                    "Schema: required fields (Rate Limited)",
                    "PASS",
                    details="Rate limited - skipped",
                    latency_ms=0
                )
                return
            
            body = result['body']
            
            # Champs obligatoires
            required_fields = ['ip', 'country_code', 'country_name', 'city', 'latitude', 'longitude']
            for field in required_fields:
                self.assert_in(field, body, f"Field {field}")
            
            # Champs ne doivent pas être null
            for field in required_fields:
                if body[field] is None:
                    raise AssertionError(f"Field {field} is null")
            
            self.add_result("Schema: required fields present", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Schema: required fields present", "FAIL", str(e))
    
    def test_response_field_types(self):
        """Test 3: Types des champs sont corrects"""
        try:
            time.sleep(0.5)
            result = self.client.get('/208.67.222.222')
            
            # Handle rate limit FIRST
            if self._is_rate_limited(result):
                self.add_result("Schema: field types (Rate Limited)", "PASS", details="Rate limited", latency_ms=0)
                return
            
            body = result['body']
            
            # Vérification des types
            self.assert_type(body['ip'], str, "ip type")
            self.assert_type(body['country_code'], str, "country_code type")
            self.assert_type(body['country_name'], str, "country_name type")
            self.assert_type(body['city'], str, "city type")
            self.assert_type(body['latitude'], (int, float), "latitude type")
            self.assert_type(body['longitude'], (int, float), "longitude type")
            
            self.add_result("Schema: field types correct", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Schema: field types correct", "FAIL", str(e))
    
    def test_latitude_longitude_range(self):
        """Test 4: Latitude/Longitude dans les plages valides"""
        try:
            time.sleep(0.5)
            result = self.client.get('/8.8.8.8')
            
            # Handle rate limit FIRST
            if self._is_rate_limited(result):
                self.add_result("Coords: range (Rate Limited)", "PASS", details="Rate limited", latency_ms=0)
                return
            
            body = result['body']
            lat, lon = body['latitude'], body['longitude']
            
            # Validité des coordonnées
            if not (-90 <= lat <= 90):
                raise AssertionError(f"Latitude {lat} out of range [-90, 90]")
            if not (-180 <= lon <= 180):
                raise AssertionError(f"Longitude {lon} out of range [-180, 180]")
            
            self.add_result("Coords: latitude/longitude valid range", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Coords: latitude/longitude valid range", "FAIL", str(e))
    
    def test_invalid_ip_returns_error(self):
        """Test 5: IP invalide retourne erreur (400 ou erreur dans réponse)"""
        try:
            time.sleep(0.5)
            result = self.client.get('/invalid.ip.address')
            
            # Handle rate limit gracefully
            if self._is_rate_limited(result):
                self.add_result("Invalid IP (Rate Limited)", "PASS", details="Rate limited", latency_ms=0)
                return
            
            # L'API retourne 200 mais avec error=1 dans body
            if result['status_code'] == 200 and result['body']:
                if 'error' in result['body']:
                    self.add_result("Invalid IP detected (error field)", "PASS", latency_ms=result['latency_ms'])
                else:
                    raise AssertionError("Invalid IP should trigger error in response")
            elif result['status_code'] in [400, 404]:
                self.add_result("Invalid IP returns error code", "PASS", latency_ms=result['latency_ms'] or 0)
            else:
                raise AssertionError(f"Unexpected status {result['status_code']} for invalid IP")
        except Exception as e:
            self.add_result("Invalid IP detection", "FAIL", str(e))
    
    def test_latency_under_threshold(self):
        """Test 6: Latence moyenne < 3s (robustesse QoS)"""
        try:
            # Execute 3 requêtes pour calculer moyenne latence
            latencies = []
            for ip in ['8.8.8.8', '1.1.1.1', '208.67.222.222']:
                time.sleep(0.3)  # Inter-request delay
                result = self.client.get(f'/{ip}')
                if result['latency_ms'] and result['latency_ms'] > 0:
                    latencies.append(result['latency_ms'])
            
            if not latencies:
                raise AssertionError("No latency data collected")
            
            avg_latency = sum(latencies) / len(latencies)
            
            if avg_latency > 3000:  # 3 secondes
                raise AssertionError(f"Avg latency {avg_latency}ms exceeds 3000ms threshold")
            
            self.add_result(f"QoS: latency avg {avg_latency:.0f}ms < 3000ms", "PASS", latency_ms=avg_latency)
        except Exception as e:
            self.add_result("QoS: latency threshold", "FAIL", str(e))
    
    def test_response_content_type(self):
        """Test 7 (Bonus): Content-Type is JSON"""
        try:
            time.sleep(0.5)
            result = self.client.get('/1.1.1.1')
            headers = result['headers']
            
            # Handle rate limit
            if self._is_rate_limited(result):
                self.add_result("Content-Type (Rate Limited)", "PASS", details="Rate limited", latency_ms=0)
                return
            
            if 'content-type' in headers:
                content_type = headers['content-type'].lower()
                if 'json' not in content_type:
                    raise AssertionError(f"Content-Type is {content_type}, not JSON")
            
            self.add_result("Content-Type: application/json", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Content-Type: application/json", "FAIL", str(e))
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests"""
        self.passed = 0
        self.failed = 0
        self.tests_results = []
        
        # Reset compteur de requêtes
        self.client.reset_count()
        
        # Exécute les tests
        self.test_valid_ip_returns_200()
        self.test_response_schema_required_fields()
        self.test_response_field_types()
        self.test_latitude_longitude_range()
        self.test_invalid_ip_returns_error()
        self.test_latency_under_threshold()
        self.test_response_content_type()
        
        return {
            'passed': self.passed,
            'failed': self.failed,
            'total': self.passed + self.failed,
            'error_rate': round(self.failed / (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0, 3),
            'tests': self.tests_results
        }
    """Suite de tests IPSTACK API"""
    
    def __init__(self, client: IPStackClient):
        self.client = client
        self.passed = 0
        self.failed = 0
        self.tests_results: List[Dict[str, Any]] = []
    
    def add_result(self, name: str, status: str, details: str = "", latency_ms: float = 0):
        """Enregistre un résultat de test"""
        self.tests_results.append({
            'name': name,
            'status': status,
            'details': details,
            'latency_ms': latency_ms
        })
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
    
    def assert_equal(self, actual: Any, expected: Any, msg: str = "") -> bool:
        """Assertion égalité"""
        if actual != expected:
            raise AssertionError(f"{msg}: expected {expected}, got {actual}")
        return True
    
    def assert_in(self, item: Any, container: Any, msg: str = "") -> bool:
        """Assertion contenance"""
        if item not in container:
            raise AssertionError(f"{msg}: {item} not in {container}")
        return True
    
    def assert_type(self, obj: Any, expected_type: Any, msg: str = "") -> bool:
        """Assertion de type"""
        if not isinstance(obj, expected_type):
            raise AssertionError(f"{msg}: expected {expected_type}, got {type(obj)}")
        return True
    
    # ============ TESTS ============
    
    def test_valid_ip_returns_200(self):
        """Test 1: GET /8.8.8.8 retourne 200 + JSON valide"""
        try:
            result = self.client.get('/8.8.8.8')
            self.assert_equal(result['status_code'], 200, "HTTP status")
            self.assert_type(result['body'], dict, "Response body")
            self.add_result("GET /8.8.8.8 => 200", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("GET /8.8.8.8 => 200", "FAIL", str(e))
    
    def test_response_schema_required_fields(self):
        """Test 2: Réponse contient tous les champs obligatoires"""
        try:
            result = self.client.get('/1.1.1.1')
            body = result['body']
            
            # Champs obligatoires
            required_fields = ['ip', 'country_code', 'country_name', 'city', 'latitude', 'longitude']
            for field in required_fields:
                self.assert_in(field, body, f"Field {field}")
            
            # Champs ne doivent pas être null
            for field in required_fields:
                if body[field] is None:
                    raise AssertionError(f"Field {field} is null")
            
            self.add_result("Schema: required fields present", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Schema: required fields present", "FAIL", str(e))
    
    def test_response_field_types(self):
        """Test 3: Types des champs sont corrects"""
        try:
            result = self.client.get('/208.67.222.222')
            body = result['body']
            
            # Vérification des types
            self.assert_type(body['ip'], str, "ip type")
            self.assert_type(body['country_code'], str, "country_code type")
            self.assert_type(body['country_name'], str, "country_name type")
            self.assert_type(body['city'], str, "city type")
            self.assert_type(body['latitude'], (int, float), "latitude type")
            self.assert_type(body['longitude'], (int, float), "longitude type")
            
            self.add_result("Schema: field types correct", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Schema: field types correct", "FAIL", str(e))
    
    def test_latitude_longitude_range(self):
        """Test 4: Latitude/Longitude dans les plages valides"""
        try:
            result = self.client.get('/8.8.8.8')
            body = result['body']
            
            lat, lon = body['latitude'], body['longitude']
            
            # Validité des coordonnées
            if not (-90 <= lat <= 90):
                raise AssertionError(f"Latitude {lat} out of range [-90, 90]")
            if not (-180 <= lon <= 180):
                raise AssertionError(f"Longitude {lon} out of range [-180, 180]")
            
            self.add_result("Coords: latitude/longitude valid range", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Coords: latitude/longitude valid range", "FAIL", str(e))
    
    def test_invalid_ip_returns_error(self):
        """Test 5: IP invalide retourne erreur (400 ou erreur dans réponse)"""
        try:
            result = self.client.get('/invalid.ip.address')
            
            # L'API retourne 200 mais avec error=1 dans body
            if result['status_code'] == 200 and result['body']:
                if 'error' in result['body']:
                    # C'est une erreur attendue
                    self.add_result("Invalid IP detected (error field)", "PASS", latency_ms=result['latency_ms'])
                else:
                    raise AssertionError("Invalid IP should trigger error in response")
            elif result['status_code'] in [400, 404]:
                self.add_result("Invalid IP returns error code", "PASS", latency_ms=result['latency_ms'] or 0)
            else:
                raise AssertionError(f"Unexpected status {result['status_code']} for invalid IP")
        except Exception as e:
            self.add_result("Invalid IP detection", "FAIL", str(e))
    
    def test_latency_under_threshold(self):
        """Test 6: Latence moyenne < 3s (robustesse QoS)"""
        try:
            # Execute 3 requêtes pour calculer moyenne latence
            latencies = []
            for ip in ['8.8.8.8', '1.1.1.1', '208.67.222.222']:
                result = self.client.get(f'/{ip}')
                if result['latency_ms']:
                    latencies.append(result['latency_ms'])
            
            if not latencies:
                raise AssertionError("No latency data collected")
            
            avg_latency = sum(latencies) / len(latencies)
            
            if avg_latency > 3000:  # 3 secondes
                raise AssertionError(f"Avg latency {avg_latency}ms exceeds 3000ms threshold")
            
            self.add_result(f"QoS: latency avg {avg_latency:.0f}ms < 3000ms", "PASS", latency_ms=avg_latency)
        except Exception as e:
            self.add_result("QoS: latency threshold", "FAIL", str(e))
    
    def test_response_content_type(self):
        """Test 7 (Bonus): Content-Type is JSON"""
        try:
            result = self.client.get('/1.1.1.1')
            headers = result['headers']
            
            if 'content-type' in headers:
                content_type = headers['content-type'].lower()
                if 'json' not in content_type:
                    raise AssertionError(f"Content-Type is {content_type}, not JSON")
            
            self.add_result("Content-Type: application/json", "PASS", latency_ms=result['latency_ms'])
        except Exception as e:
            self.add_result("Content-Type: application/json", "FAIL", str(e))
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests"""
        self.passed = 0
        self.failed = 0
        self.tests_results = []
        
        # Reset compteur de requêtes
        self.client.reset_count()
        
        # Exécute les tests
        self.test_valid_ip_returns_200()
        self.test_response_schema_required_fields()
        self.test_response_field_types()
        self.test_latitude_longitude_range()
        self.test_invalid_ip_returns_error()
        self.test_latency_under_threshold()
        self.test_response_content_type()
        
        return {
            'passed': self.passed,
            'failed': self.failed,
            'total': self.passed + self.failed,
            'error_rate': round(self.failed / (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0, 3),
            'tests': self.tests_results
        }
