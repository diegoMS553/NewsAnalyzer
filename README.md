# 🤖 Financial News Sentiment Analyzer with Telegram Bot

Un analizador avanzado de noticias financieras que utiliza múltiples fuentes de datos para proporcionar análisis de sentimiento en tiempo real con notificaciones por Telegram.

## ✨ Características

- 🔍 **Múltiples Fuentes de Noticias**: Alpha Vantage, NewsAPI, Yahoo Finance, RSS feeds, y Perplexity AI
- 📊 **Análisis de Sentimiento Avanzado**: Evaluación automática con múltiples algoritmos (VADER, TextBlob, análisis financiero específico)
- 🧠 **Análisis de Intensidad**: Detecta lenguaje emocional y palabras de intensidad alta
- 📈 **Análisis Especializado**: Vocabulario específico para mercados financieros y criptomonedas
- 🌍 **Resumen de Mercado IA**: Perplexity AI proporciona evaluación diaria del mercado global
- 📊 **Métricas Avanzadas**: Volatilidad de sentimiento, distribución de confianza, análisis por fuente
- 🤖 **Bot Telegram**: Notificaciones automáticas con formato enriquecido
- 🔗 **Enlaces Clicables**: Acceso directo a artículos originales
- 📈 **Análisis de Tickers**: Seguimiento de menciones de acciones específicas
- 🛡️ **Sistema de Respaldo**: APIs alternativas cuando las principales fallan
- 🌐 **Soporte Multi-idioma**: Traducción automática de títulos

## 📁 Estructura del Proyecto

```
Financial-News-Analyzer/
├── main.py                 # Aplicación principal
├── config.py              # Configuración del sistema
├── news_fetcher.py        # Obtención de noticias
├── sentiment_analyzer.py  # Análisis de sentimientos
├── telegram_bot.py        # Bot de Telegram
├── requirements.txt       # Dependencias
├── .env.example          # Ejemplo de variables de entorno
├── .env                  # Tu configuración (crear)
└── README.md             # Este archivo
```

## 🚀 Instalación Rápida

### 1. Clonar/Descargar el proyecto

Ya tienes los archivos en tu directorio actual.

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

1. Copia el archivo de ejemplo:
```bash
copy .env.example .env
```

2. Edita el archivo `.env` con tus configuraciones:
```env
TELEGRAM_BOT_TOKEN=tu_bot_token_aquí
TELEGRAM_CHAT_ID=tu_chat_id_aquí
NEWS_API_KEY=tu_news_api_key_aquí
```

## 🤖 Configuración del Bot de Telegram

### Paso 1: Crear el Bot

1. Abre Telegram y busca [@BotFather](https://t.me/botfather)
2. Envía `/newbot`
3. Sigue las instrucciones para nombrar tu bot
4. Guarda el **Bot Token** que te proporciona

### Paso 2: Obtener Chat IDs

**Para un solo destinatario:**
1. Busca [@userinfobot](https://t.me/userinfobot) en Telegram
2. Envía `/start`
3. Copia tu **Chat ID**

**Para múltiples destinatarios:**
1. Cada persona debe obtener su propio Chat ID usando el método anterior
2. Combina todos los IDs separados por comas

**Opción B: Método manual**
1. Envía un mensaje a tu bot recién creado
2. Ve a: `https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates`
3. Busca el `"id"` en la respuesta JSON

### Paso 3: Configurar en .env

**Para un solo destinatario (formato tradicional):**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Para múltiples destinatarios (formato nuevo):**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_IDS=123456789,987654321,555666777
```

**⚠️ Importante:** Puedes usar cualquiera de los dos formatos. El sistema detectará automáticamente si tienes uno o múltiples destinatarios.

## 📨 Soporte para Múltiples Destinatarios

El bot puede enviar el mismo análisis a múltiples personas simultáneamente:

✅ **Características del sistema multi-destinatario:**
- 📨 **Envío simultáneo** a todos los chat IDs configurados
- 🛡️ **Tolerancia a fallos** - si un destinatario falla, continúa con los demás
- 📊 **Logs detallados** - muestra éxito/fracaso por destinatario
- 🔄 **Compatibilidad** - funciona con configuración anterior (un solo destinatario)

✅ **Ejemplo de uso:**
```env
# Tú y otras 2 personas reciben el mismo análisis
TELEGRAM_CHAT_IDS=123456789,987654321,555666777
```

✅ **En los mensajes verás:**
```
Mensaje enviado exitosamente a 3/3 destinatarios
```

✅ **Si alguien deja de recibir:**
```
Mensaje enviado exitosamente a 2/3 destinatarios
Error enviando mensaje a chat 555666777: [razón del error]
```

## 🔑 APIs Opcionales (Gratuitas)

### NewsAPI (Opcional pero recomendado)

1. Ve a [NewsAPI.org](https://newsapi.org)
2. Registra una cuenta gratuita (1000 requests/día)
3. Obtén tu API key
4. Agrégala al archivo `.env`:
```env
NEWS_API_KEY=tu_api_key_aquí
```

### Alpha Vantage (Opcional)

1. Ve a [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Obtén tu API key gratuita
3. Agrégala al archivo `.env`:
```env
ALPHA_VANTAGE_API_KEY=tu_api_key_aquí
```

> **Nota**: La aplicación funciona sin estas APIs usando Yahoo Finance y web scraping.

## 🖥️ Uso de la Aplicación

### Comandos Disponibles

```bash
# Probar que todo funcione
python main.py test

# Ejecutar análisis una sola vez
python main.py run-once

# Ver configuración actual
python main.py config

# Ejecutar en modo continuo (por defecto)
python main.py
```

### Modo Continuo (Recomendado)

```bash
python main.py
```

El sistema:
1. Ejecutará pruebas iniciales
2. Enviará una notificación de inicio a Telegram
3. Hará análisis automáticos a las 9:00, 15:00 y 21:00
4. También cada X horas (configurable en `.env`)

## ⚙️ Configuración Avanzada

### Variables de Entorno Completas

```env
# OBLIGATORIO - Telegram
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id

# OPCIONAL - APIs de Noticias
NEWS_API_KEY=tu_news_api_key
ALPHA_VANTAGE_API_KEY=tu_alpha_vantage_key

# CONFIGURACIÓN
ANALYSIS_INTERVAL_HOURS=4        # Cada cuántas horas analizar
SENTIMENT_THRESHOLD=0.1          # Umbral para clasificar sentimiento
MAX_NEWS_PER_ANALYSIS=10         # Máximo artículos por análisis
```
## 📱 Ejemplo de Notificación

El bot te enviará mensajes como este:

```

📰 📊 ANÁLISIS DE NOTICIAS FINANCIERAS 📊

🚀📈🟢 Sentimiento del Mercado: POSITIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 RESUMEN EJECUTIVO
┌─ Artículos Analizados: 12 📰
├─ 🟢 Positivas: 58.3%
├─ 🔴 Negativas: 25.0%
└─ ⚪ Neutrales: 16.7%

🎯 VOLATILIDAD DEL SENTIMIENTO: 0.234
📊 CONFIANZA DEL ANÁLISIS: Alto: 8, Medio: 3, Bajo: 1

🗞️ NOTICIAS DESTACADAS

1. 🟢💚📈 Los mercados bursátiles de EE.UU. suben 🔗
   🔍 Perplexity Sonar - Reuters | 🎯 Confianza: 0.85 | 📊 IA: 🟢
   💰 AAPL, MSFT

2. ⚪💛➖ La Fed mantiene tasas de interés
   📍 Yahoo Finance | 🎯 Confianza: 0.67
   💰 FED, DXY

🌍 RESUMEN DEL MERCADO (IA)
📈🟢 Sentimiento del Día: POSITIVE
💭 Los mercados financieros globales muestran optimismo hoy, con el S&P 500 alcanzando nuevos máximos históricos impulsado por sólidos reportes de ganancias corporativas y datos económicos positivos. El Bitcoin supera los $45,000 por primera vez en meses, mientras que el oro mantiene su tendencia alcista.

📊 FUENTES PRINCIPALES: Alpha Vantage(4), Yahoo Finance(3), Perplexity Sonar(2)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 Análisis generado: 17/10/2024 15:30 UTC
🤖 Powered by Financial News Analyzer
```

## 🔧 Solución de Problemas

### Error: "TELEGRAM_BOT_TOKEN es requerido"

- Verifica que creaste el archivo `.env`
- Asegúrate de que el bot token esté configurado correctamente
- No uses comillas en el archivo `.env`

### Error: "No se obtuvieron noticias"

- Verifica tu conexión a internet
- Considera agregar una NEWS_API_KEY para más fuentes
- El web scraping puede fallar ocasionalmente

### Bot no responde en Telegram

- Verifica que el CHAT_ID sea correcto
- Asegúrate de haber enviado al menos un mensaje al bot
- Prueba con `python main.py test`

### Problemas con dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 📊 Cómo Funciona el Análisis

### Fuentes de Noticias
1. **NewsAPI**: API profesional con múltiples fuentes
2. **Yahoo Finance**: Noticias de índices principales (S&P 500, Dow Jones, NASDAQ)
3. **Web Scraping**: MarketWatch y otras fuentes como respaldo

### Análisis de Sentimientos Avanzado
1. **VADER**: Especializado en texto de redes sociales y lenguaje emocional
2. **TextBlob**: Análisis general de polaridad y subjetividad
3. **Análisis Financiero Específico**: Más de 200 palabras clave financieras y cripto
4. **Análisis de Intensidad**: Detecta lenguaje emocional y palabras de intensidad
5. **Análisis de Criptomonedas**: Vocabulario específico para mercados digitales

### Métricas Avanzadas
- **Volatilidad de Sentimiento**: Qué tan dispersos están los resultados
- **Distribución de Confianza**: Proporción de análisis de alta/media/baja confianza
- **Análisis por Fuente**: Sentimiento promedio por fuente de noticias
- **Impacto por Ticker**: Cómo afectan las noticias a acciones específicas

### Resumen de Mercado IA
- **Evaluación Diaria**: Perplexity AI analiza el estado general del mercado
- **Indicadores Clave**: S&P 500, Dow Jones, NASDAQ, Bitcoin, commodities
- **Sentimiento Global**: POSITIVO, NEGATIVO o NEUTRAL del día
- **Eventos Importantes**: Menciones de eventos económicos relevantes

### Clasificación Final
- Combina múltiples algoritmos con pesos diferenciados
- Calcula confianza basada en consenso entre métodos
- Incluye análisis de intensidad emocional
- Clasifica como: Positivo, Negativo, o Neutral

## 🔄 Ejecutar como Servicio (Windows)

Para que la aplicación se ejecute automáticamente:

1. Crea un archivo `run_analyzer.bat`:
```batch
@echo off
cd "C:\Users\diego\Documents\Investigacion de operaciones\Financial-News-Analyzer"
python main.py
pause
```

2. Agrégalo al inicio de Windows o usa el Programador de Tareas

## 📝 Logs y Monitoreo

La aplicación genera logs en:
- `financial_analyzer.log` - Archivo de log detallado
- Consola - Output en tiempo real

Los logs incluyen:
- Cantidad de noticias obtenidas
- Resultados del análisis de sentimientos
- Errores de conexión o APIs
- Estado de envíos a Telegram

## 🛡️ Seguridad y Privacidad

- **API Keys**: Mantén tu archivo `.env` seguro y nunca lo compartas
- **Bot Token**: Regenera el token si se compromete
- **Chat ID**: Solo tu recibirás las notificaciones
- **Datos**: No se almacenan noticias o análisis localmente

## 🤝 Contribuir

¿Ideas para mejorar? Algunas sugerencias:

- [ ] Agregar más fuentes de noticias
- [ ] Interfaz web para configuración
- [ ] Base de datos para histórico de análisis
- [ ] Alertas por palabras clave específicas
- [ ] Integración con Discord/Slack

## 📄 Licencia

Este proyecto es de código abierto. Úsalo y modifícalo como gustes.

## 🆘 Soporte

Si tienes problemas:

1. Revisa este README
2. Ejecuta `python main.py config` para verificar configuración
3. Ejecuta `python main.py test` para diagnosticar problemas
4. Verifica los logs en `financial_analyzer.log`

---

## 🌟 Nuevas Características Avanzadas

### 🤖 Análisis de Sentimiento Mejorado
- **Más de 200 palabras clave** específicas para mercados financieros y criptomonedas
- **Análisis de intensidad emocional** que detecta lenguaje fuerte y exclamaciones
- **Múltiples algoritmos** combinados (VADER, TextBlob, análisis financiero específico)
- **Ponderación inteligente** con mayor peso para análisis especializados

### 🌍 Resumen de Mercado con IA
- **Evaluación diaria del mercado** proporcionada por Perplexity AI
- **Análisis de índices principales** (S&P 500, Dow Jones, NASDAQ, Bitcoin, etc.)
- **Detección de eventos importantes** del día
- **Sentimiento global** claramente indicado (POSITIVO/NEGATIVO/NEUTRAL)

### 📊 Métricas Avanzadas
- **Volatilidad de sentimiento** para medir consistencia de resultados
- **Distribución de confianza** (alto/media/bajo) de los análisis
- **Análisis por fuente** para comparar confiabilidad
- **Impacto por ticker** para seguimiento específico de acciones

### 🔗 Mejoras en Mensajes de Telegram
- **Indicadores visuales** para diferentes tipos de análisis
- **Resumen de mercado integrado** en cada análisis
- **Métricas de volatilidad y confianza** visibles
- **Formato mejorado** con separadores profesionales

**¡Disfruta recibiendo análisis avanzados de noticias financieras directamente en tu Telegram! 📱💰🧠**