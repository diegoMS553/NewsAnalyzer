#!/usr/bin/env python3
"""
Financial News Sentiment Analyzer
Aplicación que analiza noticias financieras y envía los resultados vía Telegram
"""

import logging
import schedule
import time
import asyncio
from datetime import datetime
import sys
import os

# Configurar codificación UTF-8 para Windows
if os.name == 'nt':  # Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Importar módulos locales
from config import Config
from news_fetcher import NewsAggregator
from sentiment_analyzer import FinancialSentimentAnalyzer
from telegram_bot import TelegramNotifier, send_telegram_notification

# Configurar logging con codificación UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_analyzer.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configurar la codificación UTF-8 para el StreamHandler
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
        # En Windows, configurar la codificación de salida para manejar Unicode
        if hasattr(handler.stream, 'reconfigure'):
            handler.stream.reconfigure(encoding='utf-8')
        elif hasattr(sys.stdout, 'buffer'):
            # Alternativa para Python < 3.7 o cuando reconfigure no está disponible
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class FinancialNewsAnalyzer:
    """Aplicación principal para análisis de noticias financieras"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        try:
            Config.validate_config()
            # Usar configuración de scraping basada en variables de entorno
            enable_scraping = Config.ENABLE_WEB_SCRAPING and not Config.RENDER_DEPLOYMENT
            self.news_aggregator = NewsAggregator(enable_scraping=enable_scraping)
            self.sentiment_analyzer = FinancialSentimentAnalyzer()
            self.telegram_notifier = TelegramNotifier()
            
            self.logger.info("Aplicación inicializada correctamente")
        except Exception as e:
            self.logger.error(f"Error inicializando aplicación: {e}")
            raise
    
    def run_analysis(self):
        """Ejecuta un ciclo completo de análisis"""
        self.logger.info("🚀 Iniciando análisis de noticias financieras")
        
        try:
            # 1. Obtener noticias
            self.logger.info("📰 Obteniendo noticias financieras...")
            articles = self.news_aggregator.fetch_all_news()
            
            if not articles:
                self.logger.warning("No se obtuvieron noticias")
                return self._send_no_news_notification()
            
            self.logger.info(f"✅ Obtenidas {len(articles)} noticias")
            
            # 2. Analizar sentimientos
            self.logger.info("🔍 Analizando sentimientos...")
            analysis_result = self.sentiment_analyzer.analyze_multiple_articles(articles)
            
            # 3. Enviar resultados por Telegram
            self.logger.info("📱 Enviando resultados por Telegram...")
            success = send_telegram_notification(analysis_result)
            
            if success:
                self.logger.info("✅ Análisis completado y enviado exitosamente")
            else:
                self.logger.error("❌ Error enviando resultados por Telegram")
            
            return success
            
        except Exception as e:
            error_msg = f"Error durante el análisis: {e}"
            self.logger.error(error_msg)
            self._send_error_notification(error_msg)
            return False
    
    def _send_no_news_notification(self):
        """Envía notificación cuando no hay noticias disponibles"""
        try:
            async def send_notification():
                await self.telegram_notifier.send_error_notification(
                    "No se pudieron obtener noticias financieras en este momento. "
                    "Verifica la conectividad a internet y las APIs."
                )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_notification())
            loop.close()
            return True
        except Exception as e:
            self.logger.error(f"Error enviando notificación de sin noticias: {e}")
            return False
    
    def _send_error_notification(self, error_message):
        """Envía notificación de error por Telegram"""
        try:
            async def send_notification():
                await self.telegram_notifier.send_error_notification(error_message)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_notification())
            loop.close()
        except Exception as e:
            self.logger.error(f"Error enviando notificación de error: {e}")
    
    async def test_system(self):
        """Prueba todos los componentes del sistema"""
        self.logger.info("🧪 Probando sistema...")
        
        # 1. Probar conexión a Telegram
        self.logger.info("Probando conexión a Telegram...")
        telegram_ok = await self.telegram_notifier.test_connection()
        
        if not telegram_ok:
            self.logger.error("❌ Fallo conexión a Telegram")
            return False
        
        # 2. Probar obtención de noticias
        self.logger.info("Probando obtención de noticias...")
        test_articles = self.news_aggregator.fetch_all_news(3)
        news_ok = len(test_articles) > 0
        
        if not news_ok:
            self.logger.warning("⚠️ No se pudieron obtener noticias de prueba")
        else:
            self.logger.info(f"✅ Obtenidas {len(test_articles)} noticias de prueba")
        
        # 3. Probar análisis de sentimientos
        if test_articles:
            self.logger.info("Probando análisis de sentimientos...")
            test_analysis = self.sentiment_analyzer.analyze_multiple_articles(test_articles[:2])
            sentiment_ok = 'error' not in test_analysis
            
            if sentiment_ok:
                self.logger.info("✅ Análisis de sentimientos funcionando")
            else:
                self.logger.error("❌ Error en análisis de sentimientos")
        else:
            sentiment_ok = True  # No podemos probar sin noticias
        
        overall_status = telegram_ok and sentiment_ok
        
        if overall_status:
            self.logger.info("✅ Todas las pruebas del sistema pasaron")
            await self.telegram_notifier.send_startup_notification()
        else:
            self.logger.error("❌ Algunas pruebas del sistema fallaron")
        
        return overall_status
    
    def start_scheduler(self):
        """Inicia el programador de tareas"""
        interval_hours = Config.ANALYSIS_INTERVAL_HOURS
        self.logger.info(f"⏰ Programando análisis cada {interval_hours} horas")
        
        # Programar ejecución periódica
        schedule.every(interval_hours).hours.do(self.run_analysis)
        
        # También programar al inicio
        schedule.every().day.at("09:00").do(self.run_analysis)  # 9 AM
        schedule.every().day.at("15:00").do(self.run_analysis)  # 3 PM
        schedule.every().day.at("21:00").do(self.run_analysis)  # 9 PM
        
        self.logger.info("📅 Horarios programados: 9:00, 15:00, 21:00 y cada {} horas".format(interval_hours))
        
        # Mantener el programa corriendo
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Deteniendo aplicación...")
            asyncio.run(self.telegram_notifier.send_error_notification(
                "Sistema de análisis de noticias financieras detenido manualmente."
            ))

def main():
    """Función principal"""
    print("💰 Financial News Sentiment Analyzer")
    print("=====================================")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            # Modo de prueba
            print("🧪 Ejecutando en modo de prueba...")
            analyzer = FinancialNewsAnalyzer()
            asyncio.run(analyzer.test_system())
            
        elif command == "run-once":
            # Ejecutar análisis una sola vez
            print("🔍 Ejecutando análisis único...")
            analyzer = FinancialNewsAnalyzer()
            analyzer.run_analysis()
            
        elif command == "config":
            # Mostrar configuración
            print("⚙️ Configuración actual:")
            print(f"   Intervalo de análisis: {Config.ANALYSIS_INTERVAL_HOURS} horas")
            print(f"   Máximo artículos por análisis: {Config.MAX_NEWS_PER_ANALYSIS}")
            print(f"   Umbral de sentimiento: {Config.SENTIMENT_THRESHOLD}")
            print(f"   Bot Token configurado: {'✅' if Config.TELEGRAM_BOT_TOKEN else '❌'}")
            print(f"   Chat ID configurado: {'✅' if Config.TELEGRAM_CHAT_ID else '❌'}")
            print(f"   Alpha Vantage API Key: {'✅' if Config.ALPHA_VANTAGE_API_KEY else '❌ (requerido)'}")
            print(f"   NewsAPI Key: {'✅' if Config.NEWS_API_KEY else '❌ (opcional)'}")
            print(f"   Alpha Vantage Prioridad: {'✅' if Config.ALPHA_VANTAGE_PRIORITY else '❌'}")
            print(f"   Tickers por defecto: {', '.join(Config.ALPHA_VANTAGE_DEFAULT_TICKERS)}")
            print(f"   Temas por defecto: {', '.join(Config.ALPHA_VANTAGE_DEFAULT_TOPICS)}")
            print(f"   Traducción de títulos: {'✅' if Config.ENABLE_TITLE_TRANSLATION else '❌'}")
            print(f"   Idioma de traducción: {Config.TRANSLATION_TARGET_LANGUAGE}")
            print(f"   Web scraping: {'✅' if Config.ENABLE_WEB_SCRAPING else '❌'}")
            print(f"   Despliegue Render: {'✅' if Config.RENDER_DEPLOYMENT else '❌'}")
            print(f"   Puerto: {Config.PORT}")
            
        else:
            print("❓ Comandos disponibles:")
            print("   python main.py test      - Probar sistema")
            print("   python main.py run-once  - Ejecutar análisis una vez")
            print("   python main.py config    - Mostrar configuración")
            print("   python main.py          - Ejecutar en modo continuo")
    
    else:
        # Modo continuo (por defecto)
        print("🚀 Iniciando en modo continuo...")
        try:
            analyzer = FinancialNewsAnalyzer()
            
            # Prueba inicial del sistema
            print("Ejecutando pruebas iniciales...")
            system_ok = asyncio.run(analyzer.test_system())
            
            if system_ok:
                print("✅ Sistema listo, iniciando programador...")
                # Ejecutar primer análisis inmediatamente
                analyzer.run_analysis()
                # Iniciar programador
                analyzer.start_scheduler()
            else:
                print("❌ Sistema no está listo. Verifica la configuración.")
                print("💡 Ejecuta 'python main.py config' para revisar la configuración.")
                
        except KeyboardInterrupt:
            print("\n🛑 Aplicación detenida por el usuario")
        except Exception as e:
            print(f"❌ Error fatal: {e}")
            logging.error(f"Error fatal en main: {e}")

if __name__ == "__main__":
    main()