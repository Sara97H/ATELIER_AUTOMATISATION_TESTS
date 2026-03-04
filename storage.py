"""
Storage - Gestion de la base de données SQLite pour historique des runs
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

class TestStorage:
    """Stocke et récupère les résultats de tests dans SQLite"""
    
    DB_FILE = 'test_runs.db'
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self.DB_FILE
        self._init_db()
    
    def _init_db(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des runs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    passed INTEGER,
                    failed INTEGER,
                    total INTEGER,
                    error_rate REAL,
                    latency_ms_avg REAL,
                    latency_ms_p95 REAL,
                    availability_percent REAL,
                    report_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_run(self, report: Dict[str, Any]) -> int:
        """
        Sauvegarde un run de tests
        
        Args:
            report: Dict retourné par TestRunner.run()
            
        Returns:
            ID du run inséré
        """
        summary = report['summary']
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO runs 
                (api, timestamp, passed, failed, total, error_rate, 
                 latency_ms_avg, latency_ms_p95, availability_percent, report_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report['api'],
                report['timestamp'],
                summary['passed'],
                summary['failed'],
                summary['total'],
                summary['error_rate'],
                summary['latency_ms_avg'],
                summary['latency_ms_p95'],
                summary['availability_percent'],
                json.dumps(report)
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_run(self, run_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un run par ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM runs WHERE id = ?', (run_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'api': row['api'],
                    'timestamp': row['timestamp'],
                    'summary': {
                        'passed': row['passed'],
                        'failed': row['failed'],
                        'total': row['total'],
                        'error_rate': row['error_rate'],
                        'latency_ms_avg': row['latency_ms_avg'],
                        'latency_ms_p95': row['latency_ms_p95'],
                        'availability_percent': row['availability_percent']
                    },
                    'report': json.loads(row['report_json'])
                }
            return None
    
    def list_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les derniers runs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, api, timestamp, passed, failed, error_rate, 
                       latency_ms_avg, latency_ms_p95, availability_percent
                FROM runs
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_last_run(self) -> Optional[Dict[str, Any]]:
        """Récupère le dernier run"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM runs
                ORDER BY id DESC
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'api': row['api'],
                    'timestamp': row['timestamp'],
                    'summary': {
                        'passed': row['passed'],
                        'failed': row['failed'],
                        'total': row['total'],
                        'error_rate': row['error_rate'],
                        'latency_ms_avg': row['latency_ms_avg'],
                        'latency_ms_p95': row['latency_ms_p95'],
                        'availability_percent': row['availability_percent']
                    }
                }
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Nombre de runs
            cursor.execute('SELECT COUNT(*) as count FROM runs')
            total_runs = cursor.fetchone()['count']
            
            # Moyennes
            cursor.execute('''
                SELECT 
                    AVG(passed) as avg_passed,
                    AVG(failed) as avg_failed,
                    AVG(error_rate) as avg_error_rate,
                    AVG(latency_ms_avg) as avg_latency,
                    AVG(availability_percent) as avg_availability
                FROM runs
            ''')
            
            row = cursor.fetchone()
            
            return {
                'total_runs': total_runs,
                'avg_passed': round(row['avg_passed'], 2) if row['avg_passed'] else 0,
                'avg_failed': round(row['avg_failed'], 2) if row['avg_failed'] else 0,
                'avg_error_rate': round(row['avg_error_rate'], 3) if row['avg_error_rate'] else 0,
                'avg_latency_ms': round(row['avg_latency'], 2) if row['avg_latency'] else 0,
                'avg_availability_percent': round(row['avg_availability'], 1) if row['avg_availability'] else 0
            }
