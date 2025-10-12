import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from config import Config
from deep_translator import GoogleTranslator

class TelegramNotifier:
    """Cliente para enviar notificaciones a Telegram"""
    
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or Config.TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.bot_token) if self.bot_token else None
        self.logger = logging.getLogger(__name__)
        self.translator = GoogleTranslator()
        
    def validate_config(self):
        """Valida la configuración del bot"""
        if not self.bot_token:
            raise ValueError("Bot token es requerido")
        if not self.chat_id:
            raise ValueError("Chat ID es requerido")
        return True
    
    def translate_title(self, title, target_language=None):
        """Traduce el título de una noticia al español"""
        # Verificar si la traducción está habilitada
        if not Config.ENABLE_TITLE_TRANSLATION:
            return title
            
        if not title or len(title.strip()) < 5:
            return title
        
        # Usar el idioma objetivo de la configuración
        if target_language is None:
            target_language = Config.TRANSLATION_TARGET_LANGUAGE
        
        try:
            # Usar deep-translator con Google Translate
            translator = GoogleTranslator(source='auto', target=target_language)
            translation = translator.translate(title)
            
            if translation and translation != title:
                self.logger.debug(f"Título traducido (auto->{target_language}): '{title[:50]}...' -> '{translation[:50]}...'")
                return translation
            else:
                self.logger.debug(f"Título ya está en {target_language} o no se pudo traducir: '{title[:50]}...'")
                return title
                
        except Exception as e:
            self.logger.warning(f"Error traduciendo título '{title[:50]}...': {e}")
        
        # Si hay error, devolver el título original
        return title
    
    async def send_message(self, message, parse_mode=ParseMode.MARKDOWN):
        """Envía un mensaje a Telegram"""
        if not self.bot:
            self.logger.error("Bot no inicializado")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.logger.info("Mensaje enviado exitosamente")
            return True
            
        except TelegramError as e:
            self.logger.error(f"Error enviando mensaje a Telegram: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return False
    
    def format_sentiment_analysis(self, analysis_result):
        """Formatea el resultado del análisis de sentimientos para Telegram"""
        if 'error' in analysis_result:
            return f"❌ **Error en el análisis**: {analysis_result['error']}"
        
        summary = analysis_result.get('summary', {})
        timestamp = analysis_result.get('timestamp', datetime.now().isoformat())
        
        # Emoji según sentimiento general
        sentiment_emoji = {
            'positive': '📈 🟢',
            'negative': '📉 🔴', 
            'neutral': '➖ 🟡'
        }
        
        overall_sentiment = summary.get('overall_sentiment', 'neutral')
        emoji = sentiment_emoji.get(overall_sentiment, '❓')
        
        message = f"""🗞️ **Análisis de Noticias Financieras**

{emoji} **Sentimiento General**: {overall_sentiment.upper()}

📊 **Resumen:**
• Total de artículos: {summary.get('total_articles', 0)}
• Positivas: {summary.get('positive_percentage', 0):.1f}% ({summary.get('sentiment_breakdown', {}).get('positive', 0)})
• Negativas: {summary.get('negative_percentage', 0):.1f}% ({summary.get('sentiment_breakdown', {}).get('negative', 0)})
• Neutrales: {summary.get('neutral_percentage', 0):.1f}% ({summary.get('sentiment_breakdown', {}).get('neutral', 0)})

📰 **Noticias Destacadas:**"""
        
        # Agregar las noticias más relevantes
        analyzed_articles = analysis_result.get('analyzed_articles', [])
        
        # Mostrar más artículos, pero limitar para evitar mensajes muy largos
        max_articles_to_show = min(len(analyzed_articles), 8)  # Mostrar hasta 8 artículos
        
        for i, article_analysis in enumerate(analyzed_articles[:max_articles_to_show]):
            article = article_analysis.get('article', {})
            sentiment_data = article_analysis.get('sentiment_analysis', {})
            final_sentiment = sentiment_data.get('final_sentiment', {}).get('sentiment', 'neutral')
            confidence = sentiment_data.get('confidence', 0)
            
            article_emoji = sentiment_emoji.get(final_sentiment, '❓')
            
            # Traducir el título al español
            original_title = article.get('title', 'Sin título')
            translated_title = self.translate_title(original_title)
            
            message += f"\n\n{i+1}. {article_emoji} **{translated_title[:80]}...**"
            message += f"\n   • Sentimiento: {final_sentiment} ({confidence:.2f} confianza)"
            message += f"\n   • Fuente: {article.get('source', 'Desconocida')}"
            
            # Mostrar tickers mencionados si están disponibles (de Alpha Vantage)
            if 'mentioned_tickers' in article_analysis and article_analysis['mentioned_tickers']:
                tickers = ', '.join(article_analysis['mentioned_tickers'][:3])  # Mostrar máximo 3 tickers
                message += f"\n   • Tickers: {tickers}"
            
            if article.get('url'):
                message += f"\n   • [Leer más]({article['url']})"
        
        # Agregar resumen de fuentes
        sources_summary = self._get_sources_summary(analyzed_articles)
        if sources_summary:
            message += f"\n\n📊 **Fuentes utilizadas:**\n{sources_summary}"
        
        message += f"\n\n🕐 **Análisis realizado**: {datetime.fromisoformat(timestamp[:19]).strftime('%d/%m/%Y %H:%M')}"
        
        return message
    
    def _get_sources_summary(self, analyzed_articles):
        """Genera un resumen de las fuentes utilizadas"""
        source_counts = {}
        for article_analysis in analyzed_articles:
            source = article_analysis.get('article', {}).get('source', 'Desconocida')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        if not source_counts:
            return ""
        
        summary_lines = []
        for source, count in source_counts.items():
            summary_lines.append(f"• {source}: {count} artículo{'s' if count > 1 else ''}")
        
        return '\n'.join(summary_lines)
    
    def format_simple_notification(self, title, content):
        """Formatea una notificación simple"""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        return f"""🤖 **{title}**

{content}

🕐 {timestamp}"""
    
    async def send_sentiment_analysis(self, analysis_result):
        """Envía el resultado del análisis de sentimientos"""
        formatted_message = self.format_sentiment_analysis(analysis_result)
        
        # Telegram tiene límite de 4096 caracteres por mensaje
        if len(formatted_message) > 4000:
            # Dividir en múltiples mensajes
            parts = self._split_message(formatted_message, 4000)
            success = True
            for part in parts:
                result = await self.send_message(part)
                success = success and result
            return success
        else:
            return await self.send_message(formatted_message)
    
    async def send_error_notification(self, error_message):
        """Envía una notificación de error"""
        message = self.format_simple_notification(
            "Error en Análisis de Noticias",
            f"❌ Ha ocurrido un error:\n{error_message}"
        )
        return await self.send_message(message)
    
    async def send_startup_notification(self):
        """Envía notificación de inicio del sistema"""
        message = self.format_simple_notification(
            "Sistema de Análisis Iniciado",
            "✅ El analizador de noticias financieras está funcionando correctamente."
        )
        return await self.send_message(message)
    
    def _split_message(self, message, max_length=4000):
        """Divide un mensaje largo en partes más pequeñas"""
        parts = []
        current_part = ""
        
        lines = message.split('\n')
        
        for line in lines:
            if len(current_part + line + '\n') <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts
    
    async def test_connection(self):
        """Prueba la conexión con Telegram"""
        try:
            self.validate_config()
            
            # Intentar obtener información del bot
            bot_info = await self.bot.get_me()
            self.logger.info(f"Conectado como: {bot_info.first_name} (@{bot_info.username})")
            
            # Enviar mensaje de prueba
            test_message = self.format_simple_notification(
                "Prueba de Conexión",
                "🔄 Probando conexión con Telegram...\n✅ ¡Conexión exitosa!"
            )
            
            success = await self.send_message(test_message)
            return success
            
        except Exception as e:
            self.logger.error(f"Error probando conexión: {e}")
            return False

# Función helper para uso síncrono
def send_telegram_notification(analysis_result, bot_token=None, chat_id=None):
    """Función helper para enviar notificaciones de manera síncrona"""
    async def _send():
        notifier = TelegramNotifier(bot_token, chat_id)
        return await notifier.send_sentiment_analysis(analysis_result)
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop ejecutándose, crear una nueva tarea
            import threading
            result = [None]
            exception = [None]
            
            def run_in_thread():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result[0] = new_loop.run_until_complete(_send())
                    new_loop.close()
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            if exception[0]:
                raise exception[0]
            return result[0]
        else:
            return loop.run_until_complete(_send())
    except:
        # Crear nuevo loop si no existe
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_send())
        finally:
            loop.close()

if __name__ == "__main__":
    # Test del notificador
    import asyncio
    
    async def test_notifier():
        notifier = TelegramNotifier()
        
        # Prueba de conexión
        print("Probando conexión...")
        success = await notifier.test_connection()
        print(f"Conexión {'exitosa' if success else 'fallida'}")
        
        if success:
            # Prueba de análisis ficticio
            test_analysis = {
                'summary': {
                    'total_articles': 3,
                    'overall_sentiment': 'positive',
                    'positive_percentage': 66.7,
                    'negative_percentage': 33.3,
                    'neutral_percentage': 0.0,
                    'sentiment_breakdown': {'positive': 2, 'negative': 1, 'neutral': 0}
                },
                'analyzed_articles': [
                    {
                        'article': {
                            'title': 'Stock Market Reaches New Heights',
                            'source': 'Test News',
                            'url': 'https://example.com'
                        },
                        'sentiment_analysis': {
                            'final_sentiment': {'sentiment': 'positive'},
                            'confidence': 0.85
                        }
                    }
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            print("Enviando análisis de prueba...")
            result = await notifier.send_sentiment_analysis(test_analysis)
            print(f"Envío {'exitoso' if result else 'fallido'}")
    
    asyncio.run(test_notifier())