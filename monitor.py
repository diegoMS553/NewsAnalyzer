#!/usr/bin/env python3
"""
Monitor ligero para el Financial News Analyzer
Proporciona endpoints básicos para verificar el estado del cron job
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
from config import Config

app = Flask(__name__)

# Template HTML simple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Financial News Analyzer - Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status.ok { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .config { background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .config-item { margin: 5px 0; }
        .timestamp { text-align: center; color: #666; font-size: 0.9em; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Financial News Analyzer</h1>
            <h2>Monitor de Estado</h2>
        </div>
        
        <div class="status {{ status_class }}">
            <strong>Estado:</strong> {{ status_message }}
        </div>
        
        <div class="config">
            <h3>📊 Configuración</h3>
            <div class="config-item"><strong>Cron Job:</strong> Cada 4 horas ({{ cron_schedule }})</div>
            <div class="config-item"><strong>Telegram:</strong> {{ telegram_status }}</div>
            <div class="config-item"><strong>Traducción:</strong> {{ translation_status }}</div>
            <div class="config-item"><strong>Web Scraping:</strong> {{ scraping_status }}</div>
            <div class="config-item"><strong>Noticias por análisis:</strong> {{ max_news }}</div>
            <div class="config-item"><strong>Umbral de sentimiento:</strong> {{ sentiment_threshold }}</div>
        </div>
        
        <div class="config">
            <h3>🔧 Información del Servicio</h3>
            <div class="config-item"><strong>Plataforma:</strong> Render (Cron Job)</div>
            <div class="config-item"><strong>Próxima ejecución:</strong> Automática cada 4 horas</div>
            <div class="config-item"><strong>Comando:</strong> <code>python main.py run-once</code></div>
        </div>
        
        <div class="timestamp">
            Última verificación: {{ timestamp }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Página de estado principal"""
    # Verificar configuración
    telegram_configured = bool(Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID)
    
    # Determinar estado general
    if telegram_configured:
        status_class = "ok"
        status_message = "✅ Configuración completa - Cron job activo"
    else:
        status_class = "warning" 
        status_message = "⚠️ Faltan configuraciones de Telegram"
    
    return render_template_string(HTML_TEMPLATE,
        status_class=status_class,
        status_message=status_message,
        cron_schedule="0 */4 * * *",
        telegram_status="✅ Configurado" if telegram_configured else "❌ No configurado",
        translation_status="✅ Habilitada" if Config.ENABLE_TITLE_TRANSLATION else "❌ Deshabilitada",
        scraping_status="✅ Habilitado" if Config.ENABLE_WEB_SCRAPING else "❌ Deshabilitado",
        max_news=Config.MAX_NEWS_PER_ANALYSIS,
        sentiment_threshold=Config.SENTIMENT_THRESHOLD,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

@app.route('/health')
def health():
    """Endpoint de salud para Render"""
    telegram_configured = bool(Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID)
    
    health_data = {
        'status': 'healthy',
        'service': 'Financial News Analyzer Monitor',
        'timestamp': datetime.now().isoformat(),
        'cron_job': {
            'schedule': '0 */4 * * *',
            'description': 'Ejecuta análisis cada 4 horas',
            'command': 'python main.py run-once'
        },
        'configuration': {
            'telegram_configured': telegram_configured,
            'translation_enabled': Config.ENABLE_TITLE_TRANSLATION,
            'scraping_enabled': Config.ENABLE_WEB_SCRAPING,
            'max_news_per_analysis': Config.MAX_NEWS_PER_ANALYSIS,
            'sentiment_threshold': Config.SENTIMENT_THRESHOLD,
            'render_deployment': Config.RENDER_DEPLOYMENT
        }
    }
    
    return jsonify(health_data)

@app.route('/status')
def status():
    """Endpoint de estado simplificado"""
    return jsonify({
        'status': 'running',
        'service': 'monitor',
        'cron_job_schedule': '0 */4 * * *',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)