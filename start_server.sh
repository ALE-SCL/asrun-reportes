#!/bin/bash
# Script para iniciar AS RUN REPORTES en red local
# Uso: ./start_server.sh

echo "🚀 Iniciando AS RUN REPORTES en red local..."
echo "═══════════════════════════════════════════════════"

# Obtener IP local
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)

echo "📍 Dirección IP local detectada: $LOCAL_IP"
echo "🌐 La aplicación estará disponible en:"
echo "   • Local:     http://localhost:8501"
echo "   • Red Local: http://$LOCAL_IP:8501"
echo ""
echo "📋 Para acceder desde otros dispositivos en la red:"
echo "   1. Asegúrate que estén en la misma red WiFi/LAN"
echo "   2. Usa la URL: http://$LOCAL_IP:8501"
echo "   3. Si hay problemas, verifica el firewall de macOS"
echo ""
echo "⏹️  Para detener el servidor: Ctrl+C"
echo "═══════════════════════════════════════════════════"
echo ""

# Iniciar Streamlit
cd "$(dirname "$0")"
streamlit run utils/app_streamlit.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.enableCORS false \
  --server.enableXsrfProtection false
