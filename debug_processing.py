#!/usr/bin/env python3
"""
Script de depuración para entender el problema con la columna STATUS
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from procesar_asrun import procesar_archivo_txt
from database_manager import AsRunDatabase
import pandas as pd
from pathlib import Path

def debug_processing():
    """Depurar el procesamiento de archivos"""
    print("🔍 DEPURACIÓN DEL PROCESAMIENTO")
    print("=" * 50)
    
    # Usar un archivo que sabemos que tiene Lost XPoint Path
    archivo_test = Path("data/Tx List-Marina Text 20250528_055959 Marina.txt")
    
    if not archivo_test.exists():
        print(f"❌ Archivo no encontrado: {archivo_test}")
        return
    
    print(f"📁 Procesando archivo de prueba: {archivo_test.name}")
    
    # Procesar el archivo
    df_resultado = procesar_archivo_txt(archivo_test)
    
    if df_resultado.empty:
        print("❌ No se obtuvieron datos del procesamiento")
        return
    
    print(f"✅ Datos procesados: {len(df_resultado)} registros")
    print(f"📊 Columnas del DataFrame: {list(df_resultado.columns)}")
    
    # Verificar si hay columna STATUS
    if 'STATUS' in df_resultado.columns:
        print("\n📊 Análisis de la columna STATUS:")
        status_counts = df_resultado['STATUS'].value_counts()
        for status, count in status_counts.items():
            print(f"   • {status}: {count} registros")
        
        # Mostrar algunos ejemplos de Lost XPoint Path
        lost_xpoint_records = df_resultado[df_resultado['STATUS'] == 'Lost XPoint Path']
        if not lost_xpoint_records.empty:
            print(f"\n🔍 Ejemplos de registros Lost XPoint Path ({len(lost_xpoint_records)} total):")
            for i, (_, row) in enumerate(lost_xpoint_records.head(3).iterrows()):
                print(f"   {i+1}. {row['DIA_EMISION']} {row['DATETIME'].time()} - {row['TITLE']}")
        else:
            print("   ⚠️  No se encontraron registros Lost XPoint Path en el DataFrame procesado")
    else:
        print("❌ La columna STATUS no está presente en el DataFrame")
    
    # Intentar insertar en la base de datos para ver el error exacto
    print(f"\n💾 Intentando insertar en la base de datos...")
    
    try:
        db = AsRunDatabase("src/asrun_database.db")
        
        # Mostrar estructura de la tabla
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA table_info(emisiones)')
            columns_info = cursor.fetchall()
            print("📋 Estructura de la tabla emisiones:")
            for col_info in columns_info:
                print(f"   • {col_info[1]} ({col_info[2]})")
        
        # Intentar insertar un registro pequeño
        test_df = df_resultado.head(1)
        print(f"\n🧪 Insertando registro de prueba...")
        print(f"   Columnas del DataFrame: {list(test_df.columns)}")
        
        insertados, duplicados = db.insertar_emisiones(test_df, "test_debug.txt")
        print(f"   ✅ Inserción exitosa: {insertados} insertados, {duplicados} duplicados")
        
    except Exception as e:
        print(f"   ❌ Error en inserción: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_processing()
