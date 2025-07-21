#!/usr/bin/env python3
"""
Gestor de base de datos SQLite para reportes AsRun
Almacena y consulta datos de emisiones publicitarias
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import json
import re


class ClienteNormalizer:
    """Normalizador de nombres de clientes basado en patrones"""
    
    def __init__(self):
        """Inicializar mapeo de clientes"""
        # Mapeo completo de títulos exactos a nombres de clientes normalizados
        self.CLIENTE_MAPPING = {
            # AHK CHILE (1 títulos)
            'TI AHK CHILE PREMIOS': 'AHK CHILE',
            # ASEO ALONDRA (1 títulos)
            'TI ASEO ALONDRA': 'ASEO ALONDRA',
            # ATL (1 títulos)
            'ATL_LU_MPARTNER_14_17_MAY': 'ATL',
            # ATLAS (3 títulos)
            'ABRE TEPILLE_ATLAS_AG_ECON PM': 'ATLAS',
            'ATLAS CORPORATIVO': 'ATLAS',
            'CIERRE TEPILLE_ATLAS_AG_AG_ECON': 'ATLAS',
            # BHP (4 títulos)
            'BHP DESALINATIOV V2_445994': 'BHP',
            'BHP MANIFESTO 441720': 'BHP',
            'CONTINUIDAD BHP RADIO': 'BHP',
            'CONTINUIDAD BHPV2_RADIO': 'BHP',
            # BMW (1 títulos)
            'BMW TACTICA MAYO SERIE_1': 'BMW',
            # CANNON (1 títulos)
            'CANNON HOME ATELIER': 'CANNON',
            # CAP (1 títulos)
            'CAP 1 CLC ALEMANA': 'CAP',
            # CNN (1 títulos)
            'CONTINUIDAD CNN PRIME': 'CNN',
            # CONSORCIO (16 títulos)
            'ABRE CONSORCIO _CNN PRIME': 'CONSORCIO',
            'ABRE CONSORCIO_HOY ES NOTICIA': 'CONSORCIO',
            'ABRE CONS_MOV_PRIME': 'CONSORCIO',
            'A_CONS_URBANACONCEPTO_445908': 'CONSORCIO',
            'B_CONS_OUTDOORASISTENCIA_445909': 'CONSORCIO',
            'CIERRE CONSORCIO_HOY ES NOTICIA': 'CONSORCIO',
            'CIERRE CONSORSIO_CNN PRIME': 'CONSORCIO',
            'CIERRE CONS_MOV_PRIME': 'CONSORCIO',
            'CONTINUIDAD CONSORCIO HESN': 'CONSORCIO',
            'CONTINUIDAD CONSORCIO PRIME': 'CONSORCIO',
            'D_CONS_SURFERASISTENCIARUTA_4459': 'CONSORCIO',
            'E2CONS_SURFER_446326_EL_EX': 'CONSORCIO',
            'E3CONS_OUTDOOR_446325_EL_EX': 'CONSORCIO',
            'F_CONS_OUTDOORCONCEPTO_499506': 'CONSORCIO',
            'G_CONS_URBANAREVTECNICA _445911': 'CONSORCIO',
            'H_CONS_SURFERCONCEPTO_44907': 'CONSORCIO',
            # CYNERSIS (2 títulos)
            'CYNERSIS GENERICO NOV': 'CYNERSIS',
            'CYNERSIS ZOOM V3 OCT.': 'CYNERSIS',
            # ENTEL (1 títulos)
            'TI ENTEL DIGITAL': 'ENTEL',
            # GASCO (7 títulos)
            'ABRE_ GASCO_ MINERIA 360': 'GASCO',
            'ABRE_GASCO_AGENDA ECO_AM': 'GASCO',
            'ABRE_GASCO_MINERIA_AGENDA_AM': 'GASCO',
            'CIERRE_ GASCO_ MINERIA 360': 'GASCO',
            'CIERRE_GASCO_AGENDA ECO_AM': 'GASCO',
            'CONTINUIDAD GASCO MINERIA': 'GASCO',
            'GASCO MINERIA_INERSA': 'GASCO',
            # HOY (1 títulos)
            'CONTINUIDAD HOY ES NOTICIA': 'HOY',
            # KIPUS (1 títulos)
            'TI KIPUS': 'KIPUS',
            # LABORATORIO (1 títulos)
            'TI_LAB_BARNAFI_KRAUSE_V2': 'LABORATORIO',
            # MARLEY (14 títulos)
            'ABRE BHP-MARLEY RADIO': 'MARLEY',
            'ABRE BHPV2-MARLEY RADIO': 'MARLEY',
            'ABRE DEPORTES MARLEY_SKECHERS': 'MARLEY',
            'ABRE MARLEY CNN TARDE': 'MARLEY',
            'ABRE MARLEY T0': 'MARLEY',
            'ABRE MARLEY U MIRADA': 'MARLEY',
            'ABRE UM MARLEY _CONSORCIO': 'MARLEY',
            'CIERRE BHP-MARLEY RADIO': 'MARLEY',
            'CIERRE BHPV2-MARLEY RADIO': 'MARLEY',
            'CIERRE DEPORTES MARLEY_SKECHERS': 'MARLEY',
            'CIERRE MARLEY CNN TARDE': 'MARLEY',
            'CIERRE MARLEY T0': 'MARLEY',
            'CIERRE MARLEY U MIRADA': 'MARLEY',
            'CIERRE UM MARLEY _CONSORCIO': 'MARLEY',
            # MINERIA (4 títulos)
            'ABRE MINERIA': 'MINERIA',
            'CIERRE MINERIA': 'MINERIA',
            'CONTINUIDAD MINERIA 360': 'MINERIA',
            'SPOT MINERIA': 'MINERIA',
            # MIRA (10 títulos)
            'CLC MIRA DR CASTILLO': 'MIRA',
            'CLC MIRA DR FRANCA': 'MIRA',
            'CLC MIRA DR FUENTES': 'MIRA',
            'CLC MIRA DR LOPEZ': 'MIRA',
            'CLC MIRA DR PEREZ': 'MIRA',
            'CLC MIRA DR RODRIGUEZ': 'MIRA',
            'CLC MIRA DRA ESPINOSA': 'MIRA',
            'CLC MIRA DRA KATZ': 'MIRA',
            'CLC MIRA DRA SUAREZ': 'MIRA',
            'CLINICA MIRA 2025': 'MIRA',
            # MOVISTAR (6 títulos)
            'ABRE MOV': 'MOVISTAR',
            'CIERRE MOV': 'MOVISTAR',
            'CONTINUIDAD MOVISTAR PRIME': 'MOVISTAR',
            'MOV': 'MOVISTAR',
            'MOVISTAR FIBRA_E_910147_22S': 'MOVISTAR',
            'MOVISTAR FIBRA_E_910153_40S': 'MOVISTAR',
            # SINGULARITY (1 títulos)
            'SINGULARITY_MPARTNER_04JUN': 'SINGULARITY',
            # SKECHERS (3 títulos)
            'ABRE SKECHERS': 'SKECHERS',
            'CIERRE SKECHERS': 'SKECHERS',
            'SKECHERS FUTBOL': 'SKECHERS',
            # TCL (1 títulos)
            'TI_TCL_TELEVISORES': 'TCL',
            # TE PILLE (4 títulos)
            'ABRE TE PILLE AGENDA ECON AM': 'TE PILLE',
            'CIERRE TE PILLE AGENDA EC AM': 'TE PILLE',
            'TE PILLE CARLOS_EMILIO_1': 'TE PILLE',
            'TE PILLE EMILIO_PANCHO_911': 'TE PILLE',
        }
        
        # Mapeo de palabras clave para casos no exactos (fallback)
        self.CLIENTE_KEYWORDS = {
            'GASCO': 'GASCO',
            'MARLEY': 'MARLEY', 
            'ATLAS': 'ATLAS',
            'ATL': 'ATL',  # ATL se mapea a ATL (separado de ATLAS)
            'BHP': 'BHP',
            'BMW': 'BMW',
            'CANNON': 'CANNON',
            'MIRA': 'MIRA',
            'CONSORCIO': 'CONSORCIO',
            'CONS': 'CONSORCIO',  # CONS se mapea a CONSORCIO
            'CYNERSIS': 'CYNERSIS',
            'MOVISTAR': 'MOVISTAR',
            'MOV': 'MOVISTAR',  # MOV se mapea a MOVISTAR
            'SINGULARITY': 'SINGULARITY',
            'SKECHERS': 'SKECHERS',
            'TE PILLE': 'TE PILLE',
            'PILLE': 'TE PILLE',  # PILLE se mapea a TE PILLE
            'ENTEL': 'ENTEL',
            'AHK': 'AHK CHILE',
            'ASEO': 'ASEO ALONDRA',
            'CAP': 'CAP',
            'CNN': 'CNN',
            'HOY': 'HOY',
            'KIPUS': 'KIPUS',
            'LAB': 'LABORATORIO',
            'LABORATORIO': 'LABORATORIO',
            'MINERIA': 'MINERIA',
            'TCL': 'TCL'
        }
        
        # Patrones de prefijos y sufijos a ignorar en la búsqueda
        self.PREFIJOS_IGNORAR = ['ABRE_', 'ABRE ', 'CIERRE_', 'CIERRE ', 'CONTINUIDAD ', 'CLC ']
        self.SUFIJOS_IGNORAR = ['_AM', '_PM', '_RADIO', '_AGENDA', '_ECO', '_ECON', '_CNN', '_TARDE', 
                               '_T0', '_MIRADA', '_DEPORTES', '_FUTBOL', '_CORPORATIVO', '_HOME', 
                               '_ATELIER', '_GENERICO', '_NOV', '_MAYO', '_SERIE', '_TACTICA']
    
    def normalizar_cliente(self, titulo):
        """
        Normaliza el nombre del cliente basándose en el título del comercial
        
        Args:
            titulo (str): Título del comercial
            
        Returns:
            str: Nombre del cliente normalizado
        """
        if not titulo:
            return "CLIENTE_DESCONOCIDO"
        
        # 1. Buscar coincidencias exactas primero (mapeo completo)
        titulo_upper = titulo.upper().strip()
        if titulo_upper in self.CLIENTE_MAPPING:
            return self.CLIENTE_MAPPING[titulo_upper]
        
        # 2. Buscar por palabras clave (fallback)
        for palabra_clave, cliente_norm in self.CLIENTE_KEYWORDS.items():
            if palabra_clave in titulo_upper:
                return cliente_norm
        
        # 3. Si no encuentra coincidencia, intentar extraer el cliente principal
        # removiendo prefijos y sufijos comunes
        titulo_limpio = titulo_upper
        
        # Remover prefijos
        for prefijo in self.PREFIJOS_IGNORAR:
            if titulo_limpio.startswith(prefijo):
                titulo_limpio = titulo_limpio[len(prefijo):]
                break
        
        # Extraer la primera palabra significativa
        palabras = titulo_limpio.split('_')
        if palabras:
            primera_palabra = palabras[0].strip()
            
            # Buscar si la primera palabra coincide con algún cliente conocido
            if primera_palabra in self.CLIENTE_KEYWORDS:
                return self.CLIENTE_KEYWORDS[primera_palabra]
                
            # Si no encuentra coincidencia, devolver la primera palabra como cliente
            return primera_palabra if primera_palabra else "CLIENTE_DESCONOCIDO"
        
        return "CLIENTE_DESCONOCIDO"
    
    def obtener_estadisticas_normalizacion(self, titulos_list):
        """
        Obtiene estadísticas de normalización para una lista de títulos
        
        Args:
            titulos_list (list): Lista de títulos de comerciales
            
        Returns:
            dict: Estadísticas de normalización
        """
        resultados = {}
        clientes_normalizados = {}
        
        for titulo in titulos_list:
            cliente_norm = self.normalizar_cliente(titulo)
            
            if cliente_norm not in clientes_normalizados:
                clientes_normalizados[cliente_norm] = []
            
            clientes_normalizados[cliente_norm].append(titulo)
        
        return {
            'total_titulos': len(titulos_list),
            'clientes_unicos': len(clientes_normalizados),
            'mapeo_cliente_titulos': clientes_normalizados,
            'clientes_encontrados': list(clientes_normalizados.keys())
        }


class AsRunDatabase:
    """Gestor de base de datos para reportes AsRun"""
    
    def __init__(self, db_path=None):
        """Inicializar conexión a la base de datos"""
        if db_path is None:
            # Usar SIEMPRE la base de datos principal en el directorio raíz del proyecto
            current_dir = Path(__file__).parent
            # Prioridad única: BD principal en directorio padre (raíz del proyecto)
            db_path = str(current_dir.parent / "asrun_database.db")
        
        self.db_path = db_path
        self.normalizer = ClienteNormalizer()  # Inicializar normalizador
        self.init_database()
    
    def init_database(self):
        """Crear tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            # Tabla para almacenar emisiones individuales
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emisiones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_procesamiento DATE NOT NULL,
                    dia_emision DATE NOT NULL,
                    hora_emision TIME NOT NULL,
                    datetime_emision DATETIME NOT NULL,
                    cliente TEXT NOT NULL,
                    media_id TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    duracion TEXT NOT NULL,
                    archivo_origen TEXT NOT NULL,
                    status TEXT DEFAULT 'Completed',
                    event TEXT DEFAULT 'Media Event',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(dia_emision, hora_emision, media_id, cliente)
                )
            """)
            
            # Agregar columna status si no existe (para BDs existentes)
            try:
                conn.execute("ALTER TABLE emisiones ADD COLUMN status TEXT DEFAULT 'Completed'")
            except sqlite3.OperationalError:
                # La columna ya existe
                pass
            
            # Agregar columna event si no existe (para BDs existentes)
            try:
                conn.execute("ALTER TABLE emisiones ADD COLUMN event TEXT DEFAULT 'Media Event'")
                # Actualizar registros existentes con event = 'Media Event' donde media_id empiece con 'COM'
                conn.execute("UPDATE emisiones SET event = 'Media Event' WHERE media_id LIKE 'COM%' AND event IS NULL")
                conn.commit()
            except sqlite3.OperationalError:
                # La columna ya existe
                pass
            
            # Tabla para almacenar reportes generados
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reportes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_archivo TEXT NOT NULL UNIQUE,
                    fecha_generacion DATETIME NOT NULL,
                    total_emisiones INTEGER NOT NULL,
                    dias_incluidos TEXT NOT NULL,
                    clientes_incluidos TEXT NOT NULL,
                    ruta_archivo TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para mejorar consultas
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dia_emision ON emisiones(dia_emision)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cliente ON emisiones(cliente)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_media_id ON emisiones(media_id)")
            
            conn.commit()
    
    def insertar_emisiones(self, df_emisiones, archivo_origen):
        """Insertar emisiones desde un DataFrame (previene duplicados automáticamente)"""
        insertados = 0
        duplicados = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for _, fila in df_emisiones.iterrows():
                try:
                    cursor = conn.execute("""
                        INSERT OR IGNORE INTO emisiones (
                            fecha_procesamiento, dia_emision, hora_emision, 
                            datetime_emision, cliente, media_id, titulo, 
                            duracion, archivo_origen, status, event
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date.today().isoformat(),
                        fila['DIA_EMISION'].isoformat(),
                        fila['DATETIME'].time().isoformat(),
                        fila['DATETIME'].isoformat(),
                        fila['MARCA'],
                        fila['MEDIA_ID'],
                        fila['TITLE'],
                        str(fila['DURATION']),
                        archivo_origen,
                        fila.get('STATUS', 'Completed'),  # Usar STATUS si existe, sino 'Completed'
                        fila.get('EVENT', 'Media Event')  # Usar EVENT si existe, sino 'Media Event'
                    ))
                    if cursor.rowcount > 0:
                        insertados += 1
                    else:
                        duplicados += 1
                except sqlite3.IntegrityError:
                    # Duplicado detectado por constraint único
                    duplicados += 1
            
            conn.commit()
        
        if duplicados > 0:
            print(f"   💾 Guardados: {insertados} nuevos registros")
            print(f"   🔄 Omitidos: {duplicados} duplicados detectados")
        else:
            print(f"   💾 Guardados: {insertados} registros")
        
        return insertados, duplicados
    
    def insertar_reporte(self, nombre_archivo, total_emisiones, ruta_archivo, df_consolidado):
        """Insertar información de un reporte generado"""
        dias_incluidos = sorted(df_consolidado['DIA_EMISION'].unique())
        clientes_incluidos = sorted(df_consolidado['MARCA'].unique())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO reportes (
                    nombre_archivo, fecha_generacion, total_emisiones, 
                    dias_incluidos, clientes_incluidos, ruta_archivo
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nombre_archivo,
                datetime.now(),
                total_emisiones,
                json.dumps([str(d) for d in dias_incluidos]),
                json.dumps(clientes_incluidos),
                str(ruta_archivo)
            ))
            conn.commit()
    
    def consultar_emisiones_por_cliente(self, cliente, fecha_inicio=None, fecha_fin=None):
        """Consultar emisiones Media Events comerciales por cliente en un rango de fechas"""
        # Filtrar solo Media Events con Media IDs que empiecen con COM
        query = """SELECT * FROM emisiones 
                   WHERE cliente = ? 
                   AND event = 'Media Event' 
                   AND media_id LIKE 'COM%'"""
        params = [cliente]
        
        if fecha_inicio:
            query += " AND dia_emision >= ?"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND dia_emision <= ?"
            params.append(fecha_fin)
        
        query += " ORDER BY datetime_emision"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def consultar_emisiones_por_dia(self, dia_emision):
        """Consultar todas las emisiones de un día específico"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                "SELECT * FROM emisiones WHERE dia_emision = ? ORDER BY hora_emision",
                conn, params=[dia_emision]
            )
    
    def obtener_resumen_por_cliente(self, fecha_inicio=None, fecha_fin=None):
        """Obtener resumen de emisiones agrupadas por cliente"""
        query = """
            SELECT 
                cliente,
                COUNT(*) as total_emisiones,
                COUNT(DISTINCT dia_emision) as dias_activos,
                MIN(dia_emision) as primera_emision,
                MAX(dia_emision) as ultima_emision
            FROM emisiones
        """
        params = []
        
        if fecha_inicio or fecha_fin:
            query += " WHERE "
            conditions = []
            
            if fecha_inicio:
                conditions.append("dia_emision >= ?")
                params.append(fecha_inicio)
            
            if fecha_fin:
                conditions.append("dia_emision <= ?")
                params.append(fecha_fin)
            
            query += " AND ".join(conditions)
        
        query += " GROUP BY cliente ORDER BY total_emisiones DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def obtener_reportes_generados(self):
        """Obtener lista de reportes generados"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                "SELECT * FROM reportes ORDER BY fecha_generacion DESC",
                conn
            )
    
    def limpiar_datos_antiguos(self, dias_antiguedad=90):
        """Limpiar datos más antiguos que X días"""
        fecha_limite = date.today() - pd.Timedelta(days=dias_antiguedad)
        
        with sqlite3.connect(self.db_path) as conn:
            # Eliminar emisiones antiguas
            cursor = conn.execute(
                "DELETE FROM emisiones WHERE dia_emision < ?", 
                [fecha_limite]
            )
            emisiones_eliminadas = cursor.rowcount
            
            # Eliminar reportes antiguos
            cursor = conn.execute(
                "DELETE FROM reportes WHERE fecha_generacion < ?", 
                [fecha_limite]
            )
            reportes_eliminados = cursor.rowcount
            
            conn.commit()
            
            return emisiones_eliminadas, reportes_eliminados
    
    def obtener_estadisticas_generales(self):
        """Obtener estadísticas generales de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total de emisiones
            stats['total_emisiones'] = conn.execute(
                "SELECT COUNT(*) FROM emisiones"
            ).fetchone()[0]
            
            # Total de clientes únicos
            stats['total_clientes'] = conn.execute(
                "SELECT COUNT(DISTINCT cliente) FROM emisiones"
            ).fetchone()[0]
            
            # Rango de fechas
            fecha_range = conn.execute(
                "SELECT MIN(dia_emision), MAX(dia_emision) FROM emisiones"
            ).fetchone()
            
            stats['fecha_inicio'] = fecha_range[0]
            stats['fecha_fin'] = fecha_range[1]
            
            # Total de reportes
            stats['total_reportes'] = conn.execute(
                "SELECT COUNT(*) FROM reportes"
            ).fetchone()[0]
            
            return stats
        
    def obtener_emisiones_cliente(self, cliente, fecha_inicio=None, fecha_fin=None):
        """Obtener emisiones de un cliente específico (alias para consultar_emisiones_por_cliente)"""
        return self.consultar_emisiones_por_cliente(cliente, fecha_inicio, fecha_fin)
    
    def obtener_emisiones_por_fecha(self, fecha_inicio=None, fecha_fin=None):
        """Obtener todas las emisiones Media Events comerciales en un rango de fechas"""
        # Filtrar solo Media Events con Media IDs que empiecen con COM
        query = """SELECT * FROM emisiones 
                   WHERE event = 'Media Event' 
                   AND media_id LIKE 'COM%'"""
        params = []
        
        if fecha_inicio or fecha_fin:
            conditions = []
            
            if fecha_inicio:
                conditions.append("dia_emision >= ?")
                params.append(fecha_inicio)
            
            if fecha_fin:
                conditions.append("dia_emision <= ?")
                params.append(fecha_fin)
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY datetime_emision"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecutar consulta SQL y retornar resultados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

def main():
    """Función de prueba"""
    db = AsRunDatabase("test_database.db")
    
    print("🗄️  BASE DE DATOS ASRUN INICIALIZADA")
    print("=" * 40)
    
    # Mostrar estadísticas
    stats = db.obtener_estadisticas_generales()
    print(f"📊 Total emisiones: {stats['total_emisiones']}")
    print(f"👥 Total clientes: {stats['total_clientes']}")
    print(f"📅 Rango fechas: {stats['fecha_inicio']} - {stats['fecha_fin']}")
    print(f"📄 Total reportes: {stats['total_reportes']}")


if __name__ == "__main__":
    main()
