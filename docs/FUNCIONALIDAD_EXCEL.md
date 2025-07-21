# 📊 FUNCIONALIDAD EXCEL - DOCUMENTACIÓN TÉCNICA

## 🎯 Descripción General

**Versión implementada**: v2.3.1  
**Fecha**: 10 de junio de 2025  
**Objetivo**: Proporcionar análisis avanzado de datos AsRun mediante archivos Excel con múltiples hojas especializadas.

## 🔧 Implementación Técnica

### **Dependencias Requeridas**
```bash
pandas>=2.0.0
openpyxl>=3.0.0
```

### **Módulos Modificados**

#### 1. **procesar_asrun.py**
- **Función añadida**: `_generar_archivo_excel()`
- **Cambio principal**: Generación simultánea de .txt y .xlsx
- **Bug corregido**: Formateo de fechas (`DIA_EMISION.astype(str)`)
- **Mejora v2.3.1**: Función `_formatear_hora_sin_decimales()` para formato HH:MM:SS limpio

#### 2. **consultar_bd.py** 
- **Función añadida**: `_generar_archivo_excel()`
- **Cambio principal**: Capacidad Excel en consultas de BD
- **Mejora**: Configuración automática de base de datos
- **Mejora v2.3.1**: Aplicación de formato de hora sin decimales y optimización Lost XPoint Path

---

## 📋 Estructura de Archivos Excel

### **Hoja 1: "Todos los Datos"**
```python
Columnas: ['Fecha', 'Hora', 'Cliente', 'Título', 'ID Comercial', 'Duración']
Formato: 
- Fecha: YYYY-MM-DD (string)
- Hora: HH:MM:SS (string, sin decimales)
- Texto: Sin truncamiento
```

**Ancho de columnas optimizado:**
- Fecha: 12 caracteres
- Hora: 10 caracteres  
- Cliente: 20 caracteres
- Título: 40 caracteres
- ID Comercial: 20 caracteres
- Duración: 12 caracteres

### **Hoja 2: "Resumen por Cliente"**
```python
Columnas: ['Cliente', 'Total Emisiones', 'Duración Total']
Ordenado: Por total de emisiones (descendente)
Agregación: groupby('Cliente').agg({
    'Título': 'count',
    'Duración': 'count'  # Total de emisiones
})
```

### **Hoja 3: "Resumen por Fecha"**
```python
Columnas: ['Fecha', 'Total Emisiones', 'Clientes Únicos']
Ordenado: Cronológicamente
Agregación: groupby('Fecha').agg({
    'Título': 'count',
    'Cliente': 'nunique'
})
```

### **Hoja 4: "Lost XPoint Path" (cuando aplique)**
```python
Columnas: ['Fecha', 'Cliente', 'Hora Inicio', 'Título/Programa', 'Media ID', 'Duración']
Contenido: Solo registros con status "Lost XPoint Path"
Formato: 
- Fecha: YYYY-MM-DD
- Hora Inicio: HH:MM:SS (sin decimales)
- Optimizado: Eliminadas columnas "Hora Fin" y "Duración Calculada" (v2.3.1)
```

**Ancho de columnas Lost XPoint Path:**
- Fecha: 12 caracteres
- Cliente: 20 caracteres
- Hora Inicio: 12 caracteres
- Título/Programa: 30 caracteres
- Media ID: 25 caracteres
- Duración: 15 caracteres

---

## 🔄 Proceso de Generación

### **Flujo Principal**

1. **Preparación de datos**:
   ```python
   df_excel = emisiones.copy()
   df_excel['FECHA'] = df_excel['DIA_EMISION'].astype(str)
   # Aplicar formateo de hora sin decimales (v2.3.1)
   df_excel['HORA'] = df_excel['hora_emision'].apply(self._formatear_hora_sin_decimales)
   ```

2. **Creación del archivo**:
   ```python
   with pd.ExcelWriter(ruta_excel, engine='openpyxl') as writer:
       # Hoja 1: Datos completos
       df_export.to_excel(writer, sheet_name='Todos los Datos', index=False)
       
       # Hoja 2: Resumen por cliente
       resumen_cliente.to_excel(writer, sheet_name='Resumen por Cliente')
       
       # Hoja 3: Resumen por fecha
       resumen_fecha.to_excel(writer, sheet_name='Resumen por Fecha')
       
       # Hoja 4: Lost XPoint Path (si aplica)
       if lost_xpoint_df:
           lost_xpoint_df.to_excel(writer, sheet_name='Lost XPoint Path', index=False)
   ```

3. **Ajuste de formato**:
   ```python
   worksheet = writer.sheets['Todos los Datos']
   worksheet.column_dimensions['A'].width = 12  # Fecha
   worksheet.column_dimensions['B'].width = 10  # Hora (formato HH:MM:SS)
   # ... más ajustes
   ```

### **Versionado de Archivos**

El sistema verifica la existencia de **ambos formatos** antes de versionar:

```python
def obtener_siguiente_version(directorio_base, patron_base):
    version = 1
    while True:
        archivo_txt = directorio_base / f"{patron_base}_v{version}.txt"
        archivo_xlsx = directorio_base / f"{patron_base}_v{version}.xlsx"
        
        if not archivo_txt.exists() and not archivo_xlsx.exists():
            break
        version += 1
    
    return version
```

---

## 📊 Casos de Uso

### **1. Análisis de Volumen por Cliente**
**Hoja recomendada**: "Resumen por Cliente"
**Utilidad**: Identificar clientes con mayor actividad publicitaria
**Datos**: Total de emisiones y duración por cliente

### **2. Análisis de Tendencias Temporales**
**Hoja recomendada**: "Resumen por Fecha"
**Utilidad**: Identificar patrones de emisión por día
**Datos**: Actividad diaria y diversidad de clientes

### **3. Búsqueda y Filtrado Detallado**
**Hoja recomendada**: "Todos los Datos"
**Utilidad**: Análisis granular con filtros de Excel
**Datos**: Registro completo de todas las emisiones

### **4. Análisis de Horarios**
**Hoja recomendada**: "Todos los Datos"
**Utilidad**: Identificar patrones de horarios de emisión
**Datos**: Hora exacta de cada emisión (formato HH:MM:SS limpio)

### **5. Análisis de Problemas Técnicos**
**Hoja recomendada**: "Lost XPoint Path"
**Utilidad**: Identificar y analizar interrupciones o problemas técnicos
**Datos**: Registros específicos con status "Lost XPoint Path"
**Beneficio**: Análisis optimizado sin columnas innecesarias (v2.3.1)

---

## 🚨 Consideraciones Técnicas

### **Limitaciones**
- **Tamaño máximo**: Excel soporta hasta 1,048,576 filas
- **Memoria**: Archivos grandes requieren más RAM
- **Rendimiento**: Generación Excel es más lenta que .txt

### **Optimizaciones Implementadas**
- **Motor openpyxl**: Eficiente para archivos .xlsx
- **Streaming**: No carga todo en memoria simultáneamente
- **Índices eliminados**: `index=False` para hojas limpias

### **Manejo de Errores**
```python
try:
    with pd.ExcelWriter(ruta_excel, engine='openpyxl') as writer:
        # Generación del archivo
        pass
    print(f"✅ Archivo Excel generado: {nombre_xlsx}")
except Exception as e:
    print(f"❌ Error generando Excel: {e}")
    # Continúa con generación .txt
```

---

## 🧪 Testing y Validación

### **Pruebas Realizadas**

1. **✅ Generación exitosa**: Ambos formatos creados simultáneamente
2. **✅ Integridad de datos**: Misma información en .txt y .xlsx
3. **✅ Múltiples hojas**: 3-4 hojas generadas correctamente
4. **✅ Formato Excel**: Columnas con ancho apropiado
5. **✅ Versionado**: Funciona con ambos formatos
6. **✅ Filtros**: Respeta filtros por fecha y cliente
7. **✅ Formato de horas**: Sin decimales (HH:MM:SS limpio) - v2.3.1
8. **✅ Lost XPoint Path**: Análisis optimizado con 6 columnas - v2.3.1

### **Archivos de Prueba Generados**
```
✅ reporte_asrun_20250528_v1.xlsx (1,820 emisiones)
✅ reporte_asrun_20250528_consulta_v1.xlsx (1,820 emisiones) 
✅ reporte_asrun_20250528_desde_2025-05-20_hasta_2025-05-22_v1.xlsx (242 emisiones)
```

### **Validación de Estructura**
```python
# Verificación automática realizada:
xl = pd.ExcelFile('reporte.xlsx')
assert 'Todos los Datos' in xl.sheet_names
assert 'Resumen por Cliente' in xl.sheet_names  
assert 'Resumen por Fecha' in xl.sheet_names

df_main = pd.read_excel('reporte.xlsx', sheet_name='Todos los Datos')
assert len(df_main.columns) == 6
assert 'Fecha' in df_main.columns
assert 'Cliente' in df_main.columns
```

---

## 🔮 Posibles Mejoras Futuras

### **Funcionalidades Avanzadas**
- 📊 **Gráficos automáticos**: Integrar charts en Excel
- 🎨 **Formato condicional**: Destacar datos importantes
- 📈 **Tablas dinámicas**: Análisis interactivo pre-configurado
- 🔍 **Filtros automáticos**: Habilitar filtros en todas las hojas

### **Optimizaciones**
- ⚡ **Generación asíncrona**: Excel en background
- 💾 **Compresión**: Reducir tamaño de archivos
- 🔄 **Templates**: Plantillas Excel predefinidas
- 📱 **Formato móvil**: Optimización para visualización móvil

---

## 📖 Referencias

- **pandas.ExcelWriter**: [Documentación oficial](https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html)
- **openpyxl**: [Documentación oficial](https://openpyxl.readthedocs.io/)
- **Formato Excel**: [Microsoft Excel specifications](https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3)
