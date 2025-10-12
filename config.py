import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # APIs de noticias
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    # Configuración Alpha Vantage
    ALPHA_VANTAGE_PRIORITY = os.getenv('ALPHA_VANTAGE_PRIORITY', 'true').lower() == 'true'
    ALPHA_VANTAGE_DEFAULT_TICKERS = os.getenv('ALPHA_VANTAGE_DEFAULT_TICKERS', 'ORCL,MSFT,GOOGL,TSLA,NVDA,BTC,ETH,XRP,SOL,DOGE,NSDQ,DJI,S&P500').split(',')
    ALPHA_VANTAGE_DEFAULT_TOPICS = os.getenv('ALPHA_VANTAGE_DEFAULT_TOPICS', 'technology,financial_markets').split(',')
    
    # Configuración de traducción
    ENABLE_TITLE_TRANSLATION = os.getenv('ENABLE_TITLE_TRANSLATION', 'true').lower() == 'true'
    TRANSLATION_TARGET_LANGUAGE = os.getenv('TRANSLATION_TARGET_LANGUAGE', 'es')
    
    # Configuración para Render/Producción
    ENABLE_WEB_SCRAPING = os.getenv('ENABLE_WEB_SCRAPING', 'false').lower() == 'true'
    RENDER_DEPLOYMENT = os.getenv('RENDER', 'false').lower() == 'true'
    PORT = int(os.getenv('PORT', 8000))
    
    # Configuración de análisis
    ANALYSIS_INTERVAL_HOURS = int(os.getenv('ANALYSIS_INTERVAL_HOURS', 4))
    SENTIMENT_THRESHOLD = float(os.getenv('SENTIMENT_THRESHOLD', 0.1))
    MAX_NEWS_PER_ANALYSIS = int(os.getenv('MAX_NEWS_PER_ANALYSIS', 10))
    
    # URLs de noticias financieras gratuitas
    FINANCIAL_NEWS_SOURCES = [
        'https://finance.yahoo.com/news/',
        'https://www.marketwatch.com/',
        'https://www.investing.com/news/stock-market-news',
    ]
    
    # Palabras clave para filtrar noticias financieras
    FINANCIAL_KEYWORDS = [
        'stock', 'market', 'trading', 'investment', 'financial', 'economy',
        'earnings', 'revenue', 'profit', 'loss', 'bull', 'bear', 'inflation',
        'fed', 'interest rate', 'nasdaq', 'dow jones', 's&p 500', 'crypto',
        'bitcoin', 'forex', 'commodity', 'oil', 'gold'
    ]
    
    @classmethod
    def validate_config(cls):
        """Valida que la configuración esté completa"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN es requerido")
        if not cls.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID es requerido")
        if not cls.ALPHA_VANTAGE_API_KEY:
            raise ValueError("ALPHA_VANTAGE_API_KEY es requerido para el análisis de noticias")
        return True