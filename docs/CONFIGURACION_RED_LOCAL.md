# 🔥 Configuración de Firewall para Shiki's Report

## 📋 Instrucciones para Permitir Acceso en Red Local

### Opción 1: Configuración Automática (Recomendada)
Cuando inicies el servidor, macOS te preguntará si quieres permitir conexiones. **Selecciona "Permitir"**.

### Opción 2: Configuración Manual del Firewall

1. **Abrir Preferencias del Sistema:**
   - Ve a "Preferencias del Sistema" > "Seguridad y Privacidad"
   - Selecciona la pestaña "Firewall"

2. **Configurar Firewall:**
   - Haz clic en el candado para desbloquear
   - Haz clic en "Opciones del Firewall..."
   - Busca "Python" o "streamlit" en la lista
   - Cambia la configuración a "Permitir conexiones entrantes"

3. **Agregar Regla Específica (si es necesario):**
   - Haz clic en el botón "+"
   - Busca el ejecutable de Python
   - Configúralo para "Permitir conexiones entrantes"

### Opción 3: Firewall por Terminal (Avanzado)
```bash
# Permitir el puerto 8501 específicamente
sudo pfctl -f /etc/pf.conf
```

## 🌐 URLs de Acceso

### En tu Mac (Local):
- http://localhost:8501
- http://127.0.0.1:8501

### Desde otros dispositivos en la red:
- http://10.10.76.42:8501

## 📱 Instrucciones para Usuarios

1. **Conectarse a la misma red WiFi** que el Mac servidor
2. **Abrir navegador web** (Chrome, Safari, Firefox, etc.)
3. **Escribir la URL:** `http://10.10.76.42:8501`
4. **¡Listo!** Ya pueden usar Shiki's Report

## 🔧 Solución de Problemas

### Si no pueden acceder desde otros dispositivos:

1. **Verificar conectividad:**
   ```bash
   ping 10.10.76.42
   ```

2. **Verificar que el puerto esté abierto:**
   ```bash
   telnet 10.10.76.42 8501
   ```

3. **Verificar firewall de macOS:**
   - Sistema > Seguridad y Privacidad > Firewall

4. **Reiniciar el servidor:**
   - Detener: Ctrl+C
   - Iniciar: `./start_server.sh`

## ⚠️ Consideraciones de Seguridad

- ✅ **Red Local:** Seguro para uso en redes privadas/corporativas
- ⚠️ **Internet Público:** NO exponer directamente a internet sin autenticación
- 🔒 **Recomendación:** Usar solo en redes de confianza

## 📧 Compartir Acceso

Para compartir el acceso con colegas:

**Mensaje de ejemplo:**
```
¡Hola! Ya está disponible Shiki's Report:

🌐 URL: http://10.10.76.42:8501
📋 Funciones: Procesar logs AsRun, generar reportes, consultar BD
🔧 Requisitos: Estar en la misma red WiFi

¡Cualquier duda me avisas!
```
