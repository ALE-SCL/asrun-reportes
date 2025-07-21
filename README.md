# AS RUN REPORTES

Sistema integral para procesar logs de emisión de TV (AsRun) y generar reportes consolidados de publicidad comercial con base de datos SQLite integrada y interfaz web Streamlit.

## 🎯 Funcionalidades Principales

### 📊 Procesamiento de Datos
- ✅ Procesa archivos de logs AsRun en formato .txt
- ✅ Filtra automáticamente emisiones comerciales (IDs que empiecen con "COM")
- ✅ Elimina automáticamente clientes que empiecen con "MC_"
- ✅ Normaliza nombres de marcas según patrones específicos
- ✅ Considera día de emisión de 6:00 AM a 5:59 AM del día siguiente
- ✅ **Análisis completo de STATUS** - Incluye "Completed", "Lost XPoint Path" y "Play Next"
- ✅ **Filtrado inteligente de Media Events** - Solo procesa emisiones comerciales con IDs "COM"
- ✅ **Sistema anti-duplicados automático** - Previene registros duplicados
- ✅ **Detección de duplicados en tiempo real** - Muestra estadísticas de procesamiento

### 📄 Generación de Reportes
- ✅ **Genera reportes en doble formato**: `.txt` y `.xlsx` simultáneamente
- ✅ **Archivos Excel con múltiples hojas**: Datos completos, resúmenes por cliente y por fecha
- ✅ **Hoja especializada "Lost XPoint Path"** - Análisis de problemas técnicos
- ✅ **Hoja especializada "Play Next"** - Análisis de emisiones programadas
- ✅ Versionado automático para ambos formatos
- ✅ Reportes personalizados con filtros avanzados

### 🌐 Interfaz Web AS RUN REPORTES
- ✅ **Aplicación web Streamlit** - Interfaz moderna y fácil de usar
- ✅ **Dashboard interactivo** - Visualizaciones con Plotly
- ✅ **Consultas en tiempo real** - Filtros por cliente, fecha y rango
- ✅ **Estadísticas visuales** - Gráficos de actividad diaria y top clientes
- ✅ **Exportación directa** - Descarga de reportes desde la web
- ✅ **Acceso multi-dispositivo** - Compatible con escritorio y móvil

### 🗄️ Base de Datos
- ✅ Almacena datos en base de datos SQLite para consultas
- ✅ **Filtrado automático por Media Events comerciales** - Solo registros con EVENT='Media Event' y MEDIA_ID que empiecen con 'COM'
- ✅ Sistema de consultas interactivo con filtros avanzados
- ✅ Gestión automática de backups
- ✅ Optimización de rendimiento para grandes volúmenes

## 📁 Formato de Archivos Compatibles

### Archivos .txt AsRun

El sistema procesa archivos de texto con el siguiente formato:

```
Log Output - Marina Text AsRun v1.0
Filename: 'Tx List-Marina Text 20250523_055959 Marina.txt'
Channel: 'A) Tx List'
From: 23/05/25 05:59:59 to 24/05/25 05:59:59
Created : 23/05/25 06:00:19

 TYPE START TIME             END TIME               MEDIA ID                         EVENT                TITLE                            SOM         SEGMENT                          DURATION    ...
 ---- ---------------------- ---------------------- -------------------------------- -------------------- -------------------------------- ----------- -------------------------------- ----------- ...
 P    23/05/2025 07:27:15;18 23/05/2025 07:27:40;18 COM09052025001                   Media Event          CANNON HOME ATELIER              00:00:00;00 Media                            00:00:25;00 ...
```

**Criterios de filtrado automático:**
- Solo registros con `EVENT = "Media Event"`
- Solo `MEDIA_ID` que empiecen con "COM"
- Procesa registros con `STATUS = "Completed"`, `"Lost XPoint Path"` y `"Play Next"`
- Excluye automáticamente títulos que empiecen con "MC_"

## 🗂️ Estructura del Proyecto

```
asrun-report/
├── data/                    # Archivos .txt de entrada
├── reportes/               # Reportes generados (.txt y .xlsx)
├── src/                    # Scripts Python principales
│   ├── procesar_asrun.py   # Procesamiento de logs AsRun
│   ├── consultar_bd.py     # Consultor interactivo de BD
│   └── database_manager.py # Gestor de base de datos SQLite
├── utils/                  # Utilidades y herramientas
│   ├── app_streamlit.py    # Aplicación web AS RUN REPORTES
│   ├── crear_backup_completo.py # Sistema de backups
│   └── limpiar_proyecto.py # Limpieza de datos
├── tests/                  # Pruebas y validaciones
├── docs/                   # Documentación técnica
├── backups/               # Backups automáticos de BD
├── asrun_database.db      # Base de datos SQLite principal
├── start_server.sh        # Script de inicio del servidor web
├── requirements.txt       # Dependencias básicas
├── requirements_executable.txt # Dependencias completas
└── README.md             # Esta documentación
```

## 🚀 Instalación y Uso

### 1. Instalar dependencias
```bash
# Dependencias básicas
pip install -r requirements.txt

# O dependencias completas (incluye Streamlit)
pip install -r requirements_executable.txt
```

### 2. Iniciar la aplicación web AS RUN REPORTES
```bash
# Opción 1: Script automático (recomendado)
./start_server.sh

# Opción 2: Manual
cd utils/
streamlit run app_streamlit.py --server.port 8501 --server.address 0.0.0.0
```

### 3. Acceder a la aplicación
- **Local**: http://localhost:8501
- **Red local**: http://[IP-LOCAL]:8501
- La aplicación detecta automáticamente la IP de red

### 4. Procesamiento por línea de comandos (opcional)

#### Colocar archivos de datos
```bash
cp /ruta/a/tus/archivos/*.txt data/
```

#### Procesar datos
```bash
python src/procesar_asrun.py
```

#### Consultar base de datos
```bash
python src/consultar_bd.py
```

## 📊 Marcas Normalizadas

El sistema normaliza automáticamente las siguientes marcas:

- **MARLEY** - contenga "marley"
- **SINGULARITY** - contenga "singularity" 
- **CANNON** - contenga "cannon"
- **BMW** - contenga "bmw"
- **TE PILLE** - contenga "pille"
- **MOVISTAR** - contenga "movistar"
- **CONSORCIO** - contenga "cons"
- **CLINICA MIRA** - contenga "clinica mira"
- **BHP** - contenga "bhp" o "bhpv2"
- **ATLAS CORPORATIVO** - contenga "atlas corporativo"
- **CAP 1 CLC ALEMANA** - contenga "cap 1 clc alemana"
- **GASCO MINERIA_INERSA** - contenga "gasco mineria" o "inersa"
- **SKECHERS FUTBOL** - contenga "skechers"
- **TI [NOMBRE]** - títulos que empiecen con "TI " (títulos institucionales)

## 🗄️ Base de Datos

### Tablas principales:

**emisiones**: Almacena cada emisión individual
- `id`, `fecha_procesamiento`, `dia_emision`, `hora_emision`
- `datetime_emision`, `cliente`, `media_id`, `titulo`
- `duracion`, `archivo_origen`, `status`, `event`, `created_at`

**reportes**: Almacena información de reportes generados
- `id`, `nombre_archivo`, `fecha_generacion`, `total_emisiones`
- `dias_incluidos`, `clientes_incluidos`, `ruta_archivo`

### Consultas disponibles:
- 📊 Estadísticas generales y métricas de rendimiento
- 👥 Resumen por cliente con totales de emisión
- 🎯 Consultas por cliente específico
- 📅 Consultas por día específico y rangos de fechas
- 📄 Lista de reportes generados históricamente
- 🧹 Limpieza de datos antiguos y mantenimiento
- 🚨 **Análisis Lost XPoint Path** - Problemas técnicos detectados
- 📈 **Dashboard web interactivo** - Visualizaciones en tiempo real

## 🛡️ Sistema Anti-Duplicados

El sistema implementa **prevención automática de duplicados** a nivel de base de datos:

### ⚡ Características:
- **Constraint único**: Combinación de `(dia_emision, hora_emision, media_id, cliente)` debe ser única
- **INSERT OR IGNORE**: Los duplicados se ignoran automáticamente sin errores
- **Detección en tiempo real**: Muestra estadísticas de registros nuevos vs duplicados omitidos
- **Procesamiento seguro**: Puedes procesar los mismos archivos múltiples veces sin crear duplicados

### 📊 Estadísticas de Procesamiento:
```
📁 Procesando: Tx List-Marina Text 20250503_055959 Marina.txt
   ✅ 85 emisiones comerciales encontradas
   💾 Guardados: 85 nuevos registros

📁 Procesando: Tx List-Marina Text 20250503_055959 Marina.txt (segunda vez)
   ✅ 85 emisiones comerciales encontradas
   💾 Guardados: 0 nuevos registros
   🔄 Omitidos: 85 duplicados detectados
```

### 🔧 Implementación Técnica:
- **Constraint de base de datos**: `UNIQUE(dia_emision, hora_emision, media_id, cliente)`
- **Lógica de inserción**: `INSERT OR IGNORE` previene errores por duplicados
- **Contador de duplicados**: Tracking automático de registros omitidos vs insertados

## 📝 Formato de Reportes

El sistema genera **automáticamente dos formatos de reporte**:

### 📄 Archivo de Texto (.txt)
Reporte tradicional con formato tabular organizado por cliente:

```
REPORTE CONSOLIDADO DE EMISIÓN PUBLICITARIA
==================================================

Fecha de generación: 2025-05-28 10:49:54
Total de emisiones: 1,243
Período del reporte: 2025-05-12 al 2025-05-27

Cliente: CANNON
============================================================
Fecha        Hora       Duración        ID                   Título
----------------------------------------------------------------------------------------------------
2025-05-22   07:27:15   00:00:25;00     COM09052025001       CANNON HOME ATELIER
2025-05-22   07:43:01   00:00:25;00     COM09052025001       CANNON HOME ATELIER
2025-05-23   14:32:18   00:00:25;00     COM09052025002       CANNON NUEVOS MODELOS
----------------------------------------------------------------------------------------------------
Total de emisiones de CANNON: 3
```

### 📊 Archivo Excel (.xlsx)
Archivo Excel con **múltiples hojas para análisis avanzado**:

#### 🗂️ **Hoja 1: "Todos los Datos"**
- **Columnas**: Fecha, Hora, Cliente, Título, ID Comercial, Duración
- **Contenido**: Todas las emisiones en formato tabular
- **Formato**: Fechas estandarizadas, horas HH:MM:SS (sin decimales), columnas con ancho ajustado

#### 📈 **Hoja 2: "Resumen por Cliente"**
- **Columnas**: Cliente, Total Emisiones, Duración Total
- **Contenido**: Estadísticas agregadas por cliente
- **Ordenado**: Por total de emisiones (descendente)

#### 📅 **Hoja 3: "Resumen por Fecha"**
- **Columnas**: Fecha, Total Emisiones, Clientes Únicos
- **Contenido**: Estadísticas agregadas por día
- **Ordenado**: Por fecha (cronológico)

#### 🚨 **Hoja 4: "Lost XPoint Path"**
- **Columnas**: Fecha, Cliente, Hora Inicio, Título/Programa, Media ID, Duración
- **Contenido**: Solo registros con problemas técnicos (status "Lost XPoint Path")
- **Funcionalidad**: Análisis especializado de fallos técnicos
- **Formato optimizado**: Datos limpios para troubleshooting (v2.3.1)

#### 🎯 **Hoja 5: "Play Next"**
- **Columnas**: Fecha, Cliente, Hora Inicio, Título/Programa, Media ID, Duración
- **Contenido**: Solo registros programados para emisión (status "Play Next")
- **Funcionalidad**: Análisis de emisiones en cola y programación
- **Filtrado comercial**: Solo muestra Play Next de emisiones comerciales (COM)

#### 📊 **Hoja 6: "STATUS Analysis"**
- **Columnas**: Status, Total Registros, Porcentaje
- **Contenido**: Estadísticas completas de todos los estados encontrados
- **Incluye**: Completed, Lost XPoint Path, Play Next, y otros estados técnicos
- **Utilidad**: Visión general del rendimiento del sistema de emisión

### 🌐 Funcionalidades de la Aplicación Web

#### 🖥️ **Dashboard Principal**
- **Estadísticas generales**: Total de emisiones, clientes únicos, período de datos
- **Gráfico de actividad diaria**: Visualización temporal de emisiones
- **Top 10 clientes**: Ranking de clientes por volumen de emisiones
- **Filtros interactivos**: Por cliente, fecha, y rango de fechas

#### 📊 **Consultas Avanzadas**
- **Filtro por cliente**: Búsqueda y selección de cliente específico
- **Filtro por fecha**: Selector de fecha individual
- **Filtro por rango**: Selección de período entre dos fechas
- **Exportación directa**: Descarga de reportes Excel desde la interfaz web

#### 🎨 **Características de UI/UX**
- **Diseño responsivo**: Compatible con desktop, tablet y móvil
- **Tema moderno**: Interfaz limpia y profesional
- **Navegación intuitiva**: Menú lateral con opciones organizadas
- **Feedback visual**: Indicadores de progreso y confirmaciones
- **Acceso multi-usuario**: Servidor accesible desde red local

### 🎯 Características del Sistema de Reportes:

- **🔄 Generación simultánea**: Ambos formatos se crean automáticamente
- **🔢 Versionado inteligente**: Verifica existencia de ambos archivos (.txt y .xlsx)
- **📊 Múltiples perspectivas**: Excel permite análisis desde diferentes ángulos
- **📋 Formato optimizado**: Columnas con ancho apropiado para cada tipo de dato
- **📅 Fechas normalizadas**: Formato consistente YYYY-MM-DD
- **⏰ Horas limpias**: Formato HH:MM:SS sin decimales (v2.3.1)
- **🚨 Análisis Lost XPoint Path**: Hoja dedicada para problemas técnicos (v2.3.1)

```
REPORTE CONSOLIDADO DE EMISIÓN PUBLICITARIA
==================================================

Fecha de generación: 2025-05-28 10:49:54
Total de emisiones: 1,243
Período del reporte: 2025-05-12 al 2025-05-27

Cliente: CANNON
============================================================
Fecha        Hora       Duración        ID                   Título
----------------------------------------------------------------------------------------------------
2025-05-22   07:27:15   00:00:25;00     COM09052025001       CANNON HOME ATELIER
2025-05-22   07:43:01   00:00:25;00     COM09052025001       CANNON HOME ATELIER
2025-05-23   14:32:18   00:00:25;00     COM09052025002       CANNON NUEVOS MODELOS
----------------------------------------------------------------------------------------------------
Total de emisiones de CANNON: 3

Cliente: CONSORCIO
============================================================
Fecha        Hora       Duración        ID                   Título
----------------------------------------------------------------------------------------------------
2025-05-15   00:15:28   00:00:15;01     COM12052025011       B_CONS_OUTDOORASISTENCIA_445909
2025-05-15   08:19:35   00:00:15;05     COM12052025016       G_CONS_URBANAREVTECNICA _445911
----------------------------------------------------------------------------------------------------
Total de emisiones de CONSORCIO: 2
```

### 🎯 Características del Nuevo Formato:

- **📊 Agrupación por cliente**: Los datos se organizan por cliente en lugar de por fecha
- **📅 Período del reporte**: Se muestra el rango completo de fechas al inicio
- **📋 Formato tabular**: Columnas alineadas para mejor legibilidad
- **📆 Columna de fecha**: Cada emisión muestra su fecha específica
- **🔢 Contadores por cliente**: Total de emisiones por cada cliente
- **✂️ Truncamiento de títulos**: Títulos largos se recortan para mantener el formato

## 🔧 Dependencias

### Dependencias Básicas (requirements.txt)
- `pandas` - Procesamiento de datos y exportación Excel
- `openpyxl` - Generación de archivos Excel (.xlsx)
- `sqlite3` - Base de datos (incluido en Python)
- `pathlib` - Manejo de rutas
- `datetime` - Manejo de fechas

### Dependencias Completas (requirements_executable.txt)
- `streamlit` - Framework para aplicación web
- `plotly` - Visualizaciones interactivas
- `pillow` - Procesamiento de imágenes
- Todas las dependencias básicas incluidas

## 🌐 Guía de Uso de AS RUN REPORTES (Web)

### 🚀 Inicio Rápido
1. **Ejecutar**: `./start_server.sh`
2. **Abrir navegador**: http://localhost:8501
3. **Subir archivos**: Usar la sección "Subir y Procesar Archivos AsRun"
4. **Ver resultados**: Dashboard se actualiza automáticamente

### 📊 Secciones Principales

#### 1. **Dashboard**
- Estadísticas generales en tiempo real
- Gráficos de actividad diaria y clientes top
- Métricas de rendimiento del sistema

#### 2. **Subir y Procesar Archivos**
- Drag & drop de archivos .txt
- Procesamiento en tiempo real
- Feedback inmediato de resultados

#### 3. **Consultas Avanzadas**
- Filtros por cliente, fecha, rango
- Exportación directa a Excel
- Vistas personalizadas de datos

#### 4. **Gestión de Base de Datos**
- Estadísticas detalladas
- Limpieza de datos antiguos
- Gestión de backups

### 📱 Acceso Remoto
El servidor Streamlit se configura automáticamente para acceso en red local:
- **Detección automática de IP**: El script detecta la IP de red
- **Acceso multi-dispositivo**: Compatible con móviles y tablets
- **Puerto estándar**: 8501 (configurable)
- **CORS habilitado**: Permite conexiones desde cualquier origen

## 📈 Ejemplo de Uso Completo

### 🌐 Uso Recomendado (Interfaz Web)
```bash
# 1. Iniciar AS RUN REPORTES
./start_server.sh

# 2. Abrir navegador
# Local: http://localhost:8501
# Red: http://[IP-DETECTADA]:8501

# 3. Usar la interfaz web para:
# - Subir y procesar archivos .txt
# - Ver dashboard en tiempo real
# - Generar reportes personalizados
# - Exportar datos a Excel
```

### 💻 Uso por Línea de Comandos (Alternativo)
```bash
# 1. Procesar archivos .txt (genera automáticamente .txt y .xlsx)
python src/procesar_asrun.py

# 2. Consultar estadísticas y generar reportes personalizados
python src/consultar_bd.py
# Seleccionar opción 1 para ver estadísticas generales
# Seleccionar opción 3 para generar reporte con filtros

# 3. Ver reportes generados (ambos formatos)
ls reportes/
# reporte_asrun_20250721_v1.txt
# reporte_asrun_20250721_v1.xlsx
# reporte_personalizado_20250721_v1.xlsx
```

### 📊 Ejemplos de Reportes Generados:

#### Desde Interfaz Web:
- **Reporte completo**: `reporte_personalizado_20250721_134007_v1.xlsx`
- **Reporte filtrado**: Generación directa desde filtros web
- **Exportación inmediata**: Descarga automática al navegador

#### Desde Línea de Comandos:
- **Reporte completo**: `reporte_asrun_20250721_v1.xlsx` (todas las emisiones)
- **Reporte filtrado por fechas**: `reporte_asrun_20250721_desde_2025-07-15_hasta_2025-07-20_v1.xlsx`
- **Reporte desde consultor**: `reporte_asrun_20250721_consulta_v1.xlsx`

### 🔄 Flujo de Trabajo Típico:
1. **Recibir archivos AsRun** (.txt) del sistema de emisión
2. **Subir a AS RUN REPORTES** mediante la interfaz web
3. **Verificar procesamiento** en el dashboard
4. **Generar reportes personalizados** con filtros específicos
5. **Exportar a Excel** para análisis detallado
6. **Compartir reportes** con stakeholders

Los reportes se generan automáticamente con:
- ✅ **Versionado incremental** para ambos formatos
- ✅ **Almacenamiento en carpeta reportes/**
- ✅ **Registro en base de datos** para consultas posteriores
- ✅ **Análisis Lost XPoint Path** incluido
- ✅ **Análisis Play Next** para emisiones programadas
- ✅ **Múltiples hojas Excel** para diferentes perspectivas

## 📋 Formato Detallado de Archivos .txt

### Estructura requerida:

1. **Encabezado del archivo** (líneas 1-6):
   - Información del log
   - Nombre del archivo
   - Canal y fechas
   
2. **Línea de columnas** (línea 7):
   ```
   TYPE START TIME             END TIME               MEDIA ID                         EVENT                TITLE                            ...
   ```

3. **Línea de separadores** (línea 8):
   ```
   ---- ---------------------- ---------------------- -------------------------------- -------------------- -------------------------------- ...
   ```

4. **Datos** (líneas 9 en adelante):
   - Cada línea representa un evento
   - Posiciones fijas para cada campo
   - Los campos relevantes son: TYPE, START TIME, MEDIA ID, EVENT, TITLE, DURATION, STATUS

### Ejemplo de línea de datos válida:
```
P    23/05/2025 07:27:15;18 23/05/2025 07:27:40;18 COM09052025001                   Media Event          CANNON HOME ATELIER              00:00:00;00 Media                            00:00:25;00 ... Completed
P    23/05/2025 08:15:30;12 23/05/2025 08:15:55;12 COM09052025002                   Media Event          CANNON NUEVOS MODELOS            00:00:00;00 Media                            00:00:25;00 ... Play Next
P    23/05/2025 09:22:45;06 23/05/2025 09:23:10;06 COM09052025003                   Media Event          CANNON PROMOCION                 00:00:00;00 Media                            00:00:25;00 ... Lost XPoint Path
```

Este formato es el estándar para los archivos generados por sistemas AsRun y es completamente compatible con el procesador.

## 🎯 Características Avanzadas

### 🚨 Análisis Lost XPoint Path
El sistema detecta y analiza automáticamente problemas técnicos:
- **Detección automática**: Identifica registros con status "Lost XPoint Path"
- **Hoja especializada**: Genera análisis separado en Excel
- **Estadísticas detalladas**: Muestra impacto y frecuencia de problemas
- **Troubleshooting**: Facilita identificación de patrones de fallas

### 📺 Análisis Play Next
El sistema procesa y analiza emisiones programadas:
- **Estado Play Next**: Identifica registros con status "Play Next" 
- **Emisiones comerciales programadas**: Solo incluye comerciales con Media ID "COM"
- **Hoja especializada en Excel**: Análisis separado de emisiones en cola
- **Filtrado inteligente**: Excluye automáticamente Switch Events y contenido no comercial
- **Análisis de programación**: Seguimiento de emisiones en espera
- **Estadísticas incluidas**: Contabiliza en reportes y análisis STATUS

### 🔄 Sistema de Versionado Inteligente
- **Detección automática**: Verifica archivos existentes antes de generar
- **Incremento automático**: v1, v2, v3... según disponibilidad
- **Sincronización**: Mantiene misma versión para .txt y .xlsx
- **Historial completo**: Preserva todas las versiones generadas

### 🛡️ Seguridad y Rendimiento
- **Validación de datos**: Verificación de integridad antes del procesamiento
- **Filtrado automático de Media Events**: Solo procesa eventos comerciales válidos
- **Manejo de errores**: Recuperación graceful ante archivos corruptos
- **Optimización de memoria**: Procesamiento eficiente de archivos grandes
- **Backups automáticos**: Protección de datos críticos
- **Exclusión de Switch Events**: Filtra automáticamente eventos no comerciales

### 📊 Métricas y Monitoreo
- **Dashboard en tiempo real**: Métricas actualizadas automáticamente
- **Estadísticas de procesamiento**: Tracking de duplicados y nuevos registros
- **Análisis de tendencias**: Gráficos de actividad temporal
- **Alertas de calidad**: Detección de anomalías en los datos

---

## 📞 Soporte y Documentación

- **Documentación técnica**: Carpeta `docs/` con detalles de implementación
- **Archivos de configuración**: `requirements.txt` y `requirements_executable.txt`
- **Scripts de utilidad**: Carpeta `utils/` con herramientas adicionales
- **Tests incluidos**: Carpeta `tests/` para validación del sistema

**AS RUN REPORTES** v2.3.1 - Sistema integral de análisis de emisión publicitaria con interfaz web moderna, análisis avanzado de Lost XPoint Path y soporte completo para Play Next comercial.
