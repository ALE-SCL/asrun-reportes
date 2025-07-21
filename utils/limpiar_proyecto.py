#!/usr/bin/env python3
"""
Script de limpieza automatizada para el proyecto AsRun Report
Elimina archivos temporales, caché y backups antiguos
"""

import os
import glob
import shutil
from datetime import datetime, timedelta

def limpiar_cache():
    """Eliminar caché de Python"""
    print("🧹 Limpiando caché de Python...")
    
    # Eliminar __pycache__ en src/
    cache_dir = "src/__pycache__"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"   ✅ Eliminado: {cache_dir}")
    
    # Eliminar archivos .pyc
    pyc_files = glob.glob("**/*.pyc", recursive=True)
    for file in pyc_files:
        os.remove(file)
        print(f"   ✅ Eliminado: {file}")

def limpiar_archivos_sistema():
    """Eliminar archivos del sistema como .DS_Store"""
    print("🧹 Limpiando archivos del sistema...")
    
    ds_store_files = glob.glob("**/.DS_Store", recursive=True)
    for file in ds_store_files:
        os.remove(file)
        print(f"   ✅ Eliminado: {file}")

def limpiar_temporales():
    """Eliminar archivos temporales de prueba"""
    print("🧹 Limpiando archivos temporales...")
    
    # Patrones de archivos temporales
    patrones = [
        "test_*.py",
        "prueba_*.py", 
        "temp_*.py",
        "migrar_*.py",
        "*.tmp",
        "*.bak",
        "*~"
    ]
    
    for patron in patrones:
        archivos = glob.glob(patron)
        for archivo in archivos:
            os.remove(archivo)
            print(f"   ✅ Eliminado: {archivo}")

def limpiar_backups_antiguos(dias=30):
    """Eliminar backups de base de datos más antiguos de X días"""
    print(f"🧹 Limpiando backups antiguos (>{dias} días)...")
    
    backups = glob.glob("asrun_database_backup_*.db")
    fecha_limite = datetime.now() - timedelta(days=dias)
    
    for backup in backups:
        stat = os.stat(backup)
        fecha_archivo = datetime.fromtimestamp(stat.st_mtime)
        
        if fecha_archivo < fecha_limite:
            os.remove(backup)
            print(f"   ✅ Eliminado backup antiguo: {backup}")
        else:
            print(f"   ⏳ Mantenido backup reciente: {backup}")

def mostrar_estadisticas():
    """Mostrar estadísticas del proyecto después de la limpieza"""
    print("\n📊 ESTADÍSTICAS DEL PROYECTO")
    print("=" * 30)
    
    # Contar archivos por tipo
    archivos_python = len(glob.glob("src/*.py"))
    archivos_data = len(glob.glob("data/*.txt"))
    archivos_reportes = len(glob.glob("reportes/*.txt"))
    archivos_docs = len(glob.glob("*.md"))
    
    print(f"📁 Scripts Python: {archivos_python}")
    print(f"📁 Archivos de datos: {archivos_data}")  
    print(f"📁 Reportes generados: {archivos_reportes}")
    print(f"📁 Documentación: {archivos_docs}")
    
    # Tamaño de la base de datos
    if os.path.exists("asrun_database.db"):
        size_mb = os.path.getsize("asrun_database.db") / (1024*1024)
        print(f"💾 Base de datos: {size_mb:.1f} MB")

if __name__ == "__main__":
    print("🚀 LIMPIEZA AUTOMATIZADA DEL PROYECTO AsRun Report")
    print("=" * 50)
    
    try:
        limpiar_cache()
        limpiar_archivos_sistema()
        limpiar_temporales()
        limpiar_backups_antiguos(30)  # Mantener backups de último mes
        mostrar_estadisticas()
        
        print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
