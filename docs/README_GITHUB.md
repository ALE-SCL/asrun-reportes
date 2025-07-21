# AsRun Report Generator v2.3.0

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.45.1-red.svg)
![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Sistema completo para procesamiento de logs AsRun de televisión y generación automática de reportes de publicidad comercial con interfaz web moderna.

## 🌟 Características Principales

### 🎯 Procesamiento Inteligente
- **Procesamiento automático** de archivos .txt AsRun
- **Filtrado inteligente** de emisiones comerciales (IDs "COM")
- **Normalización automática** de nombres de marcas y clientes
- **Sistema anti-duplicados** con detección en tiempo real
- **Consideración de día televisivo** (6:00 AM a 5:59 AM)

### 📊 Interfaz Web Moderna (Streamlit)
- **Dashboard interactivo** con métricas en tiempo real
- **Drag & Drop** para subida de archivos
- **Consultas avanzadas** con filtros múltiples
- **Generación de reportes** personalizados
- **Gestor de descargas** con descarga masiva
- **Panel de administración** completo

### 📁 Múltiples Formatos de Salida
- **Reportes TXT** tradicionales
- **Archivos Excel** con múltiples hojas
- **Exportación CSV** para análisis
- **Descarga ZIP** para reportes masivos

### 🗄️ Base de Datos Integrada
- **SQLite** para almacenamiento eficiente
- **Consultas rápidas** con indexación optimizada
- **Backup automático** y herramientas de mantenimiento
- **Integridad de datos** garantizada

## 🚀 Instalación Rápida

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/ALE-SCL/asrun-report-generator.git
cd asrun-report-generator
```

### 2. Crear Entorno Virtual (Recomendado)
```bash
python -m venv venv

# En macOS/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación Web
```bash
streamlit run app_streamlit.py
```

La aplicación estará disponible en `http://localhost:8501`

## 📖 Uso del Sistema

### Interfaz Web (Recomendado)
1. **Ejecutar**: `streamlit run app_streamlit.py`
2. **Abrir navegador**: http://localhost:8501
3. **Navegar** por las diferentes secciones:
   - 🏠 **Dashboard**: Métricas y gráficos
   - 📁 **Procesar Archivos**: Subir y procesar logs AsRun
   - 🔍 **Consultar BD**: Búsquedas avanzadas
   - 📋 **Generar Reportes**: Reportes personalizados
   - 📥 **Descargar Reportes**: Gestión de archivos
   - ⚙️ **Administración**: Configuración y mantenimiento

### Línea de Comandos
```bash
# Procesar archivos AsRun
python src/procesar_asrun.py data/

# Consultas rápidas
python consulta_rapida.py

# Consultas con filtros
python src/consultar_bd.py
```

## 📁 Estructura del Proyecto

```
asrun-report-generator/
├── 📱 app_streamlit.py          # Interfaz web principal
├── 📋 requirements.txt          # Dependencias Python
├── 📚 README.md                 # Documentación
├── 📂 src/                      # Código fuente
│   ├── 🔧 procesar_asrun.py     # Procesador principal
│   ├── 🗄️ database_manager.py   # Gestor de BD
│   ├── 🔍 consultar_bd.py       # Consultor de BD
│   └── 📊 asrun_database.db     # Base de datos SQLite
├── 📂 data/                     # Archivos AsRun de entrada
│   └── 📄 *.txt                 # Logs AsRun
├── 📂 reportes/                 # Reportes generados
│   ├── 📄 *.txt                 # Reportes texto
│   └── 📊 *.xlsx                # Reportes Excel
└── 📂 docs/                     # Documentación adicional
```

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env` con:
```env
# Base de datos
DATABASE_PATH=src/asrun_database.db

# Configuración de reportes
REPORTS_DIR=reportes
BACKUP_DIR=backups

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Configuración de Streamlit
Archivo `.streamlit/config.toml`:
```toml
[server]
port = 8501
address = "localhost"

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

## 📊 Formato de Datos

### Entrada (Logs AsRun)
```
Date      Time     Duration  ID              Name                    
20250528  06:00:15  30       COM001          COCA COLA PUBLICIDAD    
20250528  06:05:30  15       COM002          PEPSI MARKETING         
```

### Salida (Reportes)
- **TXT**: Formato tradicional legible
- **Excel**: Múltiples hojas con análisis
- **CSV**: Para importación a otros sistemas

## 🛠️ Desarrollo

### Ejecutar Pruebas
```bash
python -m pytest tests/
```

### Crear Nueva Funcionalidad
1. Crear rama: `git checkout -b feature/nueva-funcionalidad`
2. Desarrollar y probar
3. Commit: `git commit -m "feat: descripción"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estructura de Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de errores
- `docs:` Documentación
- `style:` Formato de código
- `refactor:` Refactorización
- `test:` Pruebas
- `chore:` Mantenimiento

## 📈 Características Técnicas

### Rendimiento
- **Procesamiento**: 10,000+ registros/minuto
- **Base de datos**: Indexación optimizada
- **Memoria**: Procesamiento por lotes eficiente
- **Interfaz**: Carga asíncrona y cache inteligente

### Seguridad
- **Validación** de datos de entrada
- **Sanitización** de nombres de archivo
- **Backup automático** de base de datos
- **Logs** de auditoría completos

### Escalabilidad
- **Arquitectura modular** para extensiones
- **APIs internas** para integración
- **Configuración flexible** por entorno
- **Soporte multi-usuario** (futuro)

## 🤝 Contribuir

1. **Fork** el proyecto
2. **Crear** rama feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Crear** Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

### Problemas Comunes
- **Error de conexión BD**: Verificar permisos de archivo
- **Archivos no procesados**: Revisar formato de entrada
- **Interfaz no carga**: Verificar dependencias Streamlit

### Contacto
- **Issues**: [GitHub Issues](https://github.com/ALE-SCL/asrun-report-generator/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/ALE-SCL/asrun-report-generator/wiki)

## 🏆 Reconocimientos

- **Streamlit** por la fantástica plataforma web
- **SQLite** por la base de datos robusta
- **Pandas** por el procesamiento de datos
- **Plotly** por las visualizaciones

---

**AsRun Report Generator v2.3.0** - Desarrollado con ❤️ para la industria televisiva
