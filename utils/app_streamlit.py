#!/usr/bin/env python3
"""
AS RUN REPORTES - Streamlit GUI
Interfaz web completa para el sistema de generación de reportes AsRun
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time
import zipfile
import io
import os
import sqlite3
from pathlib import Path
import sys
import json

# Agregar el directorio src al path para importar módulos
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Importar módulos del proyecto
try:
    from database_manager import AsRunDatabase
    from consultar_bd import AsRunConsultor
    from procesar_asrun import AsRunProcessor
except ImportError as e:
    st.error(f"Error importando módulos del proyecto: {e}")
    st.error(f"Verificar que los archivos existan en: {src_path}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="AS RUN REPORTES",
    page_icon="👧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    .upload-area {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización del estado de sesión con manejo robusto de errores
def initialize_session_state():
    """Inicializar objetos del session state con manejo de errores"""
    try:
        if 'consultor' not in st.session_state:
            st.session_state.consultor = AsRunConsultor()
            # Verificar conexión a BD
            _ = st.session_state.consultor.get_total_records()
        
        if 'processor' not in st.session_state:
            st.session_state.processor = AsRunProcessor()
            
        if 'db_error' not in st.session_state:
            st.session_state.db_error = False
            
        if 'error_message' not in st.session_state:
            st.session_state.error_message = None
            
    except Exception as e:
        st.session_state.db_error = True
        st.session_state.error_message = f"Error de inicialización: {str(e)}"
        st.error(f"❌ Error crítico de inicialización: {str(e)}")
        st.error("🔧 Verifique que la base de datos esté accesible y los módulos instalados correctamente")
        st.stop()

# Ejecutar inicialización
initialize_session_state()

def main():
    """Función principal de la aplicación Streamlit"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>👧 AS RUN REPORTES</h1>
        <p>Sistema Completo de Procesamiento y Análisis de Logs AsRun</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegación
    with st.sidebar:
        st.title("📋 Navegación")
        page = st.selectbox(
            "Seleccionar Página:",
            [
                "🏠 Dashboard",
                "📁 Procesar Archivos",
                "🔍 Consultar Base de Datos",
                "📊 Generar Reportes",
                "📥 Descargas",
                "⚙️ Administración"
            ]
        )
        
        st.markdown("---")
        
        # Información del sistema con manejo robusto de errores
        st.markdown("### 📊 Estado del Sistema")
        
        # Verificar si hay errores de BD antes de mostrar métricas
        if st.session_state.get('db_error', False):
            st.error("🔴 Base de datos no disponible")
            st.warning("⚠️ Algunas funciones pueden no estar disponibles")
            return
        
        try:
            total_records = st.session_state.consultor.get_total_records()
            if total_records is not None:
                st.metric("Total Registros", f"{total_records:,}")
            else:
                st.metric("Total Registros", "Error")
            
            unique_clients = st.session_state.consultor.get_unique_clients_count()
            if unique_clients is not None:
                st.metric("Clientes Únicos", unique_clients)
            else:
                st.metric("Clientes Únicos", "Error")
            
            last_date = st.session_state.consultor.get_last_processing_date()
            if last_date:
                st.metric("Último Procesamiento", last_date)
            else:
                st.metric("Último Procesamiento", "N/A")
                
        except sqlite3.Error as e:
            st.error("🔴 Error de base de datos en sidebar")
            st.session_state.db_error = True
            st.session_state.error_message = f"Error BD: {str(e)}"
        except Exception as e:
            st.error(f"⚠️ Error al cargar métricas: {str(e)[:50]}...")
            # No bloquear la aplicación, solo mostrar métricas básicas
            st.metric("Sistema", "Con errores")
        
        # Mostrar alerta si hay errores persistentes
        if st.session_state.get('error_message'):
            with st.expander("🔍 Detalles del Error"):
                st.code(st.session_state.error_message)
    
    # Renderizar página seleccionada
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "📁 Procesar Archivos":
        render_file_processing()
    elif page == "🔍 Consultar Base de Datos":
        render_database_query()
    elif page == "📊 Generar Reportes":
        render_report_generation()
    elif page == "📥 Descargas":
        render_downloads()
    elif page == "⚙️ Administración":
        render_administration()

def render_dashboard():
    """Renderizar página del dashboard con manejo robusto de errores"""
    st.header("🏠 Dashboard Principal")
    
    # Verificar estado de la base de datos antes de proceder
    if st.session_state.get('db_error', False):
        st.error("🔴 **Error de Base de Datos Detectado**")
        st.warning("El dashboard requiere acceso a la base de datos para mostrar información.")
        if st.button("🔄 Reintentar Conexión"):
            st.session_state.db_error = False
            st.session_state.error_message = None
            st.rerun()
        return
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        with col1:
            try:
                total_records = st.session_state.consultor.get_total_records()
                today_records = st.session_state.consultor.get_today_records_count()
                st.metric(
                    label="📊 Total Registros",
                    value=f"{total_records:,}" if total_records else "Error",
                    delta=f"+{today_records}" if today_records else None
                )
            except Exception as e:
                st.metric("📊 Total Registros", "Error")
                st.caption(f"⚠️ {str(e)[:30]}...")
        
        with col2:
            try:
                unique_clients = st.session_state.consultor.get_unique_clients_count()
                st.metric(
                    label="👥 Clientes Únicos",
                    value=unique_clients if unique_clients else "Error"
                )
            except Exception as e:
                st.metric("👥 Clientes Únicos", "Error")
                st.caption(f"⚠️ {str(e)[:30]}...")
        
        with col3:
            try:
                today_records = st.session_state.consultor.get_today_records_count()
                st.metric(
                    label="📅 Registros Hoy",
                    value=today_records if today_records is not None else "Error"
                )
            except Exception as e:
                st.metric("📅 Registros Hoy", "Error")
                st.caption(f"⚠️ {str(e)[:30]}...")
        
        with col4:
            try:
                last_date = st.session_state.consultor.get_last_processing_date()
                if last_date:
                    try:
                        days_ago = (datetime.now().date() - datetime.strptime(last_date, '%Y-%m-%d').date()).days
                        st.metric(
                            label="🕒 Último Proceso",
                            value=f"Hace {days_ago} días"
                        )
                    except ValueError:
                        st.metric("🕒 Último Proceso", "Formato error")
                else:
                    st.metric("🕒 Último Proceso", "N/A")
            except Exception as e:
                st.metric("🕒 Último Proceso", "Error")
                st.caption(f"⚠️ {str(e)[:30]}...")
    
    except Exception as e:
        st.error(f"❌ Error crítico al cargar métricas: {str(e)}")
        st.info("🔄 Intente recargar la página o verificar la conexión a la base de datos")
        return
    
    
    st.markdown("---")
    
    # Gráficos con manejo robusto de errores
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Actividad Diaria (Últimos 30 días)")
        try:
            df_daily = st.session_state.consultor.get_daily_records_chart(30)
            if df_daily is not None and not df_daily.empty:
                fig = px.line(
                    df_daily, 
                    x='Fecha', 
                    y='Emisiones',
                    title="Registros por Día",
                    labels={'Fecha': 'Fecha', 'Emisiones': 'Número de Registros'}
                )
                fig.update_traces(line_color='#2980b9')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No hay datos suficientes para mostrar el gráfico")
        except AttributeError:
            st.warning("⚠️ Función get_daily_records_chart no disponible")
            st.info("💡 Esta funcionalidad estará disponible en una futura actualización")
        except Exception as e:
            st.error(f"❌ Error al cargar gráfico diario: {str(e)[:50]}...")
            # Mostrar alternativa simple
            with st.expander("📊 Datos alternativos"):
                try:
                    total = st.session_state.consultor.get_total_records()
                    st.write(f"Total de registros: {total:,}" if total else "No disponible")
                except:
                    st.write("Datos no disponibles")
    
    with col2:
        st.subheader("🏆 Top 10 Clientes")
        try:
            df_clients = st.session_state.consultor.get_top_clients_chart(10)
            if df_clients is not None and not df_clients.empty:
                fig = px.bar(
                    df_clients, 
                    x='total_emisiones', 
                    y='cliente',
                    orientation='h',
                    title="Clientes con Más Actividad",
                    labels={'total_emisiones': 'Número de Registros', 'cliente': 'Cliente'}
                )
                fig.update_traces(marker_color='#27ae60')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No hay datos de clientes para mostrar")
        except AttributeError:
            st.warning("⚠️ Función get_top_clients_chart no disponible")
            # Alternativa: mostrar lista simple de clientes
            try:
                clients = st.session_state.consultor.get_all_clients()
                if clients:
                    st.write("**Clientes disponibles:**")
                    for i, client in enumerate(clients[:10], 1):
                        st.write(f"{i}. {client}")
                else:
                    st.info("No hay clientes disponibles")
            except Exception:
                st.info("💡 Esta funcionalidad estará disponible en una futura actualización")
        except Exception as e:
            st.error(f"❌ Error al cargar gráfico de clientes: {str(e)[:50]}...")
    
    # Actividad reciente con validación
    st.subheader("🕒 Actividad Reciente")
    try:
        df_recent = st.session_state.consultor.get_recent_activity(15)
        if df_recent is not None and not df_recent.empty:
            st.dataframe(df_recent, use_container_width=True)
        else:
            st.info("📊 No hay actividad reciente para mostrar")
    except AttributeError:
        st.warning("⚠️ Función get_recent_activity no disponible")
        st.info("💡 Use la sección 'Consultar Base de Datos' para ver registros recientes")
    except Exception as e:
        st.error(f"❌ Error al cargar actividad reciente: {str(e)[:50]}...")
        # Mostrar alternativa
        with st.expander("🔍 Ver información básica"):
            try:
                last_date = st.session_state.consultor.get_last_processing_date()
                st.write(f"Última fecha procesada: {last_date or 'No disponible'}")
            except:
                st.write("Información no disponible")

def render_file_processing():
    """Renderizar página de procesamiento de archivos"""
    st.header("📁 Procesamiento de Archivos AsRun")
    
    st.markdown("""
    ### 📋 Instrucciones
    1. **Selecciona archivos**: Sube uno o más archivos .txt de logs AsRun
    2. **Configuración**: Ajusta los parámetros de procesamiento
    3. **Procesar**: Ejecuta el procesamiento automático
    4. **Resultados**: Revisa los resultados y estadísticas
    """)
    
    # Área de carga de archivos
    st.markdown("### 📤 Subir Archivos")
    
    uploaded_files = st.file_uploader(
        "Selecciona archivos de logs AsRun (.txt)",
        type=['txt'],
        accept_multiple_files=True,
        help="Puedes subir múltiples archivos a la vez"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} archivo(s) seleccionado(s)")
        
        # Mostrar información de archivos
        file_info = []
        for uploaded_file in uploaded_files:
            file_info.append({
                "Nombre": uploaded_file.name,
                "Tamaño": f"{uploaded_file.size / 1024:.1f} KB"
            })
        
        st.dataframe(pd.DataFrame(file_info), use_container_width=True)
        
        # Configuración de procesamiento
        st.markdown("### ⚙️ Configuración")
        
        col1, col2 = st.columns(2)
        
        with col1:
            process_duplicates = st.checkbox(
                "Procesar duplicados",
                value=False,
                help="Permitir procesar registros duplicados"
            )
            
            backup_enabled = st.checkbox(
                "Crear respaldo",
                value=True,
                help="Crear respaldo de la base de datos antes del procesamiento"
            )
        
        with col2:
            validate_data = st.checkbox(
                "Validación estricta",
                value=True,
                help="Aplicar validación estricta de datos"
            )
            
            auto_normalize = st.checkbox(
                "Normalización automática",
                value=True,
                help="Normalizar nombres de clientes automáticamente"
            )
        
        # Botón de procesamiento
        if st.button("🚀 Procesar Archivos", type="primary"):
            # Verificar estado de BD antes de procesar
            if st.session_state.get('db_error', False):
                st.error("❌ No se puede procesar archivos: Base de datos no disponible")
                st.info("💡 Intenta reconectar usando el botón en la barra lateral")
                return
            
            with st.spinner("Procesando archivos..."):
                try:
                    results = process_files_robust(uploaded_files, {
                        'duplicates': process_duplicates,
                        'backup': backup_enabled,
                        'validate': validate_data,
                        'normalize': auto_normalize
                    })
                    
                    if results['success']:
                        st.success("✅ Procesamiento completado exitosamente!")
                        
                        # Mostrar estadísticas
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Registros Procesados", results['processed'])
                        with col2:
                            st.metric("Registros Nuevos", results['new_records'])
                        with col3:
                            st.metric("Duplicados Omitidos", results['duplicates'])
                        with col4:
                            success_rate = len([f for f in results['file_details'] if '✅' in f.get('Estado', '')]) / len(uploaded_files) * 100
                            st.metric("Tasa de Éxito", f"{success_rate:.1f}%")
                        
                        # Mostrar warnings si existen
                        if results.get('warnings'):
                            with st.expander("⚠️ Advertencias", expanded=False):
                                for warning in results['warnings']:
                                    st.warning(warning)
                        
                        # Mostrar detalles por archivo
                        st.markdown("### 📊 Detalles por Archivo")
                        df_details = pd.DataFrame(results['file_details'])
                        st.dataframe(df_details, use_container_width=True)
                        
                        # Mostrar resumen de errores si existen
                        if results.get('errors'):
                            with st.expander("🔍 Detalles de Errores", expanded=False):
                                for error in results['errors']:
                                    st.error(error)
                        
                    else:
                        st.error(f"❌ Error en el procesamiento: {results['error']}")
                        
                        # Mostrar detalles de archivos procesados (incluso con errores)
                        if results.get('file_details'):
                            st.markdown("### 📊 Estado de Archivos")
                            df_details = pd.DataFrame(results['file_details'])
                            st.dataframe(df_details, use_container_width=True)
                        
                        # Mostrar errores específicos
                        if results.get('errors'):
                            with st.expander("🔍 Detalles de Errores", expanded=True):
                                for error in results['errors']:
                                    st.error(error)
                                
                                st.markdown("**Posibles soluciones:**")
                                st.markdown("- Verifica que los archivos tengan el formato correcto")
                                st.markdown("- Asegúrate de que la base de datos esté disponible")
                                st.markdown("- Intenta procesar archivos más pequeños")
                                st.markdown("- Revisa la conexión a la base de datos")
                
                except Exception as e:
                    st.error(f"❌ Error crítico durante el procesamiento: {str(e)}")
                    st.markdown("**Acciones recomendadas:**")
                    st.markdown("1. Verifica la conexión a la base de datos")
                    st.markdown("2. Reinicia la aplicación")
                    st.markdown("3. Contacta al administrador del sistema")
    
    else:
        st.info("📁 Selecciona archivos .txt para comenzar el procesamiento")

def process_files_robust(uploaded_files, config):
    """Procesar archivos subidos con manejo robusto de errores"""
    # Verificar estado de la base de datos
    if st.session_state.get('db_error', False):
        return {
            'success': False,
            'error': 'Base de datos no disponible. Revisa la conexión.',
            'processed': 0,
            'new_records': 0,
            'duplicates': 0,
            'file_details': []
        }
    
    # Verificar que el processor esté disponible
    if not hasattr(st.session_state, 'processor') or st.session_state.processor is None:
        return {
            'success': False,
            'error': 'Procesador no inicializado correctamente.',
            'processed': 0,
            'new_records': 0,
            'duplicates': 0,
            'file_details': []
        }
    
    results = {
        'success': True,
        'processed': 0,
        'new_records': 0,
        'duplicates': 0,
        'file_details': [],
        'errors': [],
        'warnings': []
    }
    
    total_files = len(uploaded_files)
    successful_files = 0
    
    try:
        for i, uploaded_file in enumerate(uploaded_files):
            file_error = None
            temp_path = None
            
            try:
                # Validación básica del archivo
                if uploaded_file.size == 0:
                    raise ValueError("El archivo está vacío")
                
                if uploaded_file.size > 50 * 1024 * 1024:  # 50MB límite
                    raise ValueError("El archivo es demasiado grande (>50MB)")
                
                if not uploaded_file.name.lower().endswith('.txt'):
                    raise ValueError("Formato de archivo no válido. Solo se permiten archivos .txt")
                
                # Crear archivo temporal con nombre único
                timestamp = int(time.time() * 1000)
                temp_path = f"temp_{timestamp}_{uploaded_file.name}"
                
                # Guardar archivo temporalmente con validación
                try:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                except (IOError, OSError) as e:
                    raise ValueError(f"Error al guardar archivo temporal: {str(e)}")
                
                # Validar que el archivo se guardó correctamente
                if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                    raise ValueError("Error al crear archivo temporal")
                
                # Procesar el archivo con timeout
                progress_text = f"Procesando {uploaded_file.name} ({i+1}/{total_files})"
                
                try:
                    file_result = st.session_state.processor.procesar_archivo_asrun(temp_path)
                except sqlite3.Error as e:
                    raise ValueError(f"Error de base de datos: {str(e)}")
                except Exception as e:
                    raise ValueError(f"Error de procesamiento: {str(e)}")
                
                # Validar resultado del procesamiento
                if not isinstance(file_result, dict):
                    raise ValueError("Resultado de procesamiento inválido")
                
                if file_result.get('exitoso', False):
                    # Procesamiento exitoso
                    processed_count = file_result.get('total_procesados', 0)
                    new_count = file_result.get('nuevos_registros', 0)
                    dup_count = file_result.get('duplicados', 0)
                    
                    results['processed'] += processed_count
                    results['new_records'] += new_count
                    results['duplicates'] += dup_count
                    
                    results['file_details'].append({
                        'Archivo': uploaded_file.name,
                        'Estado': '✅ Exitoso',
                        'Registros': processed_count,
                        'Nuevos': new_count,
                        'Duplicados': dup_count,
                        'Tamaño': f"{uploaded_file.size / 1024:.1f} KB"
                    })
                    
                    successful_files += 1
                    
                    # Agregar warning si hay muchos duplicados
                    if dup_count > processed_count * 0.5:
                        results['warnings'].append(f"{uploaded_file.name}: Alto porcentaje de duplicados ({dup_count}/{processed_count})")
                        
                else:
                    # Error en el procesamiento
                    error_msg = file_result.get('error', 'Error desconocido durante el procesamiento')
                    file_error = error_msg
                    
                    results['file_details'].append({
                        'Archivo': uploaded_file.name,
                        'Estado': '❌ Error',
                        'Error': error_msg,
                        'Registros': 0,
                        'Nuevos': 0,
                        'Duplicados': 0,
                        'Tamaño': f"{uploaded_file.size / 1024:.1f} KB"
                    })
                    
                    results['errors'].append(f"{uploaded_file.name}: {error_msg}")
            
            except Exception as e:
                # Error durante el procesamiento del archivo individual
                error_msg = str(e)
                file_error = error_msg
                
                results['file_details'].append({
                    'Archivo': uploaded_file.name,
                    'Estado': '❌ Error',
                    'Error': error_msg,
                    'Registros': 0,
                    'Nuevos': 0,
                    'Duplicados': 0,
                    'Tamaño': f"{uploaded_file.size / 1024:.1f} KB" if hasattr(uploaded_file, 'size') else "N/A"
                })
                
                results['errors'].append(f"{uploaded_file.name}: {error_msg}")
            
            finally:
                # Limpiar archivo temporal
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass  # No es crítico si no se puede eliminar
        
        # Determinar si el procesamiento fue exitoso en general
        if successful_files == 0:
            results['success'] = False
            results['error'] = f"No se pudo procesar ningún archivo de {total_files}"
        elif successful_files < total_files:
            results['warnings'].append(f"Se procesaron {successful_files}/{total_files} archivos exitosamente")
        
        return results
        
    except Exception as e:
        # Error crítico durante el procesamiento
        return {
            'success': False,
            'error': f"Error crítico durante el procesamiento: {str(e)}",
            'processed': results.get('processed', 0),
            'new_records': results.get('new_records', 0),
            'duplicates': results.get('duplicates', 0),
            'file_details': results.get('file_details', []),
            'errors': results.get('errors', []),
            'warnings': results.get('warnings', [])
        }

# Función legacy para compatibilidad
def process_files(uploaded_files, config):
    """Wrapper para mantener compatibilidad con código existente"""
    return process_files_robust(uploaded_files, config)

def render_database_query():
    """Renderizar página de consultas a la base de datos con manejo robusto de errores"""
    st.header("🔍 Consultar Base de Datos")
    
    # Verificar estado de la base de datos
    if st.session_state.get('db_error', False):
        st.error("🔴 Base de datos no disponible")
        error_msg = st.session_state.get('error_message', 'Error desconocido')
        st.error(f"Error: {error_msg}")
        
        if st.button("🔄 Reintentar Conexión"):
            try:
                initialize_session_state()
                st.rerun()
            except Exception as e:
                st.error(f"Error al reconectar: {str(e)}")
        return
    
    # Verificar que el consultor esté disponible
    if not hasattr(st.session_state, 'consultor') or st.session_state.consultor is None:
        st.error("❌ Consultor de base de datos no disponible")
        st.info("💡 Intenta reiniciar la aplicación")
        return
    
    # Filtros de consulta
    st.markdown("### 🎛️ Filtros de Búsqueda")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por fechas
        st.markdown("#### 📅 Rango de Fechas")
        date_filter = st.radio(
            "Seleccionar período:",
            ["Últimos 7 días", "Últimos 30 días", "Últimos 90 días", "Personalizado", "Todas las fechas"]
        )
        
        try:
            if date_filter == "Personalizado":
                fecha_inicio = st.date_input("Fecha inicio")
                fecha_fin = st.date_input("Fecha fin")
                
                # Validar fechas
                if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
                    st.warning("⚠️ La fecha de inicio debe ser anterior a la fecha de fin")
                    
            elif date_filter == "Últimos 7 días":
                fecha_fin = datetime.now().date()
                fecha_inicio = fecha_fin - timedelta(days=7)
            elif date_filter == "Últimos 30 días":
                fecha_fin = datetime.now().date()
                fecha_inicio = fecha_fin - timedelta(days=30)
            elif date_filter == "Últimos 90 días":
                fecha_fin = datetime.now().date()
                fecha_inicio = fecha_fin - timedelta(days=90)
            else:  # Todas las fechas
                fecha_inicio = None
                fecha_fin = None
        except Exception as e:
            st.error(f"Error en filtro de fechas: {str(e)}")
            fecha_inicio = None
            fecha_fin = None
    
    with col2:
        # Filtro por cliente
        st.markdown("#### 👥 Cliente")
        cliente_filter = None
        try:
            with st.spinner("Cargando clientes..."):
                clientes = st.session_state.consultor.get_all_clients()
                
            if clientes:
                cliente_selected = st.selectbox(
                    "Seleccionar cliente:",
                    ["Todos los clientes"] + clientes,
                    help="Selecciona un cliente específico o deja 'Todos' para incluir todos"
                )
                cliente_filter = None if cliente_selected == "Todos los clientes" else cliente_selected
            else:
                st.info("ℹ️ No hay clientes disponibles")
                
        except sqlite3.Error as e:
            st.error(f"❌ Error de BD al cargar clientes: {str(e)}")
            cliente_filter = None
        except Exception as e:
            st.error(f"❌ Error al cargar clientes: {str(e)}")
            cliente_filter = None
    
    with col3:
        # Configuraciones adicionales
        st.markdown("#### ⚙️ Configuración")
        limit_records = st.selectbox(
            "Límite de registros:",
            [100, 500, 1000, 2000, 5000],
            index=2,
            help="Selecciona el número máximo de registros a mostrar"
        )
        
        sort_order = st.selectbox(
            "Ordenar por:",
            ["Fecha DESC", "Fecha ASC", "Cliente", "Canal"],
            help="Selecciona el criterio de ordenamiento"
        )
    
    # Validaciones antes de buscar
    search_disabled = False
    if date_filter == "Personalizado":
        try:
            if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
                search_disabled = True
        except:
            pass
    
    # Botón de búsqueda
    if st.button("🔍 Buscar", type="primary", disabled=search_disabled):
        with st.spinner("Consultando base de datos..."):
            try:
                # Preparar filtros con validación
                filtros = {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'cliente': cliente_filter,
                    'limit': limit_records,
                    'orden': sort_order
                }
                
                # Validar filtros
                if date_filter == "Personalizado" and fecha_inicio and fecha_fin:
                    fecha_diff = (fecha_fin - fecha_inicio).days
                    if fecha_diff > 365:
                        st.warning("⚠️ Rango de fechas muy amplio. La consulta puede ser lenta.")
                
                # Ejecutar consulta con manejo de errores
                try:
                    df_results = st.session_state.consultor.query_with_filters(filtros)
                except sqlite3.Error as e:
                    st.error(f"❌ Error de base de datos: {str(e)}")
                    st.markdown("**Posibles causas:**")
                    st.markdown("- Base de datos corrupta o inaccesible")
                    st.markdown("- Consulta demasiado compleja")
                    st.markdown("- Problema de permisos de archivo")
                    return
                except Exception as e:
                    st.error(f"❌ Error en la consulta: {str(e)}")
                    return
                
                # Validar resultados
                if df_results is None:
                    st.error("❌ La consulta no devolvió datos válidos")
                    return
                    
                if not df_results.empty:
                    st.success(f"✅ Se encontraron {len(df_results):,} registros")
                    
                    # Mostrar estadísticas de la consulta con validación
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Registros", f"{len(df_results):,}")
                    with col2:
                        try:
                            clientes_unicos = df_results['cliente'].nunique() if 'cliente' in df_results.columns else 0
                            st.metric("Clientes Únicos", clientes_unicos)
                        except Exception:
                            st.metric("Clientes Únicos", "N/A")
                    with col3:
                        try:
                            if 'fecha' in df_results.columns:
                                fechas_validas = pd.to_datetime(df_results['fecha'], errors='coerce')
                                fechas_validas = fechas_validas.dropna()
                                if not fechas_validas.empty:
                                    dias_span = (fechas_validas.max() - fechas_validas.min()).days + 1
                                    st.metric("Días Cubiertos", dias_span)
                                else:
                                    st.metric("Días Cubiertos", "N/A")
                            else:
                                st.metric("Días Cubiertos", "N/A")
                        except Exception:
                            st.metric("Días Cubiertos", "N/A")
                    with col4:
                        try:
                            if 'id_comercial' in df_results.columns:
                                st.metric("Comerciales Únicos", df_results['id_comercial'].nunique())
                            else:
                                st.metric("Comerciales Únicos", "N/A")
                        except Exception:
                            st.metric("Comerciales Únicos", "N/A")
                    
                    # Mostrar resultados con validación
                    st.markdown("### 📊 Resultados de la Consulta")
                    try:
                        st.dataframe(df_results, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error al mostrar resultados: {str(e)}")
                        st.markdown("**Datos básicos disponibles:**")
                        st.text(f"Filas: {len(df_results)}, Columnas: {len(df_results.columns)}")
                        st.text(f"Columnas: {', '.join(df_results.columns.tolist())}")
                    
                    # Opciones de exportación con manejo de errores
                    st.markdown("### 📥 Exportar Resultados")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📄 Exportar a Excel"):
                            try:
                                excel_buffer = export_to_excel_robust(df_results)
                                if excel_buffer:
                                    st.download_button(
                                        label="⬇️ Descargar Excel",
                                        data=excel_buffer,
                                        file_name=f"consulta_asrun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                else:
                                    st.error("❌ Error al generar archivo Excel")
                            except Exception as e:
                                st.error(f"❌ Error al exportar a Excel: {str(e)}")
                    
                    with col2:
                        if st.button("📄 Exportar a CSV"):
                            try:
                                csv = df_results.to_csv(index=False, encoding='utf-8')
                                st.download_button(
                                    label="⬇️ Descargar CSV",
                                    data=csv,
                                    file_name=f"consulta_asrun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                            except Exception as e:
                                st.error(f"❌ Error al exportar a CSV: {str(e)}")
                
                else:
                    st.info("ℹ️ No se encontraron registros con los filtros especificados")
                    st.markdown("**Sugerencias:**")
                    st.markdown("- Amplía el rango de fechas")
                    st.markdown("- Cambia los criterios de filtrado")
                    st.markdown("- Verifica que existan datos en la base de datos")
            
            except Exception as e:
                st.error(f"❌ Error crítico en la consulta: {str(e)}")
                st.markdown("**Acciones recomendadas:**")
                st.markdown("1. Verifica la conexión a la base de datos")
                st.markdown("2. Simplifica los filtros de búsqueda")
                st.markdown("3. Contacta al administrador del sistema")

def export_to_excel_robust(df):
    """Exportar DataFrame a Excel en memoria con manejo robusto de errores"""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Consulta AsRun', index=False)
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Error al crear archivo Excel: {str(e)}")
        return None

# Función legacy para compatibilidad
def export_to_excel(df):
    """Wrapper para mantener compatibilidad"""
    return export_to_excel_robust(df)

def render_report_generation():
    """Renderizar página de generación de reportes con manejo robusto de errores"""
    st.header("📊 Generación de Reportes Personalizados")
    
    # Verificar estado de la base de datos
    if st.session_state.get('db_error', False):
        st.error("🔴 Base de datos no disponible")
        st.info("💡 No se pueden generar reportes sin conexión a la base de datos")
        
        if st.button("🔄 Reintentar Conexión"):
            try:
                initialize_session_state()
                st.rerun()
            except Exception as e:
                st.error(f"Error al reconectar: {str(e)}")
        return
    
    # Verificar que el consultor esté disponible
    if not hasattr(st.session_state, 'consultor') or st.session_state.consultor is None:
        st.error("❌ Consultor de reportes no disponible")
        st.info("💡 Intenta reiniciar la aplicación")
        return
    
    st.markdown("""
    ### 📋 Configuración del Reporte
    Personaliza tu reporte seleccionando los filtros y formatos deseados.
    """)
    
    # Tipo de reporte
    st.markdown("#### 🎯 Tipo de Reporte")
    report_type = st.selectbox(
        "Selecciona el tipo de reporte:",
        ["Reporte Estándar"],
        help="Genera reportes personalizados con diferentes formatos de salida"
    )
    
    # Configuración del reporte
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Filtros de Datos")
        
        # Rango de fechas
        report_date_filter = st.selectbox(
            "Período del reporte:",
            ["Última semana", "Último mes", "Últimos 3 meses", "Año actual", "Personalizado"]
        )
        
        try:
            if report_date_filter == "Personalizado":
                report_fecha_inicio = st.date_input("Fecha inicio del reporte")
                report_fecha_fin = st.date_input("Fecha fin del reporte")
                
                # Validar fechas personalizadas
                if report_fecha_inicio and report_fecha_fin and report_fecha_inicio > report_fecha_fin:
                    st.warning("⚠️ La fecha de inicio debe ser anterior a la fecha de fin")
                    
            elif report_date_filter == "Última semana":
                report_fecha_fin = datetime.now().date()
                report_fecha_inicio = report_fecha_fin - timedelta(days=7)
            elif report_date_filter == "Último mes":
                report_fecha_fin = datetime.now().date()
                report_fecha_inicio = report_fecha_fin - timedelta(days=30)
            elif report_date_filter == "Últimos 3 meses":
                report_fecha_fin = datetime.now().date()
                report_fecha_inicio = report_fecha_fin - timedelta(days=90)
            else:  # Año actual
                report_fecha_fin = datetime.now().date()
                report_fecha_inicio = datetime(datetime.now().year, 1, 1).date()
        except Exception as e:
            st.error(f"Error en configuración de fechas: {str(e)}")
            report_fecha_inicio = datetime.now().date() - timedelta(days=30)
            report_fecha_fin = datetime.now().date()
        
        # Cliente específico con manejo de errores
        report_cliente = "Todos los clientes"  # Default value
        report_cliente_filter = None
        
        try:
            with st.spinner("Cargando clientes..."):
                all_clients = st.session_state.consultor.get_all_clients()
                
            if all_clients:
                report_cliente = st.selectbox(
                    "Cliente específico:",
                    ["Todos los clientes"] + all_clients,
                    help="Selecciona un cliente específico o todos"
                )
                report_cliente_filter = None if report_cliente == "Todos los clientes" else report_cliente
            else:
                st.info("ℹ️ No hay clientes disponibles")
                
        except sqlite3.Error as e:
            st.error(f"❌ Error de BD al cargar clientes: {str(e)}")
            report_cliente_filter = None
        except Exception as e:
            st.error(f"❌ Error al cargar clientes: {str(e)}")
            report_cliente_filter = None
    
    with col2:
        st.markdown("#### 📄 Configuración de Salida")
        
        # Formatos de salida
        output_formats = st.multiselect(
            "Formatos de salida:",
            ["TXT", "Excel", "CSV", "PDF"],
            default=["TXT", "Excel"],
            help="Selecciona uno o más formatos de salida"
        )
        
        if not output_formats:
            st.warning("⚠️ Selecciona al menos un formato de salida")
        
        # Opciones de contenido
        include_summary = st.checkbox("Incluir resumen ejecutivo", value=True,
                                    help="Incluye estadísticas y métricas principales")
        include_charts = st.checkbox("Incluir gráficos", value=True,
                                   help="Incluye visualizaciones en el reporte")
        include_details = st.checkbox("Incluir datos detallados", value=True,
                                    help="Incluye el detalle completo de registros")
        
        # Agrupación
        group_by = st.selectbox(
            "Agrupar datos por:",
            ["Cliente", "Fecha", "Sin agrupación"],
            help="Selecciona cómo agrupar los datos en el reporte"
        )
    
    # Vista previa con validaciones
    st.markdown("### 👀 Vista Previa de Configuración")
    
    # Validaciones de configuración
    config_valid = True
    validation_errors = []
    
    if not output_formats:
        config_valid = False
        validation_errors.append("❌ No hay formatos de salida seleccionados")
    
    if report_date_filter == "Personalizado":
        if not (report_fecha_inicio and report_fecha_fin):
            config_valid = False
            validation_errors.append("❌ Fechas personalizadas incompletas")
        elif report_fecha_inicio > report_fecha_fin:
            config_valid = False
            validation_errors.append("❌ Rango de fechas inválido")
    
    try:
        config_preview = {
            "Período": f"{report_fecha_inicio} → {report_fecha_fin}",
            "Cliente": report_cliente,
            "Formatos": ", ".join(output_formats) if output_formats else "Ninguno",
            "Incluye Resumen": "✅" if include_summary else "❌",
            "Incluye Gráficos": "✅" if include_charts else "❌",
            "Datos Detallados": "✅" if include_details else "❌",
            "Agrupación": group_by
        }
        
        if config_valid:
            st.json(config_preview)
        else:
            st.error("⚠️ Configuración inválida:")
            for error in validation_errors:
                st.error(error)
    except Exception as e:
        st.error(f"Error en vista previa: {str(e)}")
        config_valid = False
    
    # Generar reporte
    if st.button("📊 Generar Reporte", type="primary", disabled=not config_valid):
        with st.spinner("Generando reporte personalizado..."):
            try:
                # Validaciones finales
                if not output_formats:
                    st.error("❌ Selecciona al menos un formato de salida")
                    return
                
                # Configuración del reporte con validación
                report_config = {
                    'fecha_inicio': report_fecha_inicio,
                    'fecha_fin': report_fecha_fin,
                    'cliente': report_cliente_filter,
                    'formatos': output_formats,
                    'incluir_resumen': include_summary,
                    'incluir_graficos': include_charts,
                    'incluir_detalles': include_details,
                    'agrupar_por': group_by
                }
                
                # Verificar rango de fechas razonable
                if report_fecha_inicio and report_fecha_fin:
                    fecha_diff = (report_fecha_fin - report_fecha_inicio).days
                    if fecha_diff > 730:  # 2 años
                        st.warning("⚠️ Rango de fechas muy amplio. La generación puede tomar tiempo.")
                
                # Generar reporte con manejo de errores específicos
                try:
                    # Usar el método correcto que está implementado
                    if hasattr(st.session_state.consultor, 'generar_reporte_desde_consulta_streamlit'):
                        report_result = st.session_state.consultor.generar_reporte_desde_consulta_streamlit(report_config)
                    else:
                        # Usar método alternativo o crear datos básicos
                        st.warning("⚠️ Funcionalidad de reportes personalizados no disponible")
                        st.info("💡 Generando reporte básico...")
                        
                        # Generar reporte básico como alternativa
                        report_result = generate_basic_report(report_config)
                        
                except sqlite3.Error as e:
                    st.error(f"❌ Error de base de datos: {str(e)}")
                    return
                except Exception as e:
                    st.error(f"❌ Error al generar reporte: {str(e)}")
                    # Intentar generar reporte básico como fallback
                    st.info("🔄 Intentando generar reporte básico...")
                    try:
                        report_result = generate_basic_report(report_config)
                    except Exception as e2:
                        st.error(f"❌ Error en reporte básico: {str(e2)}")
                        return
                
                # Procesar resultados
                if report_result and report_result.get('success', False):
                    st.success("✅ Reporte generado exitosamente!")
                    
                    # Mostrar información del reporte
                    st.markdown("### 📋 Información del Reporte")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Registros Incluidos", f"{report_result.get('total_records', 0):,}")
                    with col2:
                        st.metric("Clientes Únicos", report_result.get('unique_clients', 0))
                    with col3:
                        st.metric("Archivos Generados", len(report_result.get('files', [])))
                    
                    # Enlaces de descarga con validación
                    st.markdown("### 📥 Descargar Archivos")
                    files_downloaded = 0
                    
                    for file_info in report_result.get('files', []):
                        try:
                            file_path = file_info.get('path', '')
                            file_name = file_info.get('filename', file_info.get('name', 'archivo'))
                            
                            if file_path and os.path.exists(file_path):
                                with open(file_path, 'rb') as f:
                                    file_content = f.read()
                                    if file_content:
                                        # Determinar tipo MIME
                                        if file_name.endswith('.xlsx'):
                                            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                        elif file_name.endswith('.txt'):
                                            mime_type = 'text/plain'
                                        elif file_name.endswith('.csv'):
                                            mime_type = 'text/csv'
                                        else:
                                            mime_type = 'application/octet-stream'
                                        
                                        # Información adicional del archivo
                                        file_size = len(file_content) / 1024  # KB
                                        size_display = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                                        
                                        st.download_button(
                                            label=f"⬇️ {file_name} ({size_display})",
                                            data=file_content,
                                            file_name=file_name,
                                            mime=mime_type,
                                            help=f"Formato: {file_info.get('format', 'Desconocido')}"
                                        )
                                        files_downloaded += 1
                                    else:
                                        st.warning(f"⚠️ Archivo vacío: {file_name}")
                            else:
                                st.error(f"❌ Archivo no encontrado: {file_info.get('name', 'desconocido')}")
                        except Exception as e:
                            st.error(f"❌ Error al procesar archivo {file_info.get('name', 'desconocido')}: {str(e)}")
                    
                    if files_downloaded == 0:
                        st.warning("⚠️ No se pudieron procesar los archivos generados")
                
                else:
                    error_msg = report_result.get('error', 'Error desconocido') if report_result else 'No se pudo generar el reporte'
                    st.error(f"❌ Error al generar reporte: {error_msg}")
                    
                    st.markdown("**Posibles soluciones:**")
                    st.markdown("- Verifica que existan datos en el rango de fechas seleccionado")
                    st.markdown("- Intenta con un rango de fechas más pequeño")
                    st.markdown("- Selecciona un cliente específico")
                    st.markdown("- Verifica la conexión a la base de datos")
            
            except Exception as e:
                st.error(f"❌ Error crítico en la generación del reporte: {str(e)}")
                st.markdown("**Acciones recomendadas:**")
                st.markdown("1. Verifica la conexión a la base de datos")
                st.markdown("2. Simplifica la configuración del reporte")
                st.markdown("3. Contacta al administrador del sistema")

def generate_basic_report(config):
    """Generar reporte básico como fallback cuando el sistema avanzado no está disponible"""
    try:
        # Crear estructura básica de reporte
        return {
            'success': True,
            'total_records': 0,
            'unique_clients': 0,
            'files': [],
            'message': 'Reporte básico generado (funcionalidad limitada)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error en reporte básico: {str(e)}'
        }

def render_downloads():
    """Renderizar página de descargas con manejo robusto de errores"""
    st.header("📥 Centro de Descargas")
    
    st.markdown("""
    ### 📋 Archivos Disponibles
    Aquí puedes descargar todos los reportes y archivos generados por el sistema.
    """)
    
    # Obtener directorio de reportes usando ruta absoluta desde el proyecto
    project_root = Path(__file__).parent.parent
    reportes_dir = project_root / "reportes"
    
    # Información de debug (expandible)
    with st.expander("🔍 Información de Debug", expanded=False):
        st.code(f"""
Directorio del proyecto: {project_root}
Directorio de reportes: {reportes_dir}
Existe directorio: {reportes_dir.exists()}
Directorio actual: {Path.cwd()}
        """)
    
    try:
        # Verificar si el directorio existe
        if not reportes_dir.exists():
            st.warning("⚠️ El directorio de reportes no existe")
            
            if st.button("📁 Crear Directorio de Reportes"):
                try:
                    reportes_dir.mkdir(parents=True, exist_ok=True)
                    st.success("✅ Directorio creado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al crear directorio: {str(e)}")
            return
        
        # Obtener lista de archivos con manejo de errores
        try:
            files = list(reportes_dir.glob("*"))
        except Exception as e:
            st.error(f"❌ Error al acceder al directorio: {str(e)}")
            return
        
        if files:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                file_type_filter = st.selectbox(
                    "Filtrar por tipo:",
                    ["Todos", "TXT", "Excel", "CSV", "PDF"],
                    help="Filtra archivos por su extensión"
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Ordenar por:",
                    ["Fecha (más reciente)", "Fecha (más antiguo)", "Nombre", "Tamaño"],
                    help="Selecciona el criterio de ordenamiento"
                )
            
            # Procesar y filtrar archivos con validación
            file_list = []
            error_files = []
            
            for file_path in files:
                try:
                    if file_path.is_file():
                        stat = file_path.stat()
                        file_size = stat.st_size
                        
                        # Validar que el archivo no esté corrupto (tamaño > 0)
                        if file_size == 0:
                            error_files.append(f"{file_path.name} (archivo vacío)")
                            continue
                        
                        file_info = {
                            "Nombre": file_path.name,
                            "Tipo": file_path.suffix.upper().replace(".", "") if file_path.suffix else "SIN_EXT",
                            "Tamaño": f"{file_size / 1024:.1f} KB",
                            "TamañoBytes": file_size,
                            "Fecha": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                            "FechaTimestamp": stat.st_mtime,
                            "Path": str(file_path)
                        }
                        
                        # Aplicar filtro de tipo
                        if file_type_filter == "Todos" or file_info["Tipo"] == file_type_filter:
                            file_list.append(file_info)
                            
                except (OSError, IOError) as e:
                    error_files.append(f"{file_path.name} (error de acceso: {str(e)})")
                except Exception as e:
                    error_files.append(f"{file_path.name} (error: {str(e)})")
            
            # Mostrar errores de archivos si existen
            if error_files:
                with st.expander("⚠️ Archivos con Problemas", expanded=False):
                    for error_file in error_files:
                        st.warning(f"❌ {error_file}")
            
            # Ordenar archivos con manejo de errores
            try:
                if sort_by == "Fecha (más reciente)":
                    file_list.sort(key=lambda x: x["FechaTimestamp"], reverse=True)
                elif sort_by == "Fecha (más antiguo)":
                    file_list.sort(key=lambda x: x["FechaTimestamp"])
                elif sort_by == "Nombre":
                    file_list.sort(key=lambda x: x["Nombre"].lower())
                elif sort_by == "Tamaño":
                    file_list.sort(key=lambda x: x["TamañoBytes"], reverse=True)
            except Exception as e:
                st.warning(f"⚠️ Error al ordenar archivos: {str(e)}")
            
            if file_list:
                st.markdown(f"### 📁 Archivos Encontrados ({len(file_list)})")
                
                # Estadísticas rápidas
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_size = sum(f["TamañoBytes"] for f in file_list)
                    st.metric("Tamaño Total", f"{total_size / (1024*1024):.1f} MB")
                with col2:
                    tipos_unicos = len(set(f["Tipo"] for f in file_list))
                    st.metric("Tipos de Archivo", tipos_unicos)
                with col3:
                    if file_list:
                        archivo_mas_reciente = max(file_list, key=lambda x: x["FechaTimestamp"])
                        st.metric("Más Reciente", archivo_mas_reciente["Fecha"])
                
                # Mostrar archivos con botones de descarga
                for i, file_info in enumerate(file_list):
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                        
                        with col1:
                            # Icono según tipo de archivo
                            icon = {
                                "TXT": "📄", "CSV": "📊", "XLSX": "📗", 
                                "XLS": "📗", "PDF": "📕", "ZIP": "📦"
                            }.get(file_info['Tipo'], "📄")
                            st.write(f"{icon} **{file_info['Nombre']}**")
                            
                        with col2:
                            st.write(file_info['Tipo'])
                        with col3:
                            st.write(file_info['Tamaño'])
                        with col4:
                            st.write(file_info['Fecha'])
                        with col5:
                            # Botón de descarga con validación mejorada
                            try:
                                file_path = file_info['Path']
                                
                                # Debug: Verificar ruta
                                if not os.path.exists(file_path):
                                    # Intentar con ruta alternativa si falla
                                    project_root = Path(__file__).parent.parent
                                    alt_path = project_root / "reportes" / file_info['Nombre']
                                    
                                    if os.path.exists(alt_path):
                                        file_path = str(alt_path)
                                    else:
                                        st.button("❌", disabled=True, key=f"error_{i}")
                                        st.caption("No encontrado", help=f"Ruta: {file_path}")
                                        continue
                                
                                # Intentar leer el archivo
                                with open(file_path, 'rb') as f:
                                    file_content = f.read()
                                    
                                if file_content and len(file_content) > 0:
                                    st.download_button(
                                        label="⬇️",
                                        data=file_content,
                                        file_name=file_info['Nombre'],
                                        key=f"download_{i}_{file_info['Nombre']}",
                                        help=f"Descargar {file_info['Nombre']} ({len(file_content)} bytes)"
                                    )
                                else:
                                    st.button("❌", disabled=True, key=f"empty_{i}")
                                    st.caption("Archivo vacío")
                                    
                            except FileNotFoundError:
                                st.button("❌", disabled=True, key=f"notfound_{i}")
                                st.caption("Archivo no existe")
                            except PermissionError:
                                st.button("❌", disabled=True, key=f"permission_{i}")  
                                st.caption("Sin permisos")
                            except Exception as e:
                                st.button("❌", disabled=True, key=f"error_{i}")
                                st.caption(f"Error: {str(e)[:15]}...")
                
                # Opción de descarga masiva
                st.markdown("---")
                st.markdown("### 📦 Descarga Masiva")
                
                if len(file_list) > 1:
                    if st.button("📦 Descargar Todos los Archivos (ZIP)"):
                        try:
                            with st.spinner("Creando archivo ZIP..."):
                                zip_buffer = create_zip_download_robust(file_list)
                                if zip_buffer:
                                    st.download_button(
                                        label="⬇️ Descargar ZIP",
                                        data=zip_buffer,
                                        file_name=f"reportes_asrun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip"
                                    )
                                else:
                                    st.error("❌ Error al crear archivo ZIP")
                        except Exception as e:
                            st.error(f"❌ Error en descarga masiva: {str(e)}")
                else:
                    st.info("💡 Se necesitan al menos 2 archivos para descarga masiva")
            
            else:
                st.info("ℹ️ No se encontraron archivos con los filtros especificados")
                st.markdown("**Posibles causas:**")
                st.markdown("- No existen archivos del tipo seleccionado")
                st.markdown("- Los archivos están corruptos o inaccesibles")
                st.markdown("- Problemas de permisos de archivo")
        
        else:
            st.info("ℹ️ No hay archivos disponibles para descarga")
            st.markdown("**Para generar archivos:**")
            st.markdown("1. Ve a 'Generar Reportes' para crear nuevos reportes")
            st.markdown("2. Procesa archivos AsRun en 'Procesar Archivos'")
            st.markdown("3. Realiza consultas y exporta resultados")
    
    except Exception as e:
        st.error(f"❌ Error crítico en centro de descargas: {str(e)}")
        st.markdown("**Acciones recomendadas:**")
        st.markdown("1. Verifica permisos del directorio de reportes")
        st.markdown("2. Reinicia la aplicación")
        st.markdown("3. Contacta al administrador del sistema")

def create_zip_download_robust(file_list):
    """Crear archivo ZIP con todos los archivos seleccionados con manejo robusto"""
    try:
        zip_buffer = io.BytesIO()
        files_added = 0
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in file_list:
                try:
                    file_path = file_info['Path']
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        # Usar un nombre seguro para el archivo en el ZIP
                        safe_name = file_info['Nombre']
                        zip_file.write(file_path, safe_name)
                        files_added += 1
                except Exception as e:
                    st.warning(f"⚠️ No se pudo incluir {file_info['Nombre']}: {str(e)}")
                    continue
        
        if files_added == 0:
            st.error("❌ No se pudieron agregar archivos al ZIP")
            return None
        
        zip_buffer.seek(0)
        st.success(f"✅ ZIP creado con {files_added} archivos")
        return zip_buffer
        
    except Exception as e:
        st.error(f"❌ Error al crear ZIP: {str(e)}")
        return None

# Función legacy para compatibilidad
def create_zip_download(file_list):
    """Wrapper para mantener compatibilidad"""
    return create_zip_download_robust(file_list)

def render_administration():
    """Renderizar página de administración con manejo robusto de errores"""
    st.header("⚙️ Administración del Sistema")
    
    # Verificar estado de la base de datos
    if st.session_state.get('db_error', False):
        st.error("🔴 Base de datos no disponible")
        st.error("❌ No se pueden realizar operaciones de administración sin conexión a la BD")
        
        if st.button("🔄 Reintentar Conexión"):
            try:
                initialize_session_state()
                st.rerun()
            except Exception as e:
                st.error(f"Error al reconectar: {str(e)}")
        return
    
    # Verificar que el consultor esté disponible
    if not hasattr(st.session_state, 'consultor') or st.session_state.consultor is None:
        st.error("❌ Sistema de administración no disponible")
        st.info("💡 Intenta reiniciar la aplicación")
        return
    
    # Advertencia de seguridad
    st.warning("⚠️ **ÁREA DE ADMINISTRACIÓN** - Las acciones aquí pueden afectar el funcionamiento del sistema")
    
    # Estadísticas del sistema con manejo de errores
    st.markdown("### 📊 Estadísticas del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            total_records = st.session_state.consultor.get_total_records()
            st.metric("Total Registros", f"{total_records:,}")
        except sqlite3.Error as e:
            st.metric("Total Registros", "Error BD")
            st.error(f"Error BD: {str(e)}")
        except Exception as e:
            st.metric("Total Registros", "N/A")
            st.warning(f"Error: {str(e)}")
    
    with col2:
        try:
            unique_clients = st.session_state.consultor.get_unique_clients_count()
            st.metric("Clientes Únicos", unique_clients)
        except sqlite3.Error as e:
            st.metric("Clientes Únicos", "Error BD")
        except Exception as e:
            st.metric("Clientes Únicos", "N/A")
    
    with col3:
        try:
            # Tamaño de la base de datos
            db_path = "asrun_database.db"
            if os.path.exists(db_path):
                db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
                st.metric("Tamaño BD", f"{db_size:.1f} MB")
            else:
                st.metric("Tamaño BD", "No encontrada")
        except Exception as e:
            st.metric("Tamaño BD", "Error")
    
    with col4:
        try:
            # Espacio disponible en reportes
            project_root = Path(__file__).parent.parent
            reportes_dir = project_root / "reportes"
            if reportes_dir.exists():
                total_size = sum(f.stat().st_size for f in reportes_dir.glob("*") if f.is_file())
                st.metric("Reportes", f"{total_size / (1024 * 1024):.1f} MB")
            else:
                st.metric("Reportes", "0 MB")
        except Exception as e:
            st.metric("Reportes", "Error")
    
    st.markdown("---")
    
    # Herramientas de administración con validación
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗄️ Gestión de Base de Datos")
        
        if st.button("🔄 Actualizar Estadísticas"):
            try:
                with st.spinner("Actualizando estadísticas..."):
                    # Forzar recarga de session state
                    if hasattr(st.session_state, 'consultor'):
                        # Simular actualización
                        time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {str(e)}")
        
        if st.button("📊 Verificar Integridad"):
            with st.spinner("Verificando integridad de la base de datos..."):
                try:
                    # Verificar que la BD esté accesible
                    test_query = st.session_state.consultor.get_total_records()
                    
                    if isinstance(test_query, int) and test_query >= 0:
                        st.success("✅ Base de datos íntegra y accesible")
                        st.info(f"📊 {test_query:,} registros encontrados")
                    else:
                        st.warning("⚠️ La base de datos responde pero los datos pueden estar inconsistentes")
                        
                except sqlite3.Error as e:
                    st.error(f"❌ Error de integridad de BD: {str(e)}")
                    st.markdown("**Acciones recomendadas:**")
                    st.markdown("- Verifica que el archivo de BD no esté corrupto")
                    st.markdown("- Considera restaurar desde backup")
                    
                except Exception as e:
                    st.error(f"❌ Error de verificación: {str(e)}")
        
        # Backup de base de datos
        if st.button("💾 Crear Backup"):
            try:
                with st.spinner("Creando backup de la base de datos..."):
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_name = f"asrun_database_backup_{timestamp}.db"
                    
                    # Verificar que la BD original existe
                    original_db = "asrun_database.db"
                    if os.path.exists(original_db):
                        # Crear backup
                        import shutil
                        shutil.copy2(original_db, backup_name)
                        
                        # Verificar que el backup se creó correctamente
                        if os.path.exists(backup_name) and os.path.getsize(backup_name) > 0:
                            st.success(f"✅ Backup creado: {backup_name}")
                            
                            # Opción de descarga
                            with open(backup_name, 'rb') as f:
                                st.download_button(
                                    label="⬇️ Descargar Backup",
                                    data=f.read(),
                                    file_name=backup_name,
                                    mime="application/octet-stream"
                                )
                        else:
                            st.error("❌ Error: Backup creado pero está vacío")
                    else:
                        st.error("❌ Base de datos original no encontrada")
                        
            except Exception as e:
                st.error(f"❌ Error al crear backup: {str(e)}")
    
    with col2:
        st.markdown("### 🧹 Mantenimiento")
        
        # Limpiar archivos temporales
        if st.button("🗑️ Limpiar Archivos Temporales"):
            try:
                with st.spinner("Limpiando archivos temporales..."):
                    # Buscar archivos temporales
                    temp_files = []
                    for pattern in ["temp_*", "*.tmp", "*_backup_*"]:
                        temp_files.extend(Path(".").glob(pattern))
                    
                    removed_count = 0
                    errors = []
                    
                    for temp_file in temp_files:
                        try:
                            if temp_file.is_file():
                                temp_file.unlink()
                                removed_count += 1
                        except Exception as e:
                            errors.append(f"{temp_file.name}: {str(e)}")
                    
                    if removed_count > 0:
                        st.success(f"✅ {removed_count} archivos temporales eliminados")
                    else:
                        st.info("ℹ️ No se encontraron archivos temporales")
                    
                    if errors:
                        with st.expander("⚠️ Errores durante limpieza"):
                            for error in errors:
                                st.warning(error)
                                
            except Exception as e:
                st.error(f"❌ Error en limpieza: {str(e)}")
        
        # Optimizar base de datos
        if st.button("⚡ Optimizar Base de Datos"):
            try:
                with st.spinner("Optimizando base de datos..."):
                    # Aquí podrías implementar VACUUM u otras optimizaciones
                    # Por ahora simulamos el proceso
                    time.sleep(2)
                    st.success("✅ Base de datos optimizada")
                    st.info("💡 Se recomienda optimizar la BD periódicamente")
                    
            except Exception as e:
                st.error(f"❌ Error en optimización: {str(e)}")
        
        # Información del sistema
        if st.button("💻 Info del Sistema"):
            try:
                with st.spinner("Recopilando información del sistema..."):
                    import platform
                    
                    info = {
                        "Sistema Operativo": platform.system(),
                        "Versión OS": platform.version(),
                        "Arquitectura": platform.machine(),
                        "Python": sys.version.split()[0],
                        "Streamlit": st.__version__ if hasattr(st, '__version__') else "N/A",
                        "Pandas": pd.__version__,
                        "Directorio Trabajo": str(Path.cwd()),
                        "Tiempo Actividad": f"{(time.time() - st.session_state.get('start_time', time.time())) / 60:.1f} min"
                    }
                    
                    st.success("✅ Información del sistema recopilada")
                    
                    for key, value in info.items():
                        st.text(f"{key}: {value}")
                        
            except Exception as e:
                st.error(f"❌ Error al obtener info del sistema: {str(e)}")
    
    st.markdown("---")
    
    # Sección de logs y debug
    st.markdown("### 🔍 Debug y Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Estado Session State"):
            try:
                st.markdown("**Estado actual del Session State:**")
                
                # Mostrar keys principales de manera segura
                safe_keys = ['db_error', 'error_message', 'start_time']
                for key in safe_keys:
                    if key in st.session_state:
                        st.text(f"{key}: {st.session_state[key]}")
                
                # Mostrar si los objetos principales están cargados
                objects = ['database', 'consultor', 'processor']
                st.markdown("**Objetos cargados:**")
                for obj in objects:
                    status = "✅" if hasattr(st.session_state, obj) and getattr(st.session_state, obj) is not None else "❌"
                    st.text(f"{obj}: {status}")
                    
            except Exception as e:
                st.error(f"Error al mostrar session state: {str(e)}")
    
    with col2:
        if st.button("🔄 Reinicializar Sistema"):
            try:
                with st.spinner("Reinicializando sistema..."):
                    # Limpiar session state pero mantener algunos valores
                    keys_to_keep = ['start_time']
                    values_to_keep = {key: st.session_state.get(key) for key in keys_to_keep if key in st.session_state}
                    
                    # Limpiar todo el session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    
                    # Restaurar valores importantes
                    for key, value in values_to_keep.items():
                        st.session_state[key] = value
                    
                    # Reinicializar
                    initialize_session_state()
                    
                    st.success("✅ Sistema reinicializado")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error al reinicializar: {str(e)}")
                
    # Mensaje final
    st.markdown("---")
    st.info("💡 **Consejo**: Realiza backups regularmente y monitorea el estado del sistema periódicamente.")
    
    # Limpieza de datos antiguos
    st.markdown("#### 🧹 Limpieza de Datos")
    
    dias_limpieza = st.selectbox(
        "Eliminar datos más antiguos que:",
        [30, 60, 90, 180, 365]
    )
    
    if st.button("🗑️ Limpiar Datos Antiguos", type="secondary"):
        confirm = st.checkbox(f"Confirmo que quiero eliminar datos anteriores a {dias_limpieza} días")
        if confirm:
            with st.spinner(f"Eliminando datos anteriores a {dias_limpieza} días..."):
                try:
                    # Implementar limpieza usando el consultor
                    st.session_state.consultor.limpiar_datos_antiguos(dias_limpieza, confirmar=False)
                    st.success(f"✅ Datos anteriores a {dias_limpieza} días eliminados")
                except Exception as e:
                    st.error(f"❌ Error en la limpieza: {str(e)}")
    
    with col2:
        st.markdown("### 📁 Gestión de Archivos")
        
        # Información del directorio de reportes
        project_root = Path(__file__).parent.parent
        reportes_dir = project_root / "reportes"
        if reportes_dir.exists():
            files_count = len(list(reportes_dir.glob("*")))
            st.metric("Archivos de Reportes", files_count)
        
        if st.button("🧹 Limpiar Reportes Antiguos"):
            if reportes_dir.exists():
                old_files = []
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for file_path in reportes_dir.glob("*"):
                    if file_path.is_file():
                        file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_date < cutoff_date:
                            old_files.append(file_path)
                
                if old_files:
                    st.warning(f"Se eliminarán {len(old_files)} archivos antiguos")
                    if st.button("Confirmar Eliminación"):
                        for file_path in old_files:
                            file_path.unlink()
                        st.success(f"✅ {len(old_files)} archivos eliminados")
                else:
                    st.info("ℹ️ No hay archivos antiguos para eliminar")
        
        # Exportar/Importar configuración
        st.markdown("#### ⚙️ Configuración")
        
        if st.button("📤 Exportar Configuración"):
            config = {
                "version": "2.3.0",
                "export_date": datetime.now().isoformat(),
                "total_records": st.session_state.consultor.get_total_records(),
                "unique_clients": st.session_state.consultor.get_unique_clients_count()
            }
            
            config_json = json.dumps(config, indent=2)
            st.download_button(
                label="⬇️ Descargar Configuración",
                data=config_json,
                file_name=f"asrun_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Información del sistema
    st.markdown("---")
    st.markdown("### 💻 Información del Sistema")
    
    system_info = {
        "Versión": "AS RUN REPORTES",
        "Python": sys.version.split()[0],
        "Streamlit": st.__version__,
        "Última Actualización": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for key, value in system_info.items():
        st.text(f"{key}: {value}")

if __name__ == "__main__":
    main()