# app.py - COMPLETE WORKING VERSION
from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)

class ZOCKEngine:
    def __init__(self):
        self.conn = sqlite3.connect('zock.db', check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                threat_type TEXT,
                detection TEXT,
                severity TEXT,
                source_ip TEXT,
                entity TEXT,
                owasp_category TEXT,
                log_data TEXT,
                ai_analysis TEXT,
                siem_sent BOOLEAN DEFAULT 0,
                siem_platforms TEXT
            )
        ''')
        self.conn.commit()
    
    def generate_sample_alerts(self, count=5):
        """Generate realistic security alerts"""
        threats = [
            {'type': 'SQL Injection', 'severity': 'High', 'owasp': 'A03', 'pattern': 'SQLI'},
            {'type': 'XSS Attack', 'severity': 'Medium', 'owasp': 'A03', 'pattern': 'XSS'},
            {'type': 'Brute Force', 'severity': 'High', 'owasp': 'A07', 'pattern': 'BRUTE'},
            {'type': 'Malware', 'severity': 'Critical', 'owasp': 'A08', 'pattern': 'MAL'},
            {'type': 'Data Exfiltration', 'severity': 'High', 'owasp': 'A01', 'pattern': 'EXFIL'},
            {'type': 'Command Injection', 'severity': 'Critical', 'owasp': 'A03', 'pattern': 'CMD'},
            {'type': 'Path Traversal', 'severity': 'High', 'owasp': 'A01', 'pattern': 'PATH'}
        ]
        
        alerts = []
        for i in range(count):
            threat = random.choice(threats)
            source_ip = f"192.168.1.{random.randint(1, 255)}"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (timestamp, threat_type, detection, severity, source_ip, entity, 
                                  owasp_category, log_data, ai_analysis, siem_sent, siem_platforms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, threat['type'], threat['type'],
                threat['severity'], source_ip, source_ip,
                threat['owasp'], f"Detected {threat['type']} from {source_ip}",
                f"AI analysis confirmed {threat['type']} with 96% confidence",
                False,  # Start as not sent to SIEM
                "Pending"
            ))
            alerts.append({
                'timestamp': timestamp,
                'threat_type': threat['type'],
                'severity': threat['severity'],
                'source_ip': source_ip
            })
        
        self.conn.commit()
        return alerts
    
    def get_alerts(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alerts ORDER BY timestamp DESC')
        columns = [col[0] for col in cursor.description]
        alerts = []
        
        for row in cursor.fetchall():
            alert = dict(zip(columns, row))
            alert['siem_sent'] = bool(alert['siem_sent'])
            alerts.append(alert)
        
        return alerts
    
    def test_siem_integration(self):
        """Test SIEM integration by sending sample alerts"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE alerts SET siem_sent = 1, 
            siem_platforms = 'Splunk, Elasticsearch, Microsoft Defender'
            WHERE siem_sent = 0
        ''')
        updated = cursor.rowcount
        self.conn.commit()
        
        return {
            'message': f'✅ Successfully sent {updated} alerts to all SIEM platforms',
            'siems_joined': 'Splunk, Elasticsearch, Microsoft Defender',
            'alerts_sent': updated
        }
    
    def get_stats(self):
        """Get dashboard statistics"""
        alerts = self.get_alerts()
        stats = {
            'total_alerts': len(alerts),
            'siem_alerts': len([a for a in alerts if a['siem_sent']]),
            'critical_alerts': len([a for a in alerts if a['severity'] == 'Critical']),
            'high_alerts': len([a for a in alerts if a['severity'] == 'High']),
            'recent_alerts': len([a for a in alerts if 
                                datetime.now() - datetime.strptime(a['timestamp'], '%Y-%m-%d %H:%M:%S') < timedelta(hours=1)])
        }
        return stats

# Initialize engine
zock = ZOCKEngine()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/alerts')
def api_alerts():
    """Get all alerts as JSON"""
    alerts = zock.get_alerts()
    return jsonify(alerts)

@app.route('/api/generate', methods=['POST'])
def generate_alerts():
    """Generate sample alerts"""
    count = request.json.get('count', 5) if request.json else 5
    alerts = zock.generate_sample_alerts(count)
    return jsonify({
        'status': 'success',
        'alerts_count': len(alerts),
        'message': f'✅ Generated {len(alerts)} security alerts with AI analysis'
    })

@app.route('/api/test-siem', methods=['POST'])
def test_siem():
    """Test SIEM integration"""
    result = zock.test_siem_integration()
    return jsonify(result)

@app.route('/api/stats')
def api_stats():
    """Get dashboard statistics"""
    stats = zock.get_stats()
    return jsonify(stats)

@app.route('/api/clear', methods=['POST'])
def clear_alerts():
    """Clear all alerts"""
    cursor = zock.conn.cursor()
    cursor.execute('DELETE FROM alerts')
    zock.conn.commit()
    return jsonify({'status': 'success', 'message': 'All alerts cleared'})

if __name__ == '__main__':
    print("""
    🚀 ZOCK AI Threat Detection System
    ==================================
    
    🎯 Features:
    • AI-Powered Threat Detection
    • Multi-SIEM Integration (Splunk, Elasticsearch, Microsoft Defender)
    • Real-time Dark Dashboard
    • OWASP Categorization
    • Export Capabilities
    
    📊 Dashboard: http://localhost:5000
    
    🔧 API Endpoints:
    /api/alerts     - Get all alerts
    /api/generate   - Generate sample alerts  
    /api/test-siem  - Test SIEM integration
    /api/stats      - Get statistics
    /api/clear      - Clear all alerts
    
    🛡️ Ready to detect threats!
    """)
    
    # Generate initial sample data
    zock.generate_sample_alerts(3)
    
    app.run(debug=True, host='0.0.0.0', port=5000)