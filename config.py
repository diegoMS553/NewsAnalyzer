import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    TELEGRAM_CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS')  # Para múltiples destinatarios

    @property
    def TELEGRAM_CHAT_ID_LIST(self):
        """Devuelve lista de chat IDs (soporta single y múltiples)"""
        if self.TELEGRAM_CHAT_IDS:
            # Soporta formato: "123456789,987654321" o "123456789"
            return [chat_id.strip() for chat_id in self.TELEGRAM_CHAT_IDS.split(',') if chat_id.strip()]
        elif self.TELEGRAM_CHAT_ID:
            # Formato legacy: single chat ID
            return [self.TELEGRAM_CHAT_ID]
        else:
            return []
    
    # APIs de noticias
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_API_KEY2 = os.getenv('ALPHA_VANTAGE_API_KEY2')
    
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
    
    # Configuración de APIs y timeouts
    API_REQUEST_TIMEOUT = int(os.getenv('API_REQUEST_TIMEOUT', 10))  # segundos
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', 2))  # número de reintentos
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', 2))  # segundos entre reintentos
    API_FALLBACK_TIMEOUT = int(os.getenv('API_FALLBACK_TIMEOUT', 5))  # timeout para fallbacks
    
    # Configuración de Perplexity API
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'sonar')  # Updated model name
    PERPLEXITY_MAX_TOKENS = int(os.getenv('PERPLEXITY_MAX_TOKENS', 1000))
    PERPLEXITY_TEMPERATURE = float(os.getenv('PERPLEXITY_TEMPERATURE', 0.2))  # Más determinístico para noticias
    
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

        # Validar que haya al menos un chat ID (legacy o nuevo formato)
        if cls.TELEGRAM_CHAT_IDS:
            chat_ids = [chat_id.strip() for chat_id in cls.TELEGRAM_CHAT_IDS.split(',') if chat_id.strip()]
        elif cls.TELEGRAM_CHAT_ID:
            chat_ids = [cls.TELEGRAM_CHAT_ID]
        else:
            chat_ids = []

        if not chat_ids:
            raise ValueError("TELEGRAM_CHAT_ID o TELEGRAM_CHAT_IDS es requerido")
        
        # Alpha Vantage es la fuente principal pero no obligatoria si hay otras APIs
        has_alpha_vantage = bool(cls.ALPHA_VANTAGE_API_KEY)
        has_perplexity = bool(cls.PERPLEXITY_API_KEY)
        has_newsapi = bool(cls.NEWS_API_KEY)
        
        if not (has_alpha_vantage or has_perplexity or has_newsapi):
            raise ValueError(
                "Se requiere al menos una API de noticias configurada: "
                "ALPHA_VANTAGE_API_KEY, PERPLEXITY_API_KEY, o NEWS_API_KEY"
            )
        
        return True
