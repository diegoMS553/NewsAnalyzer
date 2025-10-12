# 🚀 Despliegue en Render - Financial News Analyzer

## 📋 Configuración de Variables de Entorno

Para desplegar correctamente el Financial News Analyzer en Render, necesitas configurar las siguientes variables de entorno en tu dashboard de Render:

### ✅ Variables Obligatorias

#### Telegram Bot Configuration
```
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```
- **TELEGRAM_BOT_TOKEN**: Token del bot de Telegram (obtener de @BotFather)
- **TELEGRAM_CHAT_ID**: ID del chat donde se enviarán los resultados

#### Configuración Básica
```
RENDER=true
ENABLE_WEB_SCRAPING=false
ENABLE_TITLE_TRANSLATION=true
TRANSLATION_TARGET_LANGUAGE=es
```

### 🔧 Variables Opcionales

#### API Keys Externas
```
# Opcional - Para datos financieros adicionales
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui

# Opcional - Para más noticias
NEWS_API_KEY=tu_news_api_key_aqui
```

#### Configuración de Análisis
```
ANALYSIS_INTERVAL_HOURS=4
MAX_NEWS_PER_ANALYSIS=8
SENTIMENT_THRESHOLD=0.1
```

## 🕐 Configuración del Cron Job

El `render.yaml` está configurado para ejecutar un cron job cada 4 horas:

```yaml
schedule: "0 */4 * * *"
```

**Horarios de ejecución (UTC):**
- 00:00 UTC (Medianoche)
- 04:00 UTC (4:00 AM)
- 08:00 UTC (8:00 AM)
- 12:00 UTC (12:00 PM)
- 16:00 UTC (4:00 PM)
- 20:00 UTC (8:00 PM)

## 📝 Pasos para Despliegue

### 1. Preparar el Repositorio
```bash
git add .
git commit -m "Configuración para despliegue en Render"
git push origin main
```

### 2. Crear el Servicio en Render

1. Ve a [render.com](https://render.com) y crea una cuenta
2. Conecta tu repositorio de GitHub
3. Render detectará automáticamente el `render.yaml`
4. Se crearán 2 servicios:
   - **financial-news-analyzer-cron** (Cron Job)
   - **financial-news-monitor** (Web Service - Opcional)

### 3. Configurar Variables de Entorno

En el dashboard de Render, para **cada servicio**, agrega las variables de entorno:

#### Para el Cron Job (financial-news-analyzer-cron):
- Agregar TODAS las variables listadas arriba
- Este es el servicio principal que ejecuta el análisis

#### Para el Monitor (financial-news-monitor):
- Solo necesita `RENDER=true` y las variables básicas
- Este servicio proporciona un dashboard web

### 4. Verificar el Despliegue

1. **Cron Job**: Verifica que se ejecute correctamente en los logs
2. **Monitor**: Visita la URL del servicio web para ver el dashboard
3. **Telegram**: Verifica que los mensajes lleguen correctamente

## 🎯 Ventajas del Cron Job vs Web Service

### ❌ Web Service (Plan Gratuito)
- Se suspende después de 15 minutos de inactividad
- Necesita tráfico constante para mantenerse activo
- Consumo innecesario de recursos

### ✅ Cron Job (Plan Gratuito)
- **NO se suspende** - se ejecuta automáticamente
- Ejecución programada y confiable
- Consumo eficiente de recursos
- Ideal para tareas de análisis periódico

## 📊 Monitoreo y Debugging

### Logs del Cron Job
- Ve a tu dashboard de Render
- Selecciona el servicio `financial-news-analyzer-cron`
- Revisa los logs en la sección "Logs"

### Dashboard Web (Monitor)
- Accede a la URL del servicio `financial-news-monitor`
- Verifica el estado de la configuración
- Revisa la información del cron job

### Endpoints de Monitoreo
```
https://tu-monitor-url.onrender.com/         # Dashboard visual
https://tu-monitor-url.onrender.com/health   # Estado JSON
https://tu-monitor-url.onrender.com/status   # Estado simplificado
```

## 🛠️ Troubleshooting

### El cron job no se ejecuta
1. Verifica que todas las variables de entorno estén configuradas
2. Revisa los logs para errores de configuración
3. Asegúrate de que el `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` sean correctos

### No llegan mensajes de Telegram
1. Verifica el token del bot con @BotFather
2. Confirma el Chat ID enviando `/start` al bot
3. Revisa los logs para errores de API de Telegram

### Errores de API
1. Verifica que las API keys sean válidas y tengan límites disponibles
2. Los servicios gratuitos (NewsAPI, yfinance) pueden tener limitaciones

## 🔄 Modificar la Frecuencia

Para cambiar la frecuencia del cron job, modifica en `render.yaml`:

```yaml
# Cada 2 horas
schedule: "0 */2 * * *"

# Cada 6 horas  
schedule: "0 */6 * * *"

# Diario a las 9:00 AM UTC
schedule: "0 9 * * *"

# Dos veces al día (9 AM y 9 PM UTC)
schedule: "0 9,21 * * *"
```

## 📈 Optimización de Recursos

El cron job está optimizado para el plan gratuito de Render:
- Ejecución cada 4 horas (6 veces al día)
- Máximo 8 noticias por análisis
- Web scraping deshabilitado por defecto
- Timeouts configurados para evitar colgarse

## 🎉 ¡Listo para Producción!

Una vez configurado, tu Financial News Analyzer:
- ✅ Se ejecutará automáticamente cada 4 horas
- ✅ No se suspenderá como los web services
- ✅ Enviará análisis de noticias por Telegram
- ✅ Tendrá un dashboard web para monitoreo