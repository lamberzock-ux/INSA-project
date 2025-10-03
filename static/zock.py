# app.py - ZOCK WITH TRADING SIGNALS
from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Create templates folder
os.makedirs('templates', exist_ok=True)

# Create the dashboard HTML with trading signals
dashboard_html = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>ZOCK Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { background:#050617; color:#e6fbff; font-family: Arial, sans-serif; margin:0; padding:20px; }
    header { display:flex; align-items:center; gap:16px; }
    h1 { color:#00d8ff; margin:0; }
    .top { display:flex; gap:20px; margin-top:16px; }
    .card { background:#0b1220; padding:20px; border-radius:8px; box-shadow:0 6px 14px rgba(0,0,0,0.6); }
    .big { font-size:32px; color:#00ffea; font-weight:bold; }
    table { width:100%; border-collapse:collapse; margin-top:12px; }
    th, td { padding:12px; border-bottom:1px solid #15202b; text-align:left; color:#dff7ff; }
    th { color:#9ef0ff; background:#15202b; }
    button { background:#0088cc; color:white; border:none; padding:10px 16px; border-radius:6px; cursor:pointer; font-size:14px; margin:5px; }
    button:hover { background:#0077bb; }
    .controls { margin-left:auto; display:flex; gap:10px; flex-wrap:wrap; }
    .severity-high { color: #ff4444; font-weight:bold; }
    .severity-medium { color: #ffaa00; font-weight:bold; }
    .severity-critical { color: #ff00ff; font-weight:bold; }
    .status-sent { color: #44ff44; }
    .status-pending { color: #ffaa00; }
    .stats-grid { display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:15px; margin-bottom:20px; }
    .stat-card { text-align:center; }
    .trading-signal-buy { color: #44ff44; font-weight:bold; }
    .trading-signal-sell { color: #ff4444; font-weight:bold; }
    .trading-signal-hold { color: #ffaa00; font-weight:bold; }
    .price-up { color: #44ff44; }
    .price-down { color: #ff4444; }
    .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    @media (max-width: 1200px) { .dashboard-grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>🛡 ZOCK AI Threat Detection</h1>
      <div style="color:#9bdfff">Live Security Monitoring + Trading Signals</div>
    </div>
    <div class="controls">
      <button onclick="generateAlerts()">🚨 Generate Alerts</button>
      <button onclick="testSIEM()">🔗 Test SIEM</button>
      <button onclick="generateTradingSignals()">📈 Trading Signals</button>
      <button onclick="downloadAlerts()">📥 Export Data</button>
    </div>
  </header>

  <div class="stats-grid">
    <div class="card stat-card">
      <div style="font-size:14px;color:#9bdfff">Security Alerts</div>
      <div id="totalAlerts" class="big">0</div>
    </div>
    <div class="card stat-card">
      <div style="font-size:14px;color:#9bdfff">SIEM Alerts</div>
      <div id="siemAlerts" class="big">0</div>
    </div>
    <div class="card stat-card">
      <div style="font-size:14px;color:#9bdfff">Trading Signals</div>
      <div id="tradingSignals" class="big">0</div>
    </div>
    <div class="card stat-card">
      <div style="font-size:14px;color:#9bdfff">Active Profits</div>
      <div id="totalProfit" class="big">$0</div>
    </div>
  </div>

  <div class="dashboard-grid">
    <div class="card">
      <h3 style="margin:0 0 15px 0;color:#9bdfff">Security Threat Distribution</h3>
      <canvas id="threatChart" height="200"></canvas>
    </div>
    <div class="card">
      <h3 style="margin:0 0 15px 0;color:#9bdfff">Trading Performance</h3>
      <canvas id="tradingChart" height="200"></canvas>
    </div>
  </div>

  <div class="dashboard-grid">
    <div class="card">
      <h3 style="margin:0 0 15px 0;color:#9bdfff">Live Security Alerts</h3>
      <table id="alertsTable">
        <thead>
          <tr>
            <th>Time</th>
            <th>Threat Type</th>
            <th>Severity</th>
            <th>Source IP</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <div class="card">
      <h3 style="margin:0 0 15px 0;color:#9bdfff">Live Trading Signals</h3>
      <table id="tradingTable">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Signal</th>
            <th>Price</th>
            <th>Change</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

<script>
let threatChart = null;
let tradingChart = null;
let tradingData = [];
let totalProfit = 0;

// Trading symbols and data
const tradingSymbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA'];
const currentPrices = {};

async function fetchAlerts(){
  const r = await fetch('/api/alerts');
  return r.json();
}

async function fetchTradingSignals(){
  const r = await fetch('/api/trading-signals');
  return r.json();
}

async function refresh(){
  const alerts = await fetchAlerts();
  const tradingSignals = await fetchTradingSignals();
  
  // Update statistics
  document.getElementById('totalAlerts').innerText = alerts.length;
  const siemCount = alerts.filter(a => a.siem_sent).length;
  document.getElementById('siemAlerts').innerText = siemCount;
  document.getElementById('tradingSignals').innerText = tradingSignals.length;
  document.getElementById('totalProfit').innerText = `$${totalProfit}`;

  // Update security alerts table
  const alertsTbody = document.querySelector("#alertsTable tbody");
  alertsTbody.innerHTML = "";
  
  alerts.slice().reverse().forEach(a => {
    const tr = document.createElement('tr');
    const severityClass = `severity-${a.severity?.toLowerCase() || 'medium'}`;
    const statusClass = a.siem_sent ? 'status-sent' : 'status-pending';
    
    tr.innerHTML = `
      <td>${a.timestamp || ''}</td>
      <td><strong>${a.threat_type || ''}</strong></td>
      <td class="${severityClass}">${a.severity || 'Medium'}</td>
      <td>${a.source_ip || ''}</td>
      <td class="${statusClass}">${a.siem_sent ? '✅ Sent' : '⏳ Pending'}</td>
    `;
    alertsTbody.appendChild(tr);
  });

  // Update trading signals table
  const tradingTbody = document.querySelector("#tradingTable tbody");
  tradingTbody.innerHTML = "";
  
  tradingSignals.forEach(signal => {
    const tr = document.createElement('tr');
    const signalClass = `trading-signal-${signal.signal.toLowerCase()}`;
    const changeClass = signal.change >= 0 ? 'price-up' : 'price-down';
    const changeSymbol = signal.change >= 0 ? '↗' : '↘';
    
    tr.innerHTML = `
      <td><strong>${signal.symbol}</strong></td>
      <td class="${signalClass}">${signal.signal} ${signal.signal === 'BUY' ? '🚀' : signal.signal === 'SELL' ? '📉' : '⏸️'}</td>
      <td>$${signal.price.toFixed(2)}</td>
      <td class="${changeClass}">${changeSymbol} ${Math.abs(signal.change).toFixed(2)}%</td>
      <td>${signal.confidence}%</td>
    `;
    tradingTbody.appendChild(tr);
  });

  // Update charts
  updateThreatChart(alerts);
  updateTradingChart(tradingSignals);
}

function updateThreatChart(alerts) {
  const threatCounts = {};
  alerts.forEach(a => { 
    const threat = a.threat_type || 'Unknown';
    threatCounts[threat] = (threatCounts[threat] || 0) + 1; 
  });

  const ctx = document.getElementById('threatChart').getContext('2d');
  
  if (threatChart) {
    threatChart.destroy();
  }

  threatChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(threatCounts),
      datasets: [{
        data: Object.values(threatCounts),
        backgroundColor: ['#ff4444', '#ffaa00', '#44ff44', '#ff00ff', '#0088ff', '#aa00ff'],
        borderColor: '#0b1220',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#bff', font: { size: 12 } }
        }
      }
    }
  });
}

function updateTradingChart(signals) {
  const ctx = document.getElementById('tradingChart').getContext('2d');
  
  // Group signals by type for chart
  const signalCounts = { BUY: 0, SELL: 0, HOLD: 0 };
  signals.forEach(s => signalCounts[s.signal]++);

  if (tradingChart) {
    tradingChart.destroy();
  }

  tradingChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['BUY', 'SELL', 'HOLD'],
      datasets: [{
        label: 'Trading Signals',
        data: [signalCounts.BUY, signalCounts.SELL, signalCounts.HOLD],
        backgroundColor: ['#44ff44', '#ff4444', '#ffaa00'],
        borderColor: ['#44ff44', '#ff4444', '#ffaa00'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: '#bff' },
          grid: { color: '#15202b' }
        },
        x: {
          ticks: { color: '#bff' },
          grid: { color: '#15202b' }
        }
      }
    }
  });
}

async function generateAlerts(){
  const r = await fetch('/api/generate', { method:'POST' });
  const result = await r.json();
  alert(`✅ ${result.message}`);
  await refresh();
}

async function testSIEM(){
  const r = await fetch('/api/test-siem', { method:'POST' });
  const result = await r.json();
  alert(`🔗 ${result.message}`);
  await refresh();
}

async function generateTradingSignals(){
  const r = await fetch('/api/generate-trading', { method:'POST' });
  const result = await r.json();
  
  // Simulate profit calculation
  const profit = (Math.random() * 200 - 50).toFixed(2);
  totalProfit += parseFloat(profit);
  
  alert(`📈 ${result.message}\nProfit: $${profit}`);
  await refresh();
}

async function downloadAlerts(){
  const alerts = await fetchAlerts();
  const signals = await fetchTradingSignals();
  const data = { security_alerts: alerts, trading_signals: signals, total_profit: totalProfit };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; 
  a.download = `zock_data_${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a); 
  a.click(); 
  a.remove();
}

// Initialize trading prices
tradingSymbols.forEach(symbol => {
  currentPrices[symbol] = Math.random() * 1000 + 50;
});

// Start auto-refresh
refresh();
setInterval(refresh, 3000);
</script>
</body>
</html>'''

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

class ZOCKEngine:
    def __init__(self):
        self.conn = sqlite3.connect('zock.db', check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        # Security alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                threat_type TEXT,
                severity TEXT,
                source_ip TEXT,
                owasp_category TEXT,
                log_data TEXT,
                ai_analysis TEXT,
                siem_sent BOOLEAN DEFAULT 0
            )
        ''')
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                signal TEXT,
                price REAL,
                change REAL,
                confidence INTEGER
            )
        ''')
        self.conn.commit()
    
    def generate_sample_alerts(self, count=5):
        threats = [
            {'type': 'SQL Injection', 'severity': 'High', 'owasp': 'A03'},
            {'type': 'XSS Attack', 'severity': 'Medium', 'owasp': 'A03'},
            {'type': 'Brute Force', 'severity': 'High', 'owasp': 'A07'},
            {'type': 'Malware', 'severity': 'Critical', 'owasp': 'A08'},
            {'type': 'Data Theft', 'severity': 'Critical', 'owasp': 'A01'},
            {'type': 'Command Injection', 'severity': 'High', 'owasp': 'A03'}
        ]
        
        for i in range(count):
            threat = random.choice(threats)
            source_ip = f"192.168.1.{random.randint(1, 255)}"
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (timestamp, threat_type, severity, source_ip, owasp_category, log_data, ai_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, threat['type'], threat['severity'], 
                source_ip, threat['owasp'],
                f"Blocked {threat['type']} attempt",
                f"AI detected pattern with {random.randint(85, 99)}% confidence"
            ))
        
        self.conn.commit()
        return count
    
    def generate_trading_signals(self, count=6):
        symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA']
        signals = ['BUY', 'SELL', 'HOLD']
        
        # Clear previous signals
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM trading_signals')
        
        for i in range(count):
            symbol = random.choice(symbols)
            signal = random.choice(signals)
            price = round(random.uniform(50, 1500), 2)
            change = round(random.uniform(-5, 5), 2)
            confidence = random.randint(75, 95)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            cursor.execute('''
                INSERT INTO trading_signals (timestamp, symbol, signal, price, change, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, symbol, signal, price, change, confidence))
        
        self.conn.commit()
        return count
    
    def get_alerts(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alerts ORDER BY timestamp DESC')
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_trading_signals(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM trading_signals ORDER BY timestamp DESC')
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def test_siem_integration(self):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE alerts SET siem_sent = 1 WHERE siem_sent = 0')
        updated = cursor.rowcount
        self.conn.commit()
        return updated
    
    def clear_alerts(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM alerts')
        cursor.execute('DELETE FROM trading_signals')
        self.conn.commit()

zock = ZOCKEngine()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/alerts')
def api_alerts():
    return jsonify(zock.get_alerts())

@app.route('/api/trading-signals')
def api_trading_signals():
    return jsonify(zock.get_trading_signals())

@app.route('/api/generate', methods=['POST'])
def generate_alerts():
    count = zock.generate_sample_alerts(5)
    return jsonify({'message': f'Generated {count} security threats', 'alerts_count': count})

@app.route('/api/generate-trading', methods=['POST'])
def generate_trading_signals():
    count = zock.generate_trading_signals(6)
    return jsonify({'message': f'Generated {count} trading signals', 'signals_count': count})

@app.route('/api/test-siem', methods=['POST'])
def test_siem():
    count = zock.test_siem_integration()
    return jsonify({'message': f'Sent {count} alerts to SIEM platforms', 'alerts_sent': count})

@app.route('/api/clear', methods=['POST'])
def clear_alerts():
    zock.clear_alerts()
    return jsonify({'message': 'All data cleared'})

if __name__ == '__main__':
    print("🚀 ZOCK AI Security + Trading Starting...")
    print("📊 Open: http://localhost:5000")
    print("🎯 Features: Security Alerts + Trading Signals")
    print("💡 Click buttons to generate data!")
    app.run(debug=True, host='0.0.0.0', port=5000)