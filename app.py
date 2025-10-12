#!/usr/bin/env python3
"""
Servidor web para Render - Financial News Analyzer
"""

import os
import logging
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request
from config import Config
from main import FinancialNewsAnalyzer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Inicializar el analizador
analyzer = None

def initialize_analyzer():
    """Inicializa el analizador de noticias"""
    global analyzer
    try:
        analyzer = FinancialNewsAnalyzer()
        return True
    except Exception as e:
        logging.error(f"Error inicializando analizador: {e}")
        return False

@app.route('/')
def health_check():
    """Endpoint de health check para Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'Financial News Analyzer',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Endpoint de salud detallado"""
    global analyzer
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'analyzer_initialized': analyzer is not None,
            'alpha_vantage_configured': bool(Config.ALPHA_VANTAGE_API_KEY),
            'telegram_configured': bool(Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID),
            'translation_enabled': Config.ENABLE_TITLE_TRANSLATION,
            'scraping_enabled': Config.ENABLE_WEB_SCRAPING,
            'render_deployment': Config.RENDER_DEPLOYMENT
        }
    }
    
    if analyzer is None:
        health_status['status'] = 'unhealthy'
        health_status['error'] = 'Analyzer not initialized'
    
    return jsonify(health_status)

@app.route('/analyze', methods=['POST'])
def analyze_news():
    """Endpoint para ejecutar análisis de noticias"""
    global analyzer
    
    if analyzer is None:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    try:
        # Ejecutar análisis
        success = analyzer.run_analysis()
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Analysis completed' if success else 'Analysis failed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error en análisis: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/config')
def get_config():
    """Endpoint para obtener configuración (sin datos sensibles)"""
    return jsonify({
        'alpha_vantage_configured': bool(Config.ALPHA_VANTAGE_API_KEY),
        'telegram_configured': bool(Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID),
        'translation_enabled': Config.ENABLE_TITLE_TRANSLATION,
        'translation_language': Config.TRANSLATION_TARGET_LANGUAGE,
        'scraping_enabled': Config.ENABLE_WEB_SCRAPING,
        'render_deployment': Config.RENDER_DEPLOYMENT,
        'analysis_interval_hours': Config.ANALYSIS_INTERVAL_HOURS,
        'max_news_per_analysis': Config.MAX_NEWS_PER_ANALYSIS,
        'sentiment_threshold': Config.SENTIMENT_THRESHOLD
    })

@app.route('/test')
def test_system():
    """Endpoint para probar el sistema"""
    global analyzer
    
    if analyzer is None:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    try:
        # Ejecutar prueba del sistema
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyzer.test_system())
        loop.close()
        
        return jsonify({
            'status': 'success' if result else 'failed',
            'message': 'System test completed',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error en prueba del sistema: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Inicializar el analizador
    if initialize_analyzer():
        logging.info("✅ Analizador inicializado correctamente")
    else:
        logging.error("❌ Error inicializando analizador")
    
    # Ejecutar servidor
    port = Config.PORT
    logging.info(f"🚀 Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
