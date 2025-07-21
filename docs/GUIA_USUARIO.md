# 📖 Guía de Usuario - Procesador de Logs AsRun

## 🚀 Introducción

Bienvenido al **Procesador de Logs AsRun**, un sistema completo para analizar logs de emisión de televisión y generar reportes de publicidad comercial. Esta guía te llevará paso a paso desde la instalación hasta el uso avanzado del sistema.

---

## 📋 Tabla de Contenidos

1. [Instalación Inicial](#instalación-inicial)
2. [Primer Uso](#primer-uso)
3. [Procesamiento de Archivos](#procesamiento-de-archivos)
4. [Consultas en Base de Datos](#consultas-en-base-de-datos)
5. [Interpretación de Reportes](#interpretación-de-reportes)
6. [Casos de Uso Comunes](#casos-de-uso-comunes)
7. [Resolución de Problemas](#resolución-de-problemas)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 📦 Instalación Inicial

### 1. Verificar Python
Asegúrate de tener Python 3.8 o superior instalado:
```bash
python --version
```

### 2. Navegar al directorio del proyecto
```bash
cd /Users/alecarrasco/Documents/06_DESARROLLOS/pago_publicidad/asrun-report
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar instalación
```bash
python src/procesar_asrun.py --help
```

---

## 🎯 Primer Uso

### Paso 1: Preparar archivos de datos

1. **Ubicación de archivos fuente**: Los archivos AsRun están en:
   ```
   /Users/alecarrasco/Documents/06_DESARROLLOS/pago_publicidad/ASRUN/
   ```

2. **Copiar archivos a procesar**: 
   ```bash
   # Copiar un archivo específico
   cp ../ASRUN/"Tx List-Marina Text 20250527_055959 Marina.txt" data/
   
   # O copiar múltiples archivos
   cp ../ASRUN/"Tx List-Marina Text 202505"* data/
   ```

### Paso 2: Ejecutar primer procesamiento

```bash
python src/procesar_asrun.py
```

**¿Qué verás?**
```
🚀 PROCESADOR DE LOGS ASRUN
========================================
📂 Datos: /Users/.../asrun-report/data
📂 Reportes: /Users/.../asrun-report/reportes
🗄️  Base de datos inicializada: .../asrun_database.db

📋 Archivos encontrados: 1
   • Tx List-Marina Text 20250527_055959 Marina.txt

🔄 Procesando archivos...
📁 Procesando: Tx List-Marina Text 20250527_055959 Marina.txt
   ✓ Líneas leídas: 773
   ✓ Encabezados encontrados en línea 6
   ✓ Datos empiezan en línea 8
   ✓ Registros extraídos: 765
   ✓ Media Events con COM y Completed: 100
   ✓ Después de filtrar MC_: 96 registros
   ✅ Procesado: 96 registros comerciales
   💾 Guardando en BD: 96 registros

📝 Generando reporte consolidado...
📄 Reporte generado: reporte_asrun_20250527_v1.txt

✅ ¡Proceso completado exitosamente!
```

---

## 📁 Procesamiento de Archivos

### Formato de archivos compatible

Los archivos deben ser archivos .txt con esta estructura:

```
Log Output - Marina Text AsRun v1.0
Filename: 'Tx List-Marina Text 20250527_055959 Marina.txt'
...

 TYPE START TIME             END TIME               MEDIA ID                         EVENT                TITLE                            ...
 ---- ---------------------- ---------------------- -------------------------------- -------------------- -------------------------------- ...
 P    27/05/2025 07:27:15;18 27/05/2025 07:27:40;18 COM09052025001                   Media Event          CANNON HOME ATELIER              ...
```

### Criterios de filtrado automático

El sistema **SOLO** procesa registros que cumplan **TODOS** estos criterios:

✅ **EVENT** = "Media Event"  
✅ **MEDIA_ID** empiece con "COM"  
✅ **STATUS** = "Completed"  
❌ **TITLE** NO empiece con "MC_" (se excluyen automáticamente)

### Procesamiento por lotes

```bash
# Procesar todos los archivos de mayo 2025
cp ../ASRUN/"Tx List-Marina Text 202505"* data/
python src/procesar_asrun.py

# Procesar archivos específicos
cp ../ASRUN/"Tx List-Marina Text 20250527_055959 Marina.txt" data/
cp ../ASRUN/"Tx List-Marina Text 20250528_055959 Marina.txt" data/
python src/procesar_asrun.py
```

---

## 🗄️ Consultas en Base de Datos

### Iniciar el consultor interactivo

```bash
python src/consultar_bd.py
```

### Menú principal

```
============================================================
🗄️  CONSULTOR DE BASE DE DATOS ASRUN
============================================================
1. 📊 Estadísticas generales
2. 👥 Resumen por cliente
3. 🎯 Consultar cliente específico
4. 📅 Consultar día específico
5. 📄 Ver reportes generados
6. 📝 Generar reporte personalizado
7. 🧹 Limpiar datos antiguos
0. 🚪 Salir
```

### 1. Estadísticas Generales

**¿Qué obtienes?**
- Total de emisiones registradas
- Número de clientes únicos
- Rango de fechas procesadas
- Total de reportes generados

**Ejemplo de salida:**
```
📊 ESTADÍSTICAS GENERALES
==================================================
📺 Total de emisiones registradas: 1,245
👥 Total de clientes únicos: 18
📄 Total de reportes generados: 5
📅 Rango de fechas: 2025-05-03 → 2025-05-27
📆 Total de días cubiertos: 25
```

### 2. Resumen por Cliente

**Funciones:**
- Ver todos los clientes o top N
- Filtrar por rango de fechas
- Estadísticas por cliente

**Ejemplo de uso:**
```
Filtros opcionales (presiona Enter para omitir):
Fecha inicio (YYYY-MM-DD): 2025-05-20
Fecha fin (YYYY-MM-DD): 2025-05-27
Mostrar solo top N clientes (número): 5
```

**Ejemplo de salida:**
```
🎯 CANNON
   • Emisiones: 125
   • Días activos: 7
   • Primera emisión: 2025-05-20
   • Última emisión: 2025-05-27

🎯 BMW
   • Emisiones: 89
   • Días activos: 6
   • Primera emisión: 2025-05-21
   • Última emisión: 2025-05-27
```

### 3. Consulta por Cliente Específico

**Ejemplo:**
```
Nombre del cliente: CANNON
Fecha inicio (YYYY-MM-DD): [Enter para omitir]
Fecha fin (YYYY-MM-DD): [Enter para omitir]
¿Mostrar detalle completo? (s/N): s
```

**Salida detallada:**
```
🎯 CONSULTA CLIENTE: CANNON
==================================================
📺 Total de emisiones encontradas: 125
📅 Días con emisiones: 7
📊 Promedio de emisiones por día: 17.9
📊 Máximo emisiones en un día: 25
📊 Mínimo emisiones en un día: 12

📋 DETALLE DE EMISIONES:
------------------------------
📺 2025-05-27 07:27:15
   • ID: COM09052025001
   • Duración: 00:00:25;00
   • Título: CANNON HOME ATELIER
```

### 4. Consulta por Día Específico

**Ejemplo:**
```
Día de emisión (YYYY-MM-DD): 2025-05-27
```

**Salida:**
```
📅 EMISIONES DEL DÍA: 2025-05-27
==================================================
📺 Total de emisiones: 96
👥 Clientes únicos: 16

📊 Resumen por cliente:
   • CANNON: 25 emisiones
   • BMW: 18 emisiones
   • MOVISTAR: 15 emisiones
   ...

📋 CRONOLOGÍA DEL DÍA:
------------------------------
🕐 07:27:15 - CANNON
   ID: COM09052025001 | Duración: 00:00:25;00
   Título: CANNON HOME ATELIER
```

### 5. Ver Reportes Generados

**Funcionalidad:**
- Listar todos los reportes generados previamente
- Ver detalles de cada reporte (fecha, filtros aplicados, número de emisiones)
- Navegar por los reportes existentes

**Ejemplo de salida:**
```
📄 REPORTES GENERADOS
==================================================
📊 Total de reportes encontrados: 3

📝 Reporte 1:
   📄 Archivo: reporte_asrun_20250528_cliente_cannon_desde_2025-05-20_hasta_2025-05-27_v1.txt
   📅 Generado: 28/05/2025 - 10:49:54
   🎯 Cliente: CANNON
   📆 Período: 2025-05-20 a 2025-05-27
   📺 Emisiones: 125

📝 Reporte 2:
   📄 Archivo: reporte_asrun_20250528_desde_2025-05-23_hasta_2025-05-27_v1.txt
   📅 Generado: 28/05/2025 - 11:15:32
   🎯 Cliente: Todos
   📆 Período: 2025-05-23 a 2025-05-27
   📺 Emisiones: 287
```

### 6. Generar Reporte Personalizado

**Nueva funcionalidad** que permite crear reportes con filtros específicos:

**Opciones de filtrado:**
- Por rango de fechas (fecha inicio y fin)
- Por cliente específico
- Combinación de ambos filtros

**Ejemplo de uso:**
```
🎯 GENERACIÓN DE REPORTE PERSONALIZADO
==================================================

Filtros opcionales (presiona Enter para omitir):
📅 Fecha inicio (YYYY-MM-DD): 2025-05-20
📅 Fecha fin (YYYY-MM-DD): 2025-05-27
👤 Cliente específico: CANNON

🔍 Aplicando filtros...
   📅 Período: 2025-05-20 a 2025-05-27
   👤 Cliente: CANNON
   📺 Emisiones encontradas: 125

💾 Generando reporte...
📝 Reporte generado exitosamente:
   📄 Archivo: reporte_asrun_20250528_cliente_cannon_desde_2025-05-20_hasta_2025-05-27_v1.txt
   📁 Ubicación: reportes/
   📊 Total de emisiones incluidas: 125
```

### ✨ Generación Automática de Reportes

**Nueva característica**: Después de realizar cualquier consulta (opciones 1-4), el sistema te preguntará automáticamente si deseas generar un reporte basado en los datos consultados.

**Flujo automático:**
```
# Después de consultar estadísticas, clientes o días específicos:

🤔 ¿Te gustaría generar un reporte basado en esta consulta? (s/N): s

🎯 GENERACIÓN DE REPORTE DESDE CONSULTA
==================================================
📊 Basado en tu consulta anterior
🔍 Aplicando filtros automáticamente...

💾 Generando reporte...
📝 Reporte generado exitosamente:
   📄 Archivo: reporte_asrun_20250528_automatico_v1.txt
   📊 Total de emisiones incluidas: 96
```

**Ventajas de la generación automática:**
- **Flujo integrado**: No necesitas cambiar de opción para generar reportes
- **Filtros inteligentes**: Aplica automáticamente los filtros de tu consulta
- **Ahorro de tiempo**: Genera reportes instantáneamente después de analizar datos
- **Consistencia**: Los reportes reflejan exactamente lo que consultaste

---

## 📄 Interpretación de Reportes

### 🔄 Generación Automática de Doble Formato

**Desde la versión 2.3.0**, el sistema genera **automáticamente dos tipos de archivo** para cada reporte:

- **📄 Archivo de texto (.txt)**: Formato tradicional para lectura y archivo
- **📊 Archivo Excel (.xlsx)**: Formato avanzado con múltiples hojas para análisis

### 📁 Ubicación de reportes
```
reportes/reporte_asrun_YYYYMMDD_vX.txt
reportes/reporte_asrun_YYYYMMDD_vX.xlsx
reportes/reporte_asrun_YYYYMMDD_cliente_NOMBRE_desde_YYYY-MM-DD_hasta_YYYY-MM-DD_vX.txt
reportes/reporte_asrun_YYYYMMDD_cliente_NOMBRE_desde_YYYY-MM-DD_hasta_YYYY-MM-DD_vX.xlsx
```

### 📊 **Estructura de Archivos Excel**

Cada archivo Excel contiene **3-4 hojas especializadas**:

#### 🗂️ **Hoja 1: "Todos los Datos"**
- **Propósito**: Vista completa de todas las emisiones
- **Columnas**: Fecha | Hora | Cliente | Título | ID Comercial | Duración
- **Formato**: Datos tabulares optimizados para análisis, horas HH:MM:SS (sin decimales)
- **Uso**: Filtros, ordenamiento, búsquedas específicas

#### 📈 **Hoja 2: "Resumen por Cliente"**
- **Propósito**: Estadísticas agregadas por cliente
- **Columnas**: Cliente | Total Emisiones | Duración Total
- **Ordenado**: Por total de emisiones (mayor a menor)
- **Uso**: Análisis de volumen por cliente, facturación

#### 📅 **Hoja 3: "Resumen por Fecha"**
- **Propósito**: Estadísticas agregadas por día
- **Columnas**: Fecha | Total Emisiones | Clientes Únicos
- **Ordenado**: Cronológicamente
- **Uso**: Análisis de tendencias diarias, actividad por fecha

#### 🚨 **Hoja 4: "Lost XPoint Path" (cuando aplique)**
- **Propósito**: Análisis de problemas técnicos o interrupciones
- **Columnas**: Fecha | Cliente | Hora Inicio | Título/Programa | Media ID | Duración
- **Contenido**: Solo registros con status "Lost XPoint Path"
- **Optimizado**: Análisis limpio sin columnas innecesarias (v2.3.1)
- **Uso**: Identificar patrones de problemas técnicos, reportes de incidencias

### 📄 **Estructura del Reporte de Texto**

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

### Interpretación de campos

**🎯 Nuevo Formato Tabular:**
- **Fecha**: Fecha específica de emisión (YYYY-MM-DD)
- **Hora**: Hora exacta de emisión (HH:MM:SS)
- **Duración**: Duración del spot (formato HH:MM:SS;FF)
- **ID**: Identificador único del material (COMDDMMAAAANN)
- **Título**: Nombre descriptivo del spot publicitario (truncado a 32 caracteres)

**📊 Información del Encabezado:**
- **Fecha de generación**: Cuándo se creó el reporte
- **Total de emisiones**: Cantidad total de spots en el reporte
- **Período del reporte**: Rango de fechas incluidas (fecha mínima al fecha máxima)

**👥 Agrupación por Cliente:**
- Los datos se organizan por cliente (no por fecha)
- Cada cliente tiene su propia sección con tabla de emisiones
- Al final de cada sección se muestra el total de emisiones del cliente

---

## 🔧 Casos de Uso Comunes

### Caso 1: Reporte semanal de un cliente (NUEVO - Flujo integrado)

```bash
# 1. Procesar archivos de la semana
cp ../ASRUN/"Tx List-Marina Text 2025052"[0-7]* data/
python src/procesar_asrun.py

# 2. Consultar y generar reporte automáticamente
python src/consultar_bd.py
# Seleccionar opción 3 (Consultar cliente específico)
# Nombre del cliente: CANNON
# Fecha inicio: 2025-05-20
# Fecha fin: 2025-05-27
# ¿Te gustaría generar un reporte basado en esta consulta? (s/N): s
```

**Resultado**: Obtienes tanto la consulta interactiva como un reporte personalizado automáticamente.

### Caso 2: Reporte personalizado avanzado

```bash
python src/consultar_bd.py
# Seleccionar opción 6 (Generar reporte personalizado)
# Fecha inicio: 2025-05-01
# Fecha fin: 2025-05-31
# Cliente específico: BMW
```

**Resultado**: Reporte completo de BMW para todo mayo 2025.

### Caso 3: Análisis de día específico con reporte

```bash
# 1. Asegurar que el día está procesado
cp ../ASRUN/"Tx List-Marina Text 20250527_055959 Marina.txt" data/
python src/procesar_asrun.py

# 2. Consultar el día y generar reporte
python src/consultar_bd.py
# Seleccionar opción 4 (Consultar día específico)
# Día: 2025-05-27
# ¿Te gustaría generar un reporte basado en esta consulta? (s/N): s
```

**Resultado**: Análisis interactivo + reporte detallado del día específico.

### Caso 4: Reporte mensual consolidado

```bash
# 1. Procesar todo el mes
cp ../ASRUN/"Tx List-Marina Text 202505"* data/
python src/procesar_asrun.py

# 2. Generar reporte completo del mes
python src/consultar_bd.py
# Seleccionar opción 6 (Generar reporte personalizado)
# Fecha inicio: 2025-05-01
# Fecha fin: 2025-05-31
# Cliente específico: [Enter para incluir todos]
```

### Caso 5: Revisión de reportes históricos

```bash
python src/consultar_bd.py
# Seleccionar opción 5 (Ver reportes generados)
```

**Resultado**: Lista completa de todos los reportes generados con sus detalles.

### Caso 6: Comparación entre períodos

```bash
# Generar reporte semana 1
python src/consultar_bd.py
# Opción 6: Fecha inicio: 2025-05-01, Fecha fin: 2025-05-07

# Generar reporte semana 2
python src/consultar_bd.py
# Opción 6: Fecha inicio: 2025-05-08, Fecha fin: 2025-05-14

# Ver ambos reportes
# Opción 5: Ver reportes generados
```

### Caso 7: Limpieza de datos antiguos

```bash
python src/consultar_bd.py
# Seleccionar opción 7
# Días de antigüedad: 90
# ¿Continuar? s
```

---

## ⚠️ Resolución de Problemas

### Error: "No se encontraron archivos .txt"

**Causa**: No hay archivos en la carpeta `data/`

**Solución**:
```bash
# Verificar contenido de data/
ls data/

# Copiar archivos
cp ../ASRUN/"Tx List-Marina Text"* data/
```

### Error: "No se encontraron registros que cumplan todos los filtros"

**Causa**: El archivo no contiene comerciales válidos

**Verificación**:
```bash
# Buscar comerciales en el archivo
grep "COM" data/"nombre_archivo.txt" | grep "Media Event" | head -5
```

**Posibles causas**:
- Archivo no contiene IDs que empiecen con "COM"
- Todos los registros son "MC_" (se filtran automáticamente)
- No hay registros con STATUS "Completed"

### Error: "No se encontraron emisiones para los filtros especificados"

**Causa**: Los filtros de fecha/cliente no coinciden con datos en la base de datos

**Solución**:
```bash
# Verificar qué datos están disponibles
python src/consultar_bd.py
# Opción 1: Ver estadísticas generales para conocer el rango de fechas
# Opción 2: Ver clientes disponibles
```

### Error: "No se pudo registrar el reporte en la base de datos"

**Causa**: Problema con la tabla de reportes en la base de datos

**Solución**:
```bash
# El reporte se genera correctamente, solo falla el registro
# Verificar que el archivo del reporte existe en reportes/
ls reportes/
# El sistema continuará funcionando normalmente
```

### Error de parseo de fechas

**Causa**: Formato de fecha inesperado

**Verificación**:
```bash
# Ver formato de fechas en el archivo
head -20 data/"nombre_archivo.txt"
```

### Base de datos bloqueada

**Solución**:
```bash
# Cerrar todos los scripts que usen la BD
# Reiniciar el proceso
python src/procesar_asrun.py
```

### Error: "Archivo de reporte no encontrado"

**Causa**: El archivo de reporte fue movido o eliminado después de registrarse en la BD

**Solución**:
```bash
# Verificar ubicación de reportes
ls reportes/
# Regenerar el reporte usando la opción 6 del consultor
```

### Warning: "DtypeWarning" o advertencias de pandas

**Causa**: Advertencias sobre inferencia de tipos de datos (no afecta funcionamiento)

**Acción**: Estas advertencias son informativas y no requieren acción. El sistema funciona correctamente.

---

## ❓ Preguntas Frecuentes

### ¿Puedo procesar el mismo archivo múltiples veces?

**Sí**, el sistema agregará los datos sin duplicar. La base de datos mantiene un registro de origen por cada emisión.

### ¿Cómo agregar una nueva marca para normalizar?

Editar `src/procesar_asrun.py`, función `normalizar_marca()`:

```python
def normalizar_marca(titulo):
    # ...existing code...
    elif 'nueva_marca' in titulo:
        return 'NUEVA_MARCA'
    # ...existing code...
```

### ¿Qué significa "día de emisión 6:00 AM a 5:59 AM"?

Las emisiones entre 00:00:00 y 05:59:59 se consideran del día anterior. Por ejemplo:
- Emisión a las 02:30:00 del 28/05/2025 → Día de emisión: 27/05/2025
- Emisión a las 08:30:00 del 28/05/2025 → Día de emisión: 28/05/2025

### ¿Cuál es la diferencia entre los tipos de reportes?

**Reporte consolidado** (procesamiento): Incluye todos los datos procesados en una sesión
**Reporte personalizado** (consultor opción 6): Permite filtros específicos de fecha/cliente
**Reporte automático** (después de consultas): Refleja exactamente los datos de tu consulta anterior

### ¿Puedo generar múltiples reportes del mismo período?

**Sí**, el sistema maneja versiones automáticamente (v1, v2, v3...) para evitar sobrescribir reportes existentes.

### ¿Cómo puedo encontrar un reporte específico?

Usa la opción 5 del consultor para ver todos los reportes generados con sus detalles y filtros aplicados.

### ¿Los reportes automáticos son diferentes a los manuales?

**No**, la diferencia está solo en cómo se generan. El contenido y formato son idénticos. Los automáticos usan los filtros de tu consulta previa.

### ¿Puedo generar un reporte de todos los clientes en un período?

**Sí**, en la opción 6 (Generar reporte personalizado), simplemente presiona Enter cuando te pida el cliente específico.

### ¿Cómo hacer backup de la base de datos?

```bash
cp asrun_database.db asrun_database_backup_$(date +%Y%m%d).db
```

### ¿Los reportes se guardan en la base de datos?

**Sí**, cada reporte generado se registra en la base de datos con sus metadatos (fecha, filtros, ubicación del archivo) para poder listarlos posteriormente.

---

## 🛠️ Mantenimiento

### Limpieza periódica

**Mensual**:
```bash
python src/consultar_bd.py
# Opción 7: Limpiar datos antiguos (90 días)
```

### Backup de reportes y base de datos

```bash
# Crear backup de reportes
tar -czf reportes_backup_$(date +%Y%m%d).tar.gz reportes/

# Backup de base de datos
cp asrun_database.db asrun_database_backup_$(date +%Y%m%d).db

# Backup completo del proyecto
tar -czf asrun_backup_completo_$(date +%Y%m%d).tar.gz \
  asrun_database.db reportes/ data/ src/
```

### Monitoreo de espacio

```bash
# Ver tamaño de la base de datos
ls -lh asrun_database.db

# Ver cantidad de archivos procesados
ls data/ | wc -l

# Ver cantidad de reportes generados
ls reportes/ | wc -l

# Estadísticas rápidas
python src/consultar_bd.py
# Opción 1: Estadísticas generales
```

### Optimización de rendimiento

**Recomendaciones**:
- Limpia datos antiguos mensualmente (opción 7)
- Haz backup de reportes y elimina archivos antiguos si es necesario
- La base de datos SQLite es eficiente hasta varios millones de registros

---

## 📞 Soporte

Para problemas técnicos o dudas sobre el uso del sistema:

1. **Verificar esta guía** - La mayoría de problemas están documentados
2. **Revisar logs de error** - Los scripts muestran mensajes detallados
3. **Verificar archivos de entrada** - Asegurar formato correcto
4. **Usar opción 1 del consultor** - Ver estadísticas para diagnóstico rápido

### ✨ Novedades de la versión actual

- **🔄 Generación automática de reportes**: Después de cada consulta, el sistema pregunta si deseas generar un reporte
- **🎯 Reportes personalizados**: Nueva opción para crear reportes con filtros específicos
- **📋 Gestión de reportes**: Lista y gestiona todos los reportes generados
- **🔍 Consultas mejoradas**: Mayor detalle en las consultas por cliente y fecha
- **💾 Base de datos integrada**: Todos los reportes se registran para fácil acceso

---

*Guía actualizada: Mayo 2025*  
*Versión del sistema: 2.1 con generación automática de reportes*  
*Nuevas funcionalidades: Reportes personalizados, generación automática, gestión de reportes*
