# Financial News Analyzer - Render Deployment

## 🚀 Despliegue en Render

Este proyecto está optimizado para desplegarse en Render sin usar web scraping, cumpliendo con las políticas de la plataforma.

### 📋 Características para Render

- ✅ **Sin Web Scraping**: Solo usa APIs oficiales
- ✅ **APIs Permitidas**: Alpha Vantage, NewsAPI, Yahoo Finance, RSS Feeds
- ✅ **Traducción Automática**: Títulos traducidos al español
- ✅ **Health Checks**: Endpoints para monitoreo
- ✅ **Configuración Flexible**: Variables de entorno

### 🔧 APIs Utilizadas

1. **Alpha Vantage** (Principal)
   - News & Sentiment API
   - Análisis de sentimiento especializado
   - Hasta 1000 artículos por solicitud

2. **NewsAPI** (Secundaria)
   - API oficial de noticias
   - 1000 requests/día gratis

3. **Yahoo Finance** (Secundaria)
   - API oficial de yfinance
   - Datos de mercado y noticias

4. **RSS Feeds** (Complementaria)
   - WSJ, NASDAQ, Reuters
   - Fuentes oficiales y públicas

### ⚙️ Variables de Entorno Requeridas

```bash
# APIs (Requeridas)
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# APIs (Opcionales)
NEWS_API_KEY=tu_news_api_key_aqui

# Configuración
RENDER=true
ENABLE_WEB_SCRAPING=false
ENABLE_TITLE_TRANSLATION=true
TRANSLATION_TARGET_LANGUAGE=es
ANALYSIS_INTERVAL_HOURS=6
MAX_NEWS_PER_ANALYSIS=8
SENTIMENT_THRESHOLD=0.1
```

### 🌐 Endpoints Disponibles

- `GET /` - Health check básico
- `GET /health` - Estado detallado del sistema
- `GET /config` - Configuración actual (sin datos sensibles)
- `POST /analyze` - Ejecutar análisis de noticias
- `GET /test` - Probar sistema completo

### 📱 Uso del Sistema

1. **Automático**: El sistema ejecuta análisis cada 6 horas
2. **Manual**: Usar endpoint `/analyze` para ejecutar análisis
3. **Monitoreo**: Usar `/health` para verificar estado

### 🔒 Seguridad

- No se almacenan datos sensibles
- Solo APIs oficiales y públicas
- Cumple políticas de Render
- Sin web scraping

### 📊 Fuentes de Noticias

- **Alpha Vantage**: 3-4 artículos (con análisis de sentimiento)
- **NewsAPI**: 2-3 artículos
- **Yahoo Finance**: 2-3 artículos
- **RSS Feeds**: 1-2 artículos

**Total**: 8-12 artículos de 4 fuentes oficiales

### 🚀 Despliegue

1. Conectar repositorio a Render
2. Configurar variables de entorno
3. Deploy automático
4. Monitorear con `/health`

### 📈 Beneficios

- **Cumplimiento**: Sin riesgo de suspensión
- **Confiabilidad**: APIs oficiales y estables
- **Escalabilidad**: Optimizado para cloud
- **Monitoreo**: Health checks integrados
