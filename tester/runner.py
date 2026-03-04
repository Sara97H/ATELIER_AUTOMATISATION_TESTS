"""
Runner - Exécute les tests, calcule métriques QoS, retourne résumé
"""

import os
import statistics
from datetime import datetime
from typing import Dict, Any
from .client import IPStackClient
from .tests import IPStackTester

class TestRunner:
    """Exécute une suite de tests et produit un rapport"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('IPSTACK_API_KEY')
        if not self.api_key:
            raise ValueError("IPSTACK_API_KEY not found in environment")
        self.client = IPStackClient(self.api_key)
        self.tester = IPStackTester(self.client)
    
    def run(self) -> Dict[str, Any]:
        """
        Exécute les tests et retourne un rapport complet
        
        Returns:
            {
                "api": "IPSTACK",
                "timestamp": "2026-03-04T...",
                "summary": {
                    "passed": int,
                    "failed": int,
                    "total": int,
                    "error_rate": float,
                    "latency_ms_avg": float,
                    "latency_ms_p95": float,
                    "availability": float
                },
                "tests": [...]
            }
        """
        print(f"[{datetime.now()}] Starting IPSTACK tests...")
        
        # Exécute les tests
        test_results = self.tester.run_all_tests()
        
        # Calcule les métriques QoS
        summary = self._calculate_metrics(test_results)
        
        report = {
            'api': 'IPSTACK',
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'tests': test_results['tests']
        }
        
        print(f"[{datetime.now()}] Tests completed")
        print(f"  ✓ Passed: {summary['passed']}")
        print(f"  ✗ Failed: {summary['failed']}")
        print(f"  Avg Latency: {summary['latency_ms_avg']:.0f}ms")
        print(f"  Error Rate: {summary['error_rate']*100:.1f}%")
        
        return report
    
    def _calculate_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les métriques de QoS à partir des résultats"""
        
        tests = test_results['tests']
        
        # Latences
        latencies = [t['latency_ms'] for t in tests if t['latency_ms'] and t['latency_ms'] > 0]
        
        avg_latency = statistics.mean(latencies) if latencies else 0
        p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 2 else avg_latency
        
        # Taux de disponibilité (PASS / total)
        total_tests = test_results['total']
        passed_tests = test_results['passed']
        availability = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'passed': test_results['passed'],
            'failed': test_results['failed'],
            'total': total_tests,
            'error_rate': test_results['error_rate'],
            'latency_ms_avg': round(avg_latency, 2),
            'latency_ms_p95': round(p95_latency, 2),
            'availability_percent': round(availability, 1)
        }
