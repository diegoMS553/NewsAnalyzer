import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from config import Config
from deep_translator import GoogleTranslator
import html

class TelegramNotifier:
    """Cliente para enviar notificaciones a Telegram (soporta múltiples destinatarios)"""

    def __init__(self, bot_token=None, chat_id=None, chat_ids=None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN

        # Obtener valores reales de configuración (no objetos property)
        config_chat_id = getattr(Config, 'TELEGRAM_CHAT_ID', None)
        config_chat_ids = getattr(Config, 'TELEGRAM_CHAT_IDS', None)

        # Usar parámetros proporcionados o configuración
        if chat_id:
            self.chat_id = str(chat_id)  # Asegurar que sea string
        else:
            self.chat_id = config_chat_id  # Ya debería ser string desde .env

        # Para múltiples chat IDs
        if chat_ids:
            self.chat_ids = chat_ids if isinstance(chat_ids, list) else [str(chat_ids)]
        elif config_chat_ids:
            # Procesar TELEGRAM_CHAT_IDS desde configuración
            self.chat_ids = [chat_id.strip() for chat_id in config_chat_ids.split(',') if chat_id.strip()]
        else:
            # Fallback a single chat ID como lista
            self.chat_ids = [self.chat_id] if self.chat_id else []

        self.bot = Bot(token=self.bot_token) if self.bot_token else None
        self.logger = logging.getLogger(__name__)
        self.translator = GoogleTranslator()
        
    def validate_config(self):
        """Valida la configuración del bot"""
        if not self.bot_token:
            raise ValueError("Bot token es requerido")

        # Asegurar que chat_ids sea una lista válida de strings
        if isinstance(self.chat_ids, list):
            chat_ids = [str(chat_id).strip() for chat_id in self.chat_ids if str(chat_id).strip()]
        else:
            chat_ids = [str(self.chat_ids).strip()] if self.chat_ids else []

        if not chat_ids or len(chat_ids) == 0:
            raise ValueError("Al menos un Chat ID es requerido (TELEGRAM_CHAT_ID o TELEGRAM_CHAT_IDS)")
        return True
    
    def escape_html(self, text):
        """Escape caracteres HTML para Telegram"""
        if not text:
            return ""
        return html.escape(str(text))
    
    def truncate_text(self, text, max_length=100):
        """Trunca texto y añade ... si es muy largo"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
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
    
    async def send_message(self, message, parse_mode=ParseMode.HTML):
        """Envía un mensaje a múltiples chat IDs de Telegram con manejo de errores mejorado"""
        if not self.bot:
            self.logger.error("Bot no inicializado")
            return False

        # Si no hay chat_ids específicos, usar la lista de configuración
        if self.chat_ids:
            if isinstance(self.chat_ids, list):
                target_chat_ids = [str(chat_id).strip() for chat_id in self.chat_ids if str(chat_id).strip()]
            else:
                target_chat_ids = [str(self.chat_ids).strip()] if self.chat_ids else []
        else:
            target_chat_ids = [str(self.chat_id).strip()] if self.chat_id else []

        success_count = 0
        total_count = len(target_chat_ids)

        try:
            # Limitar mensaje a 4096 caracteres
            if len(message) > 4096:
                message = message[:4090] + "..."

            # Enviar a todos los chat IDs
            for chat_id in target_chat_ids:
                try:
                    # Asegurar que chat_id sea string válido
                    chat_id_str = str(chat_id).strip()
                    if not chat_id_str:
                        continue

                    await self.bot.send_message(
                        chat_id=chat_id_str,
                        text=message,
                        parse_mode=parse_mode,
                        disable_web_page_preview=True
                    )
                    success_count += 1
                    self.logger.info(f"Mensaje enviado exitosamente a chat {chat_id}")

                except TelegramError as e:
                    self.logger.error(f"Error enviando mensaje a chat {chat_id}: {e}")
                    # Intentar sin formato si falla con HTML
                    try:
                        chat_id_str = str(chat_id).strip()
                        await self.bot.send_message(
                            chat_id=chat_id_str,
                            text=message[:4000],
                            parse_mode=None,
                            disable_web_page_preview=True
                        )
                        success_count += 1
                        self.logger.info(f"Mensaje enviado sin formato a chat {chat_id}")
                    except Exception as e2:
                        self.logger.error(f"Error también sin formato para chat {chat_id}: {e2}")
                except Exception as e:
                    self.logger.error(f"Error inesperado enviando a chat {chat_id}: {e}")

            # Retornar True si al menos un mensaje fue enviado exitosamente
            if success_count > 0:
                self.logger.info(f"Mensaje enviado exitosamente a {success_count}/{total_count} destinatarios")
                return True
            else:
                self.logger.error("No se pudo enviar mensaje a ningún destinatario")
                return False

        except Exception as e:
            self.logger.error(f"Error general enviando mensaje: {e}")
            return False
    
    def format_sentiment_analysis(self, analysis_result):
        """Formatea el resultado del análisis de sentimientos para Telegram con mejor estilo y enlaces"""
        if 'error' in analysis_result:
            return f"❌ <b>Error en el análisis</b>: {self.escape_html(analysis_result['error'])}"

        summary = analysis_result.get('summary', {})
        timestamp = analysis_result.get('timestamp', datetime.now().isoformat())

        # Emoji según sentimiento general con mejor diseño
        sentiment_emoji = {
            'positive': '🚀📈🟢',
            'negative': '⚠️📉🔴',
            'neutral': '⚖️➖🟡'
        }

        overall_sentiment = summary.get('overall_sentiment', 'neutral')
        emoji = sentiment_emoji.get(overall_sentiment, '❓🤔')

        # Encabezado mejorado con formato visual
        message = f"""📰 <b>📊 ANÁLISIS DE NOTICIAS FINANCIERAS</b> 📊

{emoji} <b>Sentimiento del Mercado</b>: {overall_sentiment.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>RESUMEN EJECUTIVO</b>
┌─ Artículos Analizados: {summary.get('total_articles', 0)} 📰
├─ 🟢 Positivas: {summary.get('positive_percentage', 0):.1f}%
├─ 🔴 Negativas: {summary.get('negative_percentage', 0):.1f}%
└─ ⚪ Neutrales: {summary.get('neutral_percentage', 0):.1f}%

🎯 <b>VOLATILIDAD DEL SENTIMIENTO</b>: {summary.get('sentiment_volatility', 0):.3f}
📊 <b>CONFIANZA DEL ANÁLISIS</b>: Alto: {summary.get('confidence_distribution', {}).get('high', 0)}, Medio: {summary.get('confidence_distribution', {}).get('medium', 0)}, Bajo: {summary.get('confidence_distribution', {}).get('low', 0)}

🗞️ <b>NOTICIAS DESTACADAS</b>"""

        # Agregar las noticias más relevantes (máximo 6)
        analyzed_articles = analysis_result.get('analyzed_articles', [])
        max_articles_to_show = min(len(analyzed_articles), 6)

        for i, article_analysis in enumerate(analyzed_articles[:max_articles_to_show]):
            article = article_analysis.get('article', {})
            sentiment_data = article_analysis.get('sentiment_analysis', {})
            final_sentiment = sentiment_data.get('final_sentiment', {}).get('sentiment', 'neutral')
            confidence = sentiment_data.get('confidence', 0)

            # Mejor selección de emojis por sentimiento
            sentiment_emojis = {
                'positive': '🟢💚📈',
                'negative': '🔴❤️📉',
                'neutral': '⚪💛➖'
            }

            # Usar sentimiento de Perplexity si está disponible, sino usar el análisis automático
            display_sentiment = final_sentiment
            if 'perplexity_sentiment' in article_analysis:
                display_sentiment = article_analysis['perplexity_sentiment']

            article_emoji = sentiment_emojis.get(display_sentiment, '⚪💭')

            # Traducir y truncar título
            original_title = article.get('title', 'Sin título')
            translated_title = self.translate_title(original_title)
            display_title = self.truncate_text(self.escape_html(translated_title), 70)

            source = self.escape_html(article.get('source', 'Desconocida'))
            article_url = article.get('url', '')

            # Crear enlace clicable si está disponible
            if article_url and article_url.startswith('http') and len(article_url) > 10:
                # Escapar caracteres especiales en URLs para HTML
                escaped_url = self.escape_html(article_url)
                title_link = f"<a href='{escaped_url}'>{display_title}</a>"
                # Si hay URL, mostrar indicador de enlace
                link_indicator = " 🔗"
            else:
                title_link = f"<b>{display_title}</b>"
                link_indicator = ""

            message += f"\n\n{i+1}. {article_emoji} {title_link}{link_indicator}"

            # Información adicional en línea más compacta
            # Mejorar el formato de fuente para Perplexity
            if 'Perplexity' in source:
                source_display = "🔍 " + source
                # Para artículos de Perplexity, mostrar indicador si no hay URL externa
                if not article_url or not article_url.startswith('http') or len(article_url) <= 10:
                    source_display += " (Resumen IA)"
            else:
                source_display = "📍 " + source

            info_line = f"{source_display}"
            if confidence > 0:
                info_line += f" | 🎯 Confianza: {confidence:.2f}"

            # Agregar indicador si el sentimiento viene de Perplexity
            if 'perplexity_sentiment' in article_analysis:
                sentiment_source = article_analysis['perplexity_sentiment']
                sentiment_display = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'neutral': '⚪'
                }.get(sentiment_source, '⚪')
                info_line += f" | 📊 IA: {sentiment_display}"

            message += f"\n   {info_line}"

            # Mostrar tickers mencionados si están disponibles
            if 'mentioned_tickers' in article_analysis and article_analysis['mentioned_tickers']:
                tickers = ', '.join(article_analysis['mentioned_tickers'][:3])  # Máximo 3 tickers
                message += f"\n   💰 <code>{tickers}</code>"

        # Resumen de fuentes mejorado
        sources_summary = self._get_sources_summary_compact(analyzed_articles)
        if sources_summary:
            message += f"\n\n📊 <b>FUENTES PRINCIPALES:</b> {sources_summary}"

        # Agregar resumen de mercado si está disponible
        if 'market_summary' in analysis_result and analysis_result['market_summary']:
            market_data = analysis_result['market_summary']
            market_sentiment = market_data.get('sentiment', 'neutral')
            market_emoji = {
                'positive': '📈🟢',
                'negative': '📉🔴',
                'neutral': '➖🟡'
            }.get(market_sentiment, '❓')

            message += f"\n\n🌍 <b>RESUMEN DEL MERCADO (IA)</b>"
            message += f"\n{market_emoji} <b>Sentimiento del Día</b>: {market_sentiment.upper()}"

            # Resumen del mercado (limitado para no hacer el mensaje muy largo)
            market_summary = market_data.get('summary', '')
            if len(market_summary) > 300:
                market_summary = market_summary[:297] + "..."

            message += f"\n💭 <i>{market_summary}</i>"

        # Footer mejorado
        analysis_time = datetime.fromisoformat(timestamp[:19]).strftime('%d/%m/%Y %H:%M')
        message += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        message += f"\n🕐 <b>Análisis generado:</b> {analysis_time} UTC"
        message += f"\n🤖 <i>Powered by Financial News Analyzer</i>"

        return message
    
    def _get_sources_summary_compact(self, analyzed_articles):
        """Genera un resumen compacto de las fuentes"""
        source_counts = {}
        for article_analysis in analyzed_articles:
            source = article_analysis.get('article', {}).get('source', 'Desconocida')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        if not source_counts:
            return ""
        
        # Mostrar solo las 3 fuentes principales
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return ", ".join([f"{source}({count})" for source, count in top_sources])
    
    def format_simple_notification(self, title, content):
        """Formatea una notificación simple"""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        return f"""🤖 <b>{self.escape_html(title)}</b>

{self.escape_html(content)}

🕐 <i>{timestamp}</i>"""
    
    async def send_sentiment_analysis(self, analysis_result):
        """Envía el resultado del análisis de sentimientos dividido si es necesario"""
        formatted_message = self.format_sentiment_analysis(analysis_result)
        
        # Si el mensaje es muy largo, dividirlo
        if len(formatted_message) > 3500:
            return await self._send_split_messages(formatted_message)
        else:
            return await self.send_message(formatted_message)
    
    async def _send_split_messages(self, message):
        """Envía mensajes largos divididos en partes"""
        try:
            # Dividir por secciones lógicas
            parts = []
            current_part = ""
            
            lines = message.split('\n')
            
            for line in lines:
                # Si agregar esta línea excede el límite, guardar la parte actual
                if len(current_part + line + '\n') > 3500:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'
            
            if current_part:
                parts.append(current_part.strip())
            
            # Enviar partes numeradas
            success = True
            for i, part in enumerate(parts, 1):
                part_with_header = f"📊 <b>Parte {i}/{len(parts)}</b>\n\n{part}"
                result = await self.send_message(part_with_header)
                success = success and result
                await asyncio.sleep(0.3)  # Pequeña pausa entre mensajes
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando mensajes divididos: {e}")
            # Intentar enviar versión muy corta
            try:
                short_msg = "📊 <b>Análisis completado</b>\n(El reporte completo era muy extenso)"
                return await self.send_message(short_msg)
            except:
                return False
    
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
    
    async def test_connection(self):
        """Prueba la conexión con Telegram enviando a múltiples chat IDs"""
        try:
            self.validate_config()

            # Intentar obtener información del bot
            bot_info = await self.bot.get_me()
            self.logger.info(f"Conectado como: {bot_info.first_name} (@{bot_info.username})")

            # Crear mensaje de prueba con información de múltiples destinatarios
            if isinstance(self.chat_ids, list):
                chat_ids_list = [str(chat_id).strip() for chat_id in self.chat_ids if str(chat_id).strip()]
            else:
                chat_ids_list = [str(self.chat_ids).strip()] if self.chat_ids else []
            chat_count = len(chat_ids_list)
            if chat_count == 1:
                test_content = "🔄 Probando conexión con Telegram...\n✅ ¡Conexión exitosa!"
            else:
                test_content = f"🔄 Probando conexión con Telegram...\n✅ ¡Conexión exitosa!\n📱 Enviando a {chat_count} destinatarios"

            test_message = self.format_simple_notification(
                "Prueba de Conexión",
                test_content
            )

            success = await self.send_message(test_message)
            return success

        except Exception as e:
            self.logger.error(f"Error probando conexión: {e}")
            return False


# Función helper para uso síncrono (MANTENER ESTA VERSIÓN)
def send_telegram_notification(analysis_result, bot_token=None, chat_id=None, chat_ids=None):
    """Función helper para enviar notificaciones de manera síncrona"""
    async def _send():
        notifier = TelegramNotifier(bot_token, chat_id, chat_ids)
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
