#!/usr/bin/env python3
"""
Procesador de logs AsRun - Versión simplificada desde cero
Genera reportes consolidados de emisión publicitaria
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the current directory to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import AsRunDatabase, ClienteNormalizer


def _formatear_hora_sin_decimales(hora_str):
    """Formatear hora eliminando decimales y manteniendo solo HH:MM:SS"""
    try:
        if pd.isna(hora_str):
            return "N/A"
        
        hora_str = str(hora_str)
        
        # Si la hora tiene decimales, eliminarlos
        if '.' in hora_str:
            hora_str = hora_str.split('.')[0]
        
        # Verificar si ya está en formato HH:MM:SS
        if len(hora_str.split(':')) == 3:
            try:
                # Validar que sea un tiempo válido
                datetime.strptime(hora_str, '%H:%M:%S')
                return hora_str
            except ValueError:
                pass
        
        # Si es un objeto datetime, convertir a string sin decimales
        try:
            if isinstance(hora_str, str) and 'T' in hora_str:
                # Formato datetime ISO
                dt = datetime.fromisoformat(hora_str.replace('T', ' '))
                return dt.strftime('%H:%M:%S')
            else:
                # Intentar parsear como datetime
                dt = pd.to_datetime(hora_str)
                return dt.strftime('%H:%M:%S')
        except:
            return str(hora_str)[:8] if len(str(hora_str)) >= 8 else str(hora_str)
            
    except Exception as e:
        return str(hora_str)


def _obtener_nombre_con_version(directorio, nombre_base, extension=""):
    """
    Obtener nombre de archivo con versionado automático
    
    Args:
        directorio: Path del directorio donde se guardará el archivo
        nombre_base: Nombre base del archivo (sin extensión)
        extension: Extensión del archivo (ej: '.txt', '.xlsx')
        
    Returns:
        tuple: (nombre_con_version, ruta_completa)
    """
    version = 1
    
    while True:
        nombre_versionado = f"{nombre_base}_v{version}{extension}"
        ruta_archivo = directorio / nombre_versionado
        
        # Para reportes Excel/TXT, verificar que no existan ambos formatos
        if extension in ['.txt', '.xlsx']:
            nombre_base_v = f"{nombre_base}_v{version}"
            ruta_txt = directorio / f"{nombre_base_v}.txt"
            ruta_xlsx = directorio / f"{nombre_base_v}.xlsx"
            
            if not ruta_txt.exists() and not ruta_xlsx.exists():
                break
        else:
            # Para otros tipos de archivo, verificar solo la extensión específica
            if not ruta_archivo.exists():
                break
        
        version += 1
    
    return nombre_versionado, ruta_archivo


class AsRunProcessor:
    """Clase wrapper para el procesamiento de archivos AsRun - Compatible con Streamlit"""
    
    def __init__(self, db_path=None):
        """Inicializar el procesador"""
        if db_path is None:
            # Usar SIEMPRE la base de datos principal en el directorio raíz del proyecto
            current_dir = Path(__file__).parent
            # Prioridad única: BD principal en directorio padre (raíz del proyecto)
            db_path = str(current_dir.parent / "asrun_database.db")
        
        self.db = AsRunDatabase(db_path)
        self.directorio_proyecto = Path(db_path).parent
    
    def procesar_archivo_asrun(self, ruta_archivo):
        """Procesar un archivo AsRun individual - Interfaz para Streamlit"""
        try:
            # Procesar el archivo usando la función existente
            df = procesar_archivo_txt(Path(ruta_archivo))
            
            if df.empty:
                return {
                    'exitoso': False,
                    'error': 'No se pudieron extraer datos válidos del archivo',
                    'total_procesados': 0,
                    'nuevos_registros': 0,
                    'duplicados': 0
                }
            
            # Insertar emisiones en la base de datos
            insertados, duplicados = self.db.insertar_emisiones(df, Path(ruta_archivo).name)
            
            return {
                'exitoso': True,
                'total_procesados': len(df),
                'nuevos_registros': insertados,
                'duplicados': duplicados,
                'datos_procesados': df
            }
            
        except Exception as e:
            return {
                'exitoso': False,
                'error': str(e),
                'total_procesados': 0,
                'nuevos_registros': 0,
                'duplicados': 0
            }
    
    def procesar_multiples_archivos(self, rutas_archivos):
        """Procesar múltiples archivos AsRun"""
        resultados = []
        total_insertados = 0
        total_duplicados = 0
        dataframes = []
        
        for ruta in rutas_archivos:
            resultado = self.procesar_archivo_asrun(ruta)
            resultados.append({
                'archivo': Path(ruta).name,
                'resultado': resultado
            })
            
            if resultado['exitoso']:
                total_insertados += resultado['nuevos_registros']
                total_duplicados += resultado['duplicados']
                dataframes.append(resultado['datos_procesados'])
        
        return {
            'exitoso': len(dataframes) > 0,
            'archivos_procesados': len(resultados),
            'total_insertados': total_insertados,
            'total_duplicados': total_duplicados,
            'resultados_detalle': resultados,
            'dataframes': dataframes
        }


def normalizar_marca(titulo):
    """Normaliza el nombre de la marca usando el sistema de normalización"""
    if not isinstance(titulo, str):
        return "DESCONOCIDO"
    
    # Filtrar clientes que empiecen con "MC_"
    if titulo.upper().startswith('MC_'):
        return None  # Marcador para filtrar después
    
    # Usar el normalizador de clientes
    normalizer = ClienteNormalizer()
    return normalizer.normalizar_cliente(titulo)


def procesar_archivo_txt(ruta_archivo):
    """Procesa un archivo .txt AsRun y devuelve los datos filtrados"""
    print(f"📁 Procesando: {ruta_archivo.name}")
    
    try:
        # Leer archivo de texto
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        print(f"   ✓ Líneas leídas: {len(lineas)}")
        
        # Encontrar línea de encabezados (contiene TYPE START TIME...)
        linea_encabezado = None
        inicio_datos = None
        
        for i, linea in enumerate(lineas):
            if 'TYPE START TIME' in linea and 'MEDIA ID' in linea:
                linea_encabezado = i
                # Los datos empiezan después de la línea de separadores (----)
                for j in range(i + 1, len(lineas)):
                    if '----' in lineas[j]:
                        inicio_datos = j + 1
                        break
                break
        
        if linea_encabezado is None or inicio_datos is None:
            print("   ❌ No se encontró el formato esperado de encabezados")
            return pd.DataFrame()
        
        print(f"   ✓ Encabezados encontrados en línea {linea_encabezado}")
        print(f"   ✓ Datos empiezan en línea {inicio_datos}")
        
        # Procesar líneas de datos
        datos = []
        for i in range(inicio_datos, len(lineas)):
            linea = lineas[i].strip()
            if not linea or len(linea) < 100:  # Saltar líneas vacías o muy cortas
                continue
            
            # Parsear línea usando posiciones fijas (basado en el formato observado)
            try:
                # Usando las posiciones correctas basadas en el header
                tipo = linea[1:5].strip()
                fecha_inicio = linea[5:28].strip()  # START TIME
                fecha_fin = linea[28:51].strip()    # END TIME  
                media_id = linea[51:84].strip()     # MEDIA ID
                evento = linea[84:105].strip()      # EVENT
                titulo = linea[105:138].strip()     # TITLE
                som = linea[138:150].strip()        # SOM
                segmento = linea[150:183].strip()   # SEGMENT
                duracion = linea[183:195].strip()   # DURATION
                
                # Buscar status al final de la línea (más preciso)
                if 'Lost XPoint Path' in linea:
                    status = 'Lost XPoint Path'
                elif 'Play Next' in linea:
                    status = 'Play Next'
                elif 'Completed' in linea:
                    status = 'Completed'
                else:
                    status = 'Other'
                
                datos.append({
                    'TYPE': tipo,
                    'START_TIME': fecha_inicio,
                    'END_TIME': fecha_fin,
                    'MEDIA_ID': media_id,
                    'EVENT': evento,
                    'TITLE': titulo,
                    'SOM': som,
                    'SEGMENT': segmento,
                    'DURATION': duracion,
                    'STATUS': status
                })
            except Exception as e_linea:
                # Saltar líneas que no se puedan parsear
                continue
        
        if not datos:
            print("   ⚠️  No se pudieron extraer datos válidos")
            return pd.DataFrame()
        
        # Crear DataFrame
        df = pd.DataFrame(datos)
        print(f"   ✓ Registros extraídos: {len(df)}")
        
        # Filtrar solo Media Events con COM IDs y diferentes STATUS
        # Para todos los STATUS: requiere Media Event + MEDIA_ID que empiece con COM
        df_filtrado = df[
            (df['EVENT'] == 'Media Event') & 
            (df['MEDIA_ID'].str.startswith('COM', na=False)) &
            (df['STATUS'].isin(['Completed', 'Lost XPoint Path', 'Play Next']))
        ].copy()
        
        print(f"   ✓ Media Events con COM y STATUS válido: {len(df_filtrado)}")
        
        # Mostrar estadísticas de STATUS
        status_counts = df_filtrado['STATUS'].value_counts()
        for status, count in status_counts.items():
            print(f"     • {status}: {count} registros")
        
        if len(df_filtrado) == 0:
            print("   ⚠️  No se encontraron registros que cumplan todos los filtros")
            return pd.DataFrame()
         # Procesar fechas y horas
        # Convertir START_TIME al formato datetime, eliminando frames (;FF)
        def parse_time_without_frames(time_str):
            """Parsear tiempo eliminando los frames al final y asegurando formato limpio"""
            try:
                time_str = str(time_str).strip()
                # Si tiene frames (;XX), eliminarlos
                if ';' in time_str:
                    time_str = time_str.split(';')[0]
                    
                # Verificar que el formato sea correcto y solo contenga HH:MM:SS
                parts = time_str.split(' ')
                if len(parts) >= 2:
                    # Formato: "DD/MM/YYYY HH:MM:SS"
                    date_part = parts[0]
                    time_part = parts[1]
                    
                    # Asegurar que time_part solo tenga HH:MM:SS
                    time_components = time_part.split(':')
                    if len(time_components) >= 3:
                        # Tomar solo horas, minutos y segundos (sin microsegundos ni frames)
                        clean_time = f"{time_components[0]}:{time_components[1]}:{time_components[2]}"
                        return f"{date_part} {clean_time}"
                
                return time_str
            except Exception as e:
                print(f"   ⚠️  Error procesando tiempo '{time_str}': {e}")
                return time_str

        df_filtrado['START_TIME_CLEAN'] = df_filtrado['START_TIME'].apply(parse_time_without_frames)
        
        df_filtrado['DATETIME'] = pd.to_datetime(
            df_filtrado['START_TIME_CLEAN'], 
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce'
        )
        
        # Filtrar filas donde no se pudo parsear la fecha
        df_filtrado = df_filtrado.dropna(subset=['DATETIME'])
        
        if len(df_filtrado) == 0:
            print("   ⚠️  No se pudieron procesar las fechas correctamente")
            return pd.DataFrame()
        
        # Calcular día de emisión (6am-5:59am)
        df_filtrado['DIA_EMISION'] = df_filtrado['DATETIME'].apply(
            lambda x: (x - timedelta(days=1)).date() if x.hour < 6 else x.date()
        )
        
        # Normalizar marcas
        df_filtrado['MARCA'] = df_filtrado['TITLE'].apply(normalizar_marca)
        
        # Filtrar registros con marcas válidas (eliminar MC_)
        df_filtrado = df_filtrado[df_filtrado['MARCA'].notna()].copy()
        
        print(f"   ✓ Después de filtrar MC_: {len(df_filtrado)} registros")
        
        # Seleccionar columnas necesarias (incluyendo STATUS y EVENT para filtros posteriores)
        resultado = df_filtrado[['DATETIME', 'DIA_EMISION', 'MEDIA_ID', 'TITLE', 'MARCA', 'DURATION', 'STATUS', 'EVENT']].copy()
        
        print(f"   ✅ Procesado: {len(resultado)} registros comerciales")
        
        # Mostrar resumen final de STATUS
        if 'STATUS' in resultado.columns:
            status_counts = resultado['STATUS'].value_counts()
            print(f"   📊 STATUS final:")
            for status, count in status_counts.items():
                print(f"     • {status}: {count}")
        
        return resultado
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def generar_reporte(lista_dataframes, directorio_salida):
    """Genera el reporte consolidado en formato .txt y .xlsx"""
    if not lista_dataframes:
        print("❌ No hay datos para procesar")
        return None
    
    # Unir todos los datos
    df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
    total_registros = len(df_consolidado)
    
    print(f"\n📊 Total de registros consolidados: {total_registros}")
    
    # Crear directorio de salida
    directorio_salida.mkdir(exist_ok=True)
    
    # Determinar nombre del archivo con versionado
    fecha_mas_reciente = df_consolidado['DIA_EMISION'].max().strftime('%Y%m%d')
    nombre_base = f"reporte_asrun_{fecha_mas_reciente}"
    
    # Obtener nombres de archivos con versionado automático
    nombre_archivo_txt, ruta_archivo_txt = _obtener_nombre_con_version(
        directorio_salida, nombre_base, ".txt"
    )
    nombre_archivo_xlsx, ruta_archivo_xlsx = _obtener_nombre_con_version(
        directorio_salida, nombre_base, ".xlsx"
    )
    
    # Ordenar datos por marca, fecha y hora
    df_consolidado = df_consolidado.sort_values(['MARCA', 'DIA_EMISION', 'DATETIME'])
    
    # GENERAR ARCHIVO .TXT (formato original)
    contenido = []
    contenido.append("REPORTE CONSOLIDADO DE EMISIÓN PUBLICITARIA")
    contenido.append("=" * 50)
    contenido.append("")
    contenido.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    contenido.append(f"Total de emisiones: {total_registros:,}")
    
    # Determinar y mostrar rango de fechas del reporte
    fecha_min = df_consolidado['DIA_EMISION'].min()
    fecha_max = df_consolidado['DIA_EMISION'].max()
    contenido.append(f"Período del reporte: {fecha_min} al {fecha_max}")
    contenido.append("")
    
    # Agrupar por cliente (para el reporte .txt)
    grupos = df_consolidado.groupby('MARCA')
    
    for cliente_nombre, grupo in grupos:
        contenido.append(f"Cliente: {cliente_nombre}")
        contenido.append("=" * 60)
        
        # Encabezado de tabla
        contenido.append(f"{'Fecha':<12} {'Hora':<10} {'Duración':<15} {'ID':<20} {'Título'}")
        contenido.append("-" * 100)
        
        for _, fila in grupo.iterrows():
            fecha = fila['DIA_EMISION'].strftime('%Y-%m-%d')
            hora = fila['DATETIME'].strftime('%H:%M:%S')
            duracion = str(fila['DURATION']).strip()
            media_id = str(fila['MEDIA_ID']).strip()
            titulo = str(fila['TITLE']).strip()
            
            # Truncar título si es muy largo
            if len(titulo) > 35:
                titulo = titulo[:32] + "..."
            
            contenido.append(f"{fecha:<12} {hora:<10} {duracion:<15} {media_id:<20} {titulo}")
        
        contenido.append("")
        contenido.append(f"Total de emisiones de {cliente_nombre}: {len(grupo)}")
        contenido.append("")
    
    # AGREGAR ANÁLISIS DE STATUS AL FINAL DEL REPORTE
    if 'STATUS' in df_consolidado.columns:
        contenido.append("\nANÁLISIS DE STATUS")
        contenido.append("-" * 30)
        
        status_counts = df_consolidado['STATUS'].value_counts()
        for status, count in status_counts.items():
            porcentaje = (count / len(df_consolidado)) * 100
            contenido.append(f"{status}: {count} emisiones ({porcentaje:.1f}%)")
        
        # Detalles de Lost XPoint Path si existe - Solo Media Events con COM
        lost_xpoint_df = df_consolidado[
            (df_consolidado['STATUS'].str.contains('Lost XPoint Path', case=False, na=False)) &
            (df_consolidado['EVENT'] == 'Media Event') &
            (df_consolidado['MEDIA_ID'].str.startswith('COM', na=False))
        ]
        if not lost_xpoint_df.empty:
            contenido.append(f"\nDETALLE DE LOST XPOINT PATH ({len(lost_xpoint_df)} registros)")
            contenido.append("-" * 50)
            
            for _, row in lost_xpoint_df.iterrows():
                # Formatear hora sin decimales
                hora_limpia = _formatear_hora_sin_decimales(row['DATETIME'].strftime('%H:%M:%S'))
                contenido.append(f"Fecha: {row['DIA_EMISION']} | Hora: {hora_limpia} | Cliente: {row['MARCA']}")
                contenido.append(f"Título: {row['TITLE']}")
                if pd.notna(row['MEDIA_ID']):
                    contenido.append(f"Media ID: {row['MEDIA_ID']}")
                contenido.append("")
        
        # Detalles de Play Next si existe - Solo Media Events con COM
        play_next_df = df_consolidado[
            (df_consolidado['STATUS'].str.contains('Play Next', case=False, na=False)) &
            (df_consolidado['EVENT'] == 'Media Event') &
            (df_consolidado['MEDIA_ID'].str.startswith('COM', na=False))
        ]
        if not play_next_df.empty:
            contenido.append(f"\nDETALLE DE PLAY NEXT ({len(play_next_df)} registros)")
            contenido.append("-" * 50)
            
            for _, row in play_next_df.iterrows():
                # Formatear hora sin decimales
                hora_limpia = _formatear_hora_sin_decimales(row['DATETIME'].strftime('%H:%M:%S'))
                contenido.append(f"Fecha: {row['DIA_EMISION']} | Hora: {hora_limpia} | Cliente: {row['MARCA']}")
                contenido.append(f"Título: {row['TITLE']}")
                if pd.notna(row['MEDIA_ID']):
                    contenido.append(f"Media ID: {row['MEDIA_ID']}")
                contenido.append("")
    
    contenido.append("\n" + "=" * 80)
    contenido.append("FIN DEL REPORTE")
    contenido.append("=" * 80)
    
    # Guardar archivo .TXT
    with open(ruta_archivo_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(contenido))
    
    # GENERAR ARCHIVO .XLSX
    print("📊 Generando archivo Excel...")
    
    # Preparar datos para Excel
    df_excel = df_consolidado.copy()
    df_excel['FECHA'] = df_excel['DIA_EMISION'].astype(str)
    # Aplicar formateo de hora sin decimales
    df_excel['HORA'] = df_excel['DATETIME'].dt.strftime('%H:%M:%S').apply(_formatear_hora_sin_decimales)
    
    # Reordenar y renombrar columnas para Excel
    df_excel = df_excel[['FECHA', 'HORA', 'MARCA', 'TITLE', 'MEDIA_ID', 'DURATION']].copy()
    df_excel.columns = ['Fecha', 'Hora', 'Cliente', 'Título', 'ID Comercial', 'Duración']
    
    # Crear el archivo Excel con múltiples hojas
    with pd.ExcelWriter(ruta_archivo_xlsx, engine='openpyxl') as writer:
        # Hoja 1: Todos los datos
        df_excel.to_excel(writer, sheet_name='Todos los Datos', index=False)
        
        # Hoja 2: Resumen por cliente
        resumen_cliente = df_excel.groupby('Cliente').agg({
            'Título': 'count',
            'Duración': 'sum'
        }).rename(columns={'Título': 'Total Emisiones', 'Duración': 'Duración Total'})
        resumen_cliente.to_excel(writer, sheet_name='Resumen por Cliente')
        
        # Hoja 3: Resumen por fecha
        resumen_fecha = df_excel.groupby('Fecha').agg({
            'Título': 'count',
            'Cliente': 'nunique'
        }).rename(columns={'Título': 'Total Emisiones', 'Cliente': 'Clientes Únicos'})
        resumen_fecha.to_excel(writer, sheet_name='Resumen por Fecha')
        
        # Hoja 4: Lost XPoint Path (si hay registros) - Solo Media Events con COM
        lost_xpoint_df = df_consolidado[
            (df_consolidado['STATUS'].str.contains('Lost XPoint Path', case=False, na=False)) &
            (df_consolidado['EVENT'] == 'Media Event') &
            (df_consolidado['MEDIA_ID'].str.startswith('COM', na=False))
        ]
        if not lost_xpoint_df.empty:
            df_lost_xpoint = lost_xpoint_df.copy()
            df_lost_xpoint['FECHA'] = df_lost_xpoint['DIA_EMISION'].astype(str)
            df_lost_xpoint['HORA'] = df_lost_xpoint['DATETIME'].dt.strftime('%H:%M:%S').apply(_formatear_hora_sin_decimales)
            df_lost_xpoint_excel = df_lost_xpoint[['FECHA', 'MARCA', 'HORA', 'TITLE', 'MEDIA_ID', 'DURATION']].copy()
            df_lost_xpoint_excel.columns = ['Fecha', 'Cliente', 'Hora Inicio', 'Título/Programa', 'Media ID', 'Duración']
            df_lost_xpoint_excel.to_excel(writer, sheet_name='Lost XPoint Path', index=False)
        
        # Hoja 5: Play Next (si hay registros) - Solo Media Events con COM
        play_next_df = df_consolidado[
            (df_consolidado['STATUS'].str.contains('Play Next', case=False, na=False)) &
            (df_consolidado['EVENT'] == 'Media Event') &
            (df_consolidado['MEDIA_ID'].str.startswith('COM', na=False))
        ]
        if not play_next_df.empty:
            df_play_next = play_next_df.copy()
            df_play_next['FECHA'] = df_play_next['DIA_EMISION'].astype(str)
            df_play_next['HORA'] = df_play_next['DATETIME'].dt.strftime('%H:%M:%S').apply(_formatear_hora_sin_decimales)
            df_play_next_excel = df_play_next[['FECHA', 'MARCA', 'HORA', 'TITLE', 'MEDIA_ID', 'DURATION']].copy()
            df_play_next_excel.columns = ['Fecha', 'Cliente', 'Hora Programada', 'Título/Programa', 'Media ID', 'Duración']
            df_play_next_excel.to_excel(writer, sheet_name='Play Next', index=False)
        
        # Hoja 6: STATUS Analysis
        if 'STATUS' in df_consolidado.columns:
            status_analysis = df_consolidado['STATUS'].value_counts().reset_index()
            status_analysis.columns = ['Status', 'Total Registros']
            status_analysis['Porcentaje'] = (status_analysis['Total Registros'] / len(df_consolidado) * 100).round(1)
            status_analysis.to_excel(writer, sheet_name='STATUS Analysis', index=False)
        
        # Ajustar ancho de columnas en la hoja principal
        worksheet = writer.sheets['Todos los Datos']
        worksheet.column_dimensions['A'].width = 12  # Fecha
        worksheet.column_dimensions['B'].width = 10  # Hora
        worksheet.column_dimensions['C'].width = 20  # Cliente
        worksheet.column_dimensions['D'].width = 40  # Título
        worksheet.column_dimensions['E'].width = 20  # ID Comercial
        worksheet.column_dimensions['F'].width = 12  # Duración
    
    print(f"📄 Reporte TXT generado: {nombre_archivo_txt}")
    print(f"📊 Reporte Excel generado: {nombre_archivo_xlsx}")
    
    return ruta_archivo_txt


def main():
    """Función principal"""
    print("🚀 PROCESADOR DE LOGS ASRUN")
    print("=" * 40)
    
    # Definir rutas
    directorio_script = Path(__file__).parent
    directorio_proyecto = directorio_script.parent
    directorio_datos = directorio_proyecto / 'data'
    directorio_reportes = directorio_proyecto / 'reportes'
    
    print(f"📂 Datos: {directorio_datos}")
    print(f"📂 Reportes: {directorio_reportes}")
    
    # Verificar directorio de datos
    if not directorio_datos.exists():
        print(f"❌ No existe el directorio de datos: {directorio_datos}")
        return
    
    # Inicializar base de datos
    db_path = directorio_proyecto / 'asrun_database.db'
    db = AsRunDatabase(str(db_path))
    print(f"🗄️  Base de datos inicializada: {db_path}")
    
    # Buscar archivos .txt
    archivos = list(directorio_datos.glob('*.txt'))
    
    if not archivos:
        print("❌ No se encontraron archivos .txt")
        return
    
    print(f"\n📋 Archivos encontrados: {len(archivos)}")
    for archivo in archivos:
        print(f"   • {archivo.name}")
    
    print("\n🔄 Procesando archivos...")
    
    # Procesar cada archivo
    dataframes = []
    total_insertados = 0
    total_duplicados = 0
    
    for archivo in archivos:
        df = procesar_archivo_txt(archivo)
        if not df.empty:
            dataframes.append(df)
            # Guardar emisiones en la base de datos
            print(f"   💾 Procesando BD: {len(df)} registros de {archivo.name}")
            insertados, duplicados = db.insertar_emisiones(df, archivo.name)
            total_insertados += insertados
            total_duplicados += duplicados
    
    # Generar reporte final
    if dataframes:
        print("\n📝 Generando reporte consolidado...")
        ruta_reporte = generar_reporte(dataframes, directorio_reportes)
        
        if ruta_reporte:
            # Guardar información del reporte en BD
            df_consolidado = pd.concat(dataframes, ignore_index=True)
            db.insertar_reporte(
                ruta_reporte.name, 
                len(df_consolidado), 
                ruta_reporte, 
                df_consolidado
            )
            
            print(f"\n✅ ¡Proceso completado exitosamente!")
            print(f"📄 Reporte guardado en: {ruta_reporte}")
            print(f"🗄️  Base de datos actualizada:")
            print(f"   • Nuevos registros insertados: {total_insertados}")
            if total_duplicados > 0:
                print(f"   • Duplicados omitidos: {total_duplicados}")
            
            # Mostrar estadísticas de la BD
            stats = db.obtener_estadisticas_generales()
            print(f"\n📊 Estadísticas de la base de datos:")
            print(f"   • Total emisiones: {stats['total_emisiones']}")
            print(f"   • Total clientes: {stats['total_clientes']}")
            print(f"   • Total reportes: {stats['total_reportes']}")
        else:
            print("\n❌ Error al generar el reporte")
    else:
        print("\n❌ No se pudieron procesar los archivos")


if __name__ == "__main__":
    main()
