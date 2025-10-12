# 💰 Financial News Sentiment Analyzer

Una aplicación de Python que analiza automáticamente noticias financieras para determinar si son positivas o negativas, y envía los resultados a través de un bot de Telegram.

## 🌟 Características

- **Múltiples fuentes de noticias**: NewsAPI, Yahoo Finance, y web scraping
- **Análisis de sentimientos avanzado**: Combina VADER, TextBlob y análisis financiero específico
- **Notificaciones en Telegram**: Recibe análisis directamente en tu teléfono
- **Programación automática**: Ejecuta análisis cada pocas horas
- **APIs gratuitas**: Funciona sin costos adicionales

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

### Paso 2: Obtener tu Chat ID

**Opción A: Usando el bot**
1. Busca [@userinfobot](https://t.me/userinfobot) en Telegram
2. Envía `/start`
3. Copia tu **Chat ID**

**Opción B: Método manual**
1. Envía un mensaje a tu bot recién creado
2. Ve a: `https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates`
3. Busca el `"id"` en la respuesta JSON

### Paso 3: Configurar en .env

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
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
🗞️ Análisis de Noticias Financieras

📈 🟢 Sentimiento General: POSITIVE

📊 Resumen:
• Total de artículos: 8
• Positivas: 62.5% (5)
• Negativas: 25.0% (2) 
• Neutrales: 12.5% (1)

📰 Noticias Destacadas:

1. 📈 🟢 Stock Market Reaches Record High...
   • Sentimiento: positive (0.89 confianza)
   • Fuente: Yahoo Finance
   • Leer más

2. 📉 🔴 Inflation Concerns Grow...
   • Sentimiento: negative (0.76 confianza)
   • Fuente: MarketWatch
   • Leer más

🕐 Análisis realizado: 11/10/2024 16:30
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

### Análisis de Sentimientos
1. **VADER**: Especializado en texto de redes sociales
2. **TextBlob**: Análisis general de polaridad
3. **Financiero**: Palabras clave específicas del ámbito financiero

### Clasificación Final
- Combina los tres métodos
- Calcula confianza basada en consenso
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

**¡Disfruta recibiendo análisis de noticias financieras directamente en tu Telegram! 📱💰**