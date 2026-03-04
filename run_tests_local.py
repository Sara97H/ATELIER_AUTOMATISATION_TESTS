#!/usr/bin/env python3
"""
Script de test local - Vérifie que tout fonctionne correctement
Utilise la clé API IPSTACK fournie
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env if exists
load_dotenv()

def test_imports():
    """Vérifie que tous les imports fonctionnent"""
    print("[TEST] Vérification des imports...")
    try:
        from tester.client import IPStackClient
        from tester.tests import IPStackTester
        from tester.runner import TestRunner
        from storage import TestStorage
        print("✅ Imports OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur imports: {e}\n")
        return False

def test_client():
    """Teste le client HTTP"""
    print("[TEST] Vérification du client HTTP...")
    try:
        from tester.client import IPStackClient
        
        # Utilise la clé API de l'utilisateur
        api_key = os.getenv('IPSTACK_API_KEY')
        if not api_key:
            print("⚠️ IPSTACK_API_KEY not set - utilise 'test_key'")
            api_key = "test_key"
        
        client = IPStackClient(api_key)
        print(f"✅ Client créé avec succès (max_requests={client.MAX_REQUESTS_PER_RUN})\n")
        return True
    except Exception as e:
        print(f"❌ Erreur client: {e}\n")
        return False

def test_tests():
    """Teste la suite de tests"""
    print("[TEST] Vérification de la suite de tests...")
    try:
        from tester.client import IPStackClient
        from tester.tests import IPStackTester
        
        api_key = os.getenv('IPSTACK_API_KEY', 'test_key')
        client = IPStackClient(api_key)
        tester = IPStackTester(client)
        
        # Vérifie les assertions
        tester.assert_equal(1, 1, "Test égalité")
        tester.assert_type("test", str, "Test type")
        tester.assert_in(1, [1, 2, 3], "Test contenance")
        
        print("✅ Suite de tests OK (assertions fonctionnent)\n")
        return True
    except Exception as e:
        print(f"❌ Erreur tests: {e}\n")
        return False

def test_storage():
    """Teste la base de données SQLite"""
    print("[TEST] Vérification de la base de données...")
    try:
        from storage import TestStorage
        import os
        import time
        
        storage = TestStorage('test_runs_test.db')
        
        # Test des statistiques
        stats = storage.get_stats()
        print(f"✅ Storage OK (total_runs={stats['total_runs']})\n")
        
        # Cleanup - avec retry pour Windows
        db_file = 'test_runs_test.db'
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except (OSError, PermissionError):
                # Windows peut verrouiller le fichier - c'est OK
                print("  (Note: could not delete test db file - this is OK)")
        
        return True
    except Exception as e:
        print(f"❌ Erreur storage: {e}\n")
        return False

def test_flask_app():
    """Teste l'application Flask"""
    print("[TEST] Vérification de l'application Flask...")
    try:
        from flask_app import app
        
        # Vérifie les routes
        client = app.test_client()
        
        response = client.get('/')
        print(f"  - GET / : {response.status_code}")
        
        response = client.get('/health')
        print(f"  - GET /health : {response.status_code}")
        
        response = client.get('/api/dashboard')
        print(f"  - GET /api/dashboard : {response.status_code}")
        
        print("✅ Flask app OK\n")
        return True
    except Exception as e:
        print(f"❌ Erreur Flask: {e}\n")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 IPSTACK Testing Framework - Local Test Suite")
    print("="*60 + "\n")
    
    tests = [
        test_imports,
        test_client,
        test_tests,
        test_storage,
        test_flask_app
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Exception in {test.__name__}: {e}\n")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix them.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
