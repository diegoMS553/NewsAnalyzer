@echo off
echo ========================================
echo Financial News Sentiment Analyzer
echo Instalacion automatica para Windows
echo ========================================
echo.

echo Instalando dependencias de Python...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Error instalando dependencias. Intentando con pip alternativo...
    python -m pip install -r requirements.txt
)

echo.
echo Copiando archivo de configuracion...
copy .env.example .env

echo.
echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo PROXIMOS PASOS:
echo 1. Edita el archivo .env con tu configuracion
echo 2. Agrega tu TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID
echo 3. Ejecuta: python main.py test
echo.
echo Para obtener ayuda detallada, lee README.md
echo.
pause