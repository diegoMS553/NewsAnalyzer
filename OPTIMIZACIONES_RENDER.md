# Optimizaciones para Reducir Costos en Render

## Resumen de Cambios Implementados

### 1. **Configuraciones de Timeout y Reintentos**

#### Variables de Entorno Nuevas:
```bash
# Timeout para requests de APIs (segundos)
API_REQUEST_TIMEOUT=10

# Número máximo de reintentos por API
API_MAX_RETRIES=2

# Delay entre reintentos (segundos)
API_RETRY_DELAY=2

# Timeout para operaciones de fallback (segundos)
API_FALLBACK_TIMEOUT=5
```

#### Beneficios:
- **Reduce tiempo de ejecución**: Las APIs que no responden se abandonan rápidamente
- **Evita bucles infinitos**: Límite máximo de reintentos por API
- **Control de costos**: Menor tiempo de ejecución = menores costos en Render

### 2. **Optimizaciones de APIs Existentes**

#### Alpha Vantage API:
- ❌ **Eliminada recursión infinita** en rate limits
- ✅ **Timeout de 10 segundos** (configurable)
- ✅ **Máximo 2 reintentos** por solicitud
- ✅ **Abandono inmediato** en rate limits para evitar costos extra

#### NewsAPI:
- ✅ **Timeout optimizado** a 10 segundos
- ✅ **Reintentos controlados** con delay
- ✅ **Validación mejorada** de respuestas

#### Yahoo Finance:
- ✅ **Timeout reducido** de 15s a 5s para fallbacks
- ✅ **Mejor manejo de errores** JSON
- ✅ **Socket timeout** configurable

#### Web Scraping (MarketWatch, Investing.com):
- ✅ **Timeout reducido** de 20s a 5s
- ✅ **Abandono rápido** en errores HTTP
- ✅ **Solo habilitado** cuando `ENABLE_WEB_SCRAPING=true`

#### RSS Feeds:
- ✅ **Timeout optimizado** a 10 segundos
- ✅ **Mejor manejo** de feeds no disponibles

### 3. **Nueva API: Perplexity Sonar**

#### Variables de Entorno para Perplexity:
```bash
# API Key de Perplexity
PERPLEXITY_API_KEY=your_api_key_here

# Modelo optimizado para búsquedas web
PERPLEXITY_MODEL=sonar-small-online

# Tokens máximos (controla costo)
PERPLEXITY_MAX_TOKENS=1000

# Temperatura para determinismo
PERPLEXITY_TEMPERATURE=0.2
```

#### Características:
- 🔍 **Búsqueda web en tiempo real** con filtrado avanzado
- 📰 **Especializada en noticias actuales** y análisis de mercado
- ⚡ **Timeouts optimizados** (10s máximo)
- 💰 **Control de costos** via max_tokens
- 🤖 **Parsing inteligente** de contenido estructurado

#### Ventajas sobre otras APIs:
1. **Noticias más actuales**: Acceso a web en tiempo real
2. **Mejor agregación**: Combina múltiples fuentes automáticamente
3. **Análisis contextual**: Entiende el contexto financiero
4. **Menos limitada**: No tiene restricciones de rate limit como Alpha Vantage

### 4. **Sistema de Cuotas Inteligente**

#### Distribución Automática:
```python
# Si tienes Alpha Vantage + Perplexity + NewsAPI + Yahoo
total_sources = 4
base_quota = max_articles // total_sources

# Si solo tienes Alpha Vantage + Yahoo
total_sources = 2
base_quota = max_articles // total_sources
```

#### Beneficios:
- ⚖️ **Balanceo automático** entre fuentes disponibles
- 🚫 **No desperdicio** de cuotas en APIs no configuradas
- 🎯 **Optimización dinámica** según APIs disponibles

### 5. **Validación de Configuración Flexible**

#### Antes:
- ❌ Alpha Vantage era obligatorio

#### Ahora:
- ✅ **Al menos una API** de noticias es requerida
- ✅ **Múltiples opciones**: Alpha Vantage, Perplexity, o NewsAPI
- ✅ **Yahoo Finance y RSS** siempre disponibles como fallback

### 6. **Prevención de Costos Extra**

#### Rate Limits:
- ❌ **Eliminadas esperas de 60 segundos** en Alpha Vantage
- ✅ **Abandono inmediato** cuando hay rate limit
- ⚠️ **Logging claro** cuando se salta una API

#### Timeouts Agresivos:
- 🕐 **10 segundos máximo** para APIs principales
- 🕐 **5 segundos máximo** para operaciones de fallback
- 🔄 **Máximo 2 reintentos** por operación

#### Manejo de Errores:
- 🚨 **Fallo rápido** en errores de conexión
- 📝 **Logging detallado** para debugging
- 🔄 **Continuación automática** con otras fuentes

## Instrucciones de Configuración

### Variables de Entorno Recomendadas para Render:

```bash
# APIs (configura al menos una)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
PERPLEXITY_API_KEY=your_perplexity_key
NEWS_API_KEY=your_newsapi_key

# Telegram (requerido)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optimizaciones de rendimiento
API_REQUEST_TIMEOUT=8
API_MAX_RETRIES=1
API_RETRY_DELAY=1
API_FALLBACK_TIMEOUT=4
MAX_NEWS_PER_ANALYSIS=8

# Web scraping (deshabilitado en producción)
ENABLE_WEB_SCRAPING=false
RENDER_DEPLOYMENT=true
```

### Para Desarrollo Local:
```bash
# Permitir más tiempo y reintentos
API_REQUEST_TIMEOUT=15
API_MAX_RETRIES=3
API_RETRY_DELAY=3
ENABLE_WEB_SCRAPING=true
```

## Estimación de Reducción de Costos

### Antes:
- ⏱️ **Tiempo promedio**: 2-5 minutos por ejecución
- 🔄 **Rate limits**: Esperas de 60+ segundos
- 🐌 **Timeouts largos**: 15-20 segundos por API
- ♾️ **Posibles bucles infinitos** en recursión

### Después:
- ⏱️ **Tiempo promedio**: 30-60 segundos por ejecución
- ⚡ **Rate limits**: Abandono inmediato (0 segundos)
- 🚀 **Timeouts cortos**: 5-10 segundos por API
- 🛑 **Límites estrictos**: Máximo 2 reintentos

### Reducción Estimada:
- 📉 **60-80% menos tiempo** de ejecución
- 💰 **60-80% menos costo** en Render
- 🎯 **Mayor confiabilidad** del sistema

## Monitoreo Recomendado

### Logs a Observar:
- `"Rate limit detectado - saltando esta solicitud"` ✅ Comportamiento esperado
- `"API falló después de X intentos"` ⚠️ API no disponible
- `"timeout/connection error"` ⚠️ Problemas de red
- `"Obtenidos X artículos de Perplexity"` ✅ Nueva fuente funcionando

### Métricas de Éxito:
- Tiempo total de ejecución < 90 segundos
- Al menos 5-8 artículos obtenidos
- No más de 2 reintentos por API
- Logs sin errores de timeout > 10 segundos