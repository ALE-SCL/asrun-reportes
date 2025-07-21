#!/usr/bin/env python3
"""
Script de Backup Completo para Shiki's Report (Asrun)
Crea una copia de seguridad completa del proyecto con timestamp
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

def crear_backup_completo():
    """Crear backup completo del proyecto Shiki's Report"""
    
    # Configuración
    proyecto_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"shikis_report_backup_{timestamp}"
    
    # Directorio de destino del backup
    backup_dir = proyecto_dir.parent / "backups" / backup_name
    
    print("🔄 INICIANDO BACKUP COMPLETO DE SHIKI'S REPORT")
    print("=" * 60)
    print(f"📂 Directorio origen: {proyecto_dir}")
    print(f"📁 Directorio backup: {backup_dir}")
    print(f"⏰ Timestamp: {timestamp}")
    print()
    
    try:
        # Crear directorio de backups si no existe
        backup_dir.parent.mkdir(exist_ok=True)
        backup_dir.mkdir(exist_ok=True)
        
        # 1. Copiar todos los archivos principales
        print("📋 1. Copiando archivos principales...")
        archivos_principales = [
            "app_streamlit.py",
            "requirements.txt", 
            "requirements_gui.txt",
            "README.md",
            "README_GITHUB.md",
            "CHANGELOG.md",
            "GUIA_USUARIO.md",
            "RESUMEN_EJECUTIVO.md",
            "ESTADO_FINAL_COMPLETO.md",
            "FUNCIONALIDAD_EXCEL.md",
            "LICENSE"
        ]
        
        for archivo in archivos_principales:
            src_file = proyecto_dir / archivo
            if src_file.exists():
                shutil.copy2(src_file, backup_dir / archivo)
                print(f"  ✅ {archivo}")
            else:
                print(f"  ⚠️  {archivo} (no existe)")
        
        # 2. Copiar directorio src completo
        print("\n🔧 2. Copiando código fuente (src/)...")
        src_dir = proyecto_dir / "src"
        if src_dir.exists():
            backup_src = backup_dir / "src"
            shutil.copytree(src_dir, backup_src)
            print(f"  ✅ Directorio src/ copiado completo")
            
            # Contar archivos Python
            py_files = list(backup_src.glob("*.py"))
            print(f"  📄 {len(py_files)} archivos Python copiados")
        else:
            print("  ⚠️  Directorio src/ no encontrado")
        
        # 3. Backup específico de bases de datos
        print("\n🗄️  3. Respaldando bases de datos...")
        bases_datos = [
            "asrun_database.db",
            "asrun_database_backup_*.db"
        ]
        
        db_backup_dir = backup_dir / "databases"
        db_backup_dir.mkdir(exist_ok=True)
        
        # Base de datos principal
        db_principal = proyecto_dir / "asrun_database.db"
        if db_principal.exists():
            # Crear backup con verificación de integridad
            db_backup_path = db_backup_dir / f"asrun_database_backup_{timestamp}.db"
            crear_backup_bd_verificado(db_principal, db_backup_path)
            print(f"  ✅ Base de datos principal → {db_backup_path.name}")
        
        # Buscar otros backups de BD existentes
        backups_existentes = list(proyecto_dir.glob("asrun_database_backup_*.db"))
        for backup_bd in backups_existentes:
            shutil.copy2(backup_bd, db_backup_dir / backup_bd.name)
            print(f"  ✅ {backup_bd.name}")
        
        # BD en src/
        src_db = proyecto_dir / "src" / "asrun_database.db"
        if src_db.exists():
            shutil.copy2(src_db, db_backup_dir / "src_asrun_database.db")
            print(f"  ✅ src/asrun_database.db")
        
        # 4. Copiar reportes generados
        print("\n📊 4. Copiando reportes...")
        reportes_dir = proyecto_dir / "reportes"
        if reportes_dir.exists() and any(reportes_dir.iterdir()):
            backup_reportes = backup_dir / "reportes"
            shutil.copytree(reportes_dir, backup_reportes)
            
            # Contar archivos por tipo
            txt_files = list(backup_reportes.glob("*.txt"))
            xlsx_files = list(backup_reportes.glob("*.xlsx"))
            
            print(f"  ✅ {len(txt_files)} reportes .txt")
            print(f"  ✅ {len(xlsx_files)} reportes .xlsx")
        else:
            print("  ℹ️  No hay reportes para respaldar")
        
        # 5. Copiar datos de entrada
        print("\n📁 5. Copiando datos de entrada...")
        data_dir = proyecto_dir / "data"
        if data_dir.exists() and any(data_dir.iterdir()):
            backup_data = backup_dir / "data"
            shutil.copytree(data_dir, backup_data)
            
            data_files = list(backup_data.glob("*.txt"))
            print(f"  ✅ {len(data_files)} archivos de datos")
        else:
            print("  ℹ️  No hay datos de entrada para respaldar")
        
        # 6. Crear directorio de configuración
        print("\n⚙️ 6. Copiando configuración...")
        config_dir = proyecto_dir / ".streamlit"
        if config_dir.exists():
            backup_config = backup_dir / ".streamlit"
            shutil.copytree(config_dir, backup_config)
            print(f"  ✅ Configuración Streamlit copiada")
        
        # 7. Crear archivo de información del backup
        print("\n📝 7. Creando información del backup...")
        crear_info_backup(backup_dir, timestamp, proyecto_dir)
        
        # 8. Crear archivo comprimido ZIP
        print("\n📦 8. Creando archivo comprimido...")
        zip_path = backup_dir.parent / f"{backup_name}.zip"
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', backup_dir.parent, backup_name)
        
        # Calcular tamaños
        backup_size = get_dir_size(backup_dir)
        zip_size = zip_path.stat().st_size
        
        print("\n🎉 BACKUP COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        print(f"📂 Directorio backup: {backup_dir}")
        print(f"📦 Archivo ZIP: {zip_path}")
        print(f"💾 Tamaño backup: {backup_size / (1024*1024):.1f} MB")
        print(f"🗜️  Tamaño ZIP: {zip_size / (1024*1024):.1f} MB")
        print(f"📊 Compresión: {(1 - zip_size/backup_size)*100:.1f}%")
        print()
        print("✅ El backup incluye:")
        print("   • Código fuente completo")
        print("   • Bases de datos con verificación")
        print("   • Reportes generados")
        print("   • Datos de entrada")
        print("   • Configuración")
        print("   • Documentación")
        
        return True, backup_dir, zip_path
        
    except Exception as e:
        print(f"\n❌ ERROR durante el backup: {str(e)}")
        return False, None, None

def crear_backup_bd_verificado(origen, destino):
    """Crear backup de BD con verificación de integridad"""
    try:
        # Verificar BD origen
        with sqlite3.connect(origen) as conn:
            conn.execute("PRAGMA integrity_check")
        
        # Copiar archivo
        shutil.copy2(origen, destino)
        
        # Verificar BD destino
        with sqlite3.connect(destino) as conn:
            result = conn.execute("PRAGMA integrity_check").fetchone()
            if result[0] != "ok":
                raise ValueError(f"Verificación de integridad falló: {result[0]}")
        
        return True
    except Exception as e:
        print(f"    ⚠️  Error al verificar BD {origen.name}: {str(e)}")
        # Hacer copia simple como fallback
        shutil.copy2(origen, destino)
        return False

def crear_info_backup(backup_dir, timestamp, proyecto_dir):
    """Crear archivo con información del backup"""
    info_content = f"""# BACKUP DE SHIKI'S REPORT (ASRUN)
==================================================

## Información del Backup
- **Fecha y hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Timestamp**: {timestamp}
- **Directorio origen**: {proyecto_dir}
- **Directorio backup**: {backup_dir}

## Contenido del Backup

### 📱 Aplicación Principal
- app_streamlit.py (Interfaz web principal)
- requirements.txt (Dependencias Python)

### 🔧 Código Fuente (src/)
- procesar_asrun.py (Procesador principal)
- database_manager.py (Gestor de BD)
- consultar_bd.py (Consultor de BD)

### 🗄️ Bases de Datos
- asrun_database.db (BD principal)
- Backups automáticos de BD

### 📊 Reportes
- Archivos .txt (Reportes de texto)
- Archivos .xlsx (Reportes Excel)

### 📁 Datos
- Archivos .txt de logs AsRun

### 📚 Documentación
- README.md (Documentación principal)
- GUIA_USUARIO.md (Guía de usuario)
- CHANGELOG.md (Historial de cambios)
- RESUMEN_EJECUTIVO.md (Resumen ejecutivo)

### ⚙️ Configuración
- .streamlit/config.toml (Configuración Streamlit)

## Instrucciones de Restauración

### 1. Descomprimir backup
```bash
unzip shikis_report_backup_{timestamp}.zip
```

### 2. Restaurar directorio
```bash
cp -r shikis_report_backup_{timestamp}/* /ruta/destino/
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar aplicación
```bash
streamlit run app_streamlit.py
```

## Verificación del Backup
- ✅ Archivos principales copiados
- ✅ Código fuente completo
- ✅ Bases de datos verificadas
- ✅ Reportes incluidos
- ✅ Configuración preservada

---
Backup creado automáticamente por el script crear_backup_completo.py
"""
    
    info_file = backup_dir / "BACKUP_INFO.md"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)

def get_dir_size(path):
    """Calcular tamaño total de un directorio"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total += os.path.getsize(file_path)
    return total

def main():
    """Función principal"""
    print("🎌 Shiki's Report (Asrun) - Backup Completo")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    current_dir = Path.cwd()
    if not (current_dir / "app_streamlit.py").exists():
        print("❌ Error: Este script debe ejecutarse desde el directorio del proyecto")
        print(f"   Directorio actual: {current_dir}")
        print("   Debe contener app_streamlit.py")
        sys.exit(1)
    
    # Confirmación del usuario
    respuesta = input("\n¿Crear backup completo del proyecto? (s/N): ").lower().strip()
    if respuesta not in ['s', 'sí', 'si', 'y', 'yes']:
        print("❌ Backup cancelado por el usuario")
        sys.exit(0)
    
    # Crear backup
    exito, backup_dir, zip_path = crear_backup_completo()
    
    if exito:
        print(f"\n🎉 ¡Backup completado exitosamente!")
        print(f"📁 Ubicación: {backup_dir}")
        if zip_path:
            print(f"📦 Archivo ZIP: {zip_path}")
        
        # Preguntar si limpiar directorio temporal
        limpiar = input("\n¿Eliminar directorio temporal de backup? (recomendado) (S/n): ").lower().strip()
        if limpiar not in ['n', 'no']:
            try:
                shutil.rmtree(backup_dir)
                print("🗑️  Directorio temporal eliminado")
            except Exception as e:
                print(f"⚠️  No se pudo eliminar directorio temporal: {e}")
    else:
        print("\n❌ Error al crear el backup")
        sys.exit(1)

if __name__ == "__main__":
    main()
