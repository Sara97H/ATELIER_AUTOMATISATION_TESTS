from flask import Flask, render_template, jsonify, request
import os
from pathlib import Path

# Charger les variables d'environnement depuis .env
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

from tester.runner import TestRunner
from storage import TestStorage

app = Flask(__name__)

# Initialize storage
storage = TestStorage()

@app.get("/")
def dashboard():
    """Affiche le dashboard des tests (page d'accueil)"""
    return render_template('dashboard.html')

@app.get("/consignes")
def consignes():
    """Page des consignes/instructions"""
    return render_template('consignes.html')

@app.get("/dashboard")
def dashboard_alt():
    """Alias pour /dashboard"""
    return render_template('dashboard.html')

@app.post("/api/run")
def run_tests():
    """Exécute les tests et enregistre le résultat"""
    try:
        # Vérifie la clé API
        api_key= os.getenv("IPSTACK_API_KEY", "7ead199380666b8913f0ecf608ff9996")
        print(api_key)
        if not api_key:
            return jsonify({'error': 'IPSTACK_API_KEY not configured'}), 500
        
        # Exécute les tests
        runner = TestRunner(api_key)
        report = runner.run()
        
        # Enregistre dans la base de données
        run_id = storage.save_run(report)
        
        return jsonify({
            'success': True,
            'run_id': run_id,
            'report': report
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get("/api/dashboard")
def get_dashboard_data():
    """Retourne les données pour le dashboard (dernier run + historique)"""
    try:
        last_run = storage.get_last_run()
        history = storage.list_runs(limit=20)
        stats = storage.get_stats()
        
        return jsonify({
            'last_run': last_run,
            'history': history,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.get("/health")
def health():
    """Endpoint de santé pour vérifier l'état du service"""
    try:
        last_run = storage.get_last_run()
        stats = storage.get_stats()
        
        # Détermine le statut basé sur le dernier run
        status = 'healthy'
        if last_run and last_run['summary']['availability_percent'] < 80:
            status = 'degraded'
        
        return jsonify({
            'status': status,
            'last_run_timestamp': last_run['timestamp'] if last_run else None,
            'total_runs': stats['total_runs'],
            'avg_availability': stats['avg_availability_percent']
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
