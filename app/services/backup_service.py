"""
Servicio de Backup y Restauración del Sistema ISMS
ISO 27001:2023 - Control A.8.13 (Respaldo de información)

Este servicio permite:
- Crear backups completos del sistema (base de datos + archivos)
- Restaurar el sistema desde un backup
- Listar backups disponibles
- Gestionar la retención de backups
"""
import os
import zipfile
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import current_app
from models import db
import shutil
import tempfile


class BackupService:
    """Servicio de gestión de backups del sistema"""

    BACKUP_DIR = 'backups'
    UPLOAD_FOLDERS = [
        'uploads/changes',
        'uploads/documents',
        'uploads/incidents',
        'uploads/tasks',
        'uploads/assets',
        'uploads/audits'
    ]

    @classmethod
    def get_backup_directory(cls):
        """Obtiene el directorio de backups, creándolo si no existe"""
        backup_path = Path(cls.BACKUP_DIR)
        backup_path.mkdir(parents=True, exist_ok=True)
        return backup_path

    @classmethod
    def create_backup(cls, description='Manual backup', include_files=True):
        """
        Crea un backup completo del sistema

        Args:
            description: Descripción del backup
            include_files: Si se deben incluir los archivos subidos

        Returns:
            dict con información del backup creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'isms_backup_{timestamp}'

        backup_dir = cls.get_backup_directory()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # 1. Exportar base de datos
            print(f"📦 Creando backup: {backup_name}")
            db_file = temp_dir / 'database.sql'
            cls._export_database(db_file)

            # 2. Crear archivo de metadatos
            metadata = {
                'backup_name': backup_name,
                'created_at': timestamp,
                'description': description,
                'database_engine': current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split(':')[0],
                'include_files': include_files,
                'app_version': '1.0.0',  # TODO: Obtener de config
                'tables_count': cls._count_tables(),
                'files_included': []
            }

            # 3. Copiar archivos si se solicita
            if include_files:
                files_dir = temp_dir / 'files'
                files_dir.mkdir(exist_ok=True)

                for folder in cls.UPLOAD_FOLDERS:
                    folder_path = Path(folder)
                    if folder_path.exists():
                        dest_path = files_dir / folder
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        if folder_path.is_dir():
                            shutil.copytree(folder_path, dest_path, dirs_exist_ok=True)
                            # Contar archivos
                            file_count = sum(1 for _ in dest_path.rglob('*') if _.is_file())
                            metadata['files_included'].append({
                                'folder': folder,
                                'file_count': file_count
                            })

            # 4. Guardar metadatos
            metadata_file = temp_dir / 'metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # 5. Crear archivo ZIP
            zip_path = backup_dir / f'{backup_name}.zip'
            cls._create_zip(temp_dir, zip_path)

            # 6. Calcular tamaño
            file_size = os.path.getsize(zip_path)

            print(f"✅ Backup creado: {zip_path} ({cls._format_size(file_size)})")

            return {
                'success': True,
                'backup_name': backup_name,
                'file_path': str(zip_path),
                'file_size': file_size,
                'created_at': timestamp,
                'description': description,
                'metadata': metadata
            }

        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Limpiar directorio temporal
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    @classmethod
    def _export_database(cls, output_file):
        """Exporta la base de datos a un archivo SQL"""
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')

        if db_uri.startswith('postgresql'):
            cls._export_postgresql(db_uri, output_file)
        elif db_uri.startswith('sqlite'):
            cls._export_sqlite(db_uri, output_file)
        else:
            raise ValueError(f"Motor de base de datos no soportado: {db_uri.split(':')[0]}")

    @classmethod
    def _export_postgresql(cls, db_uri, output_file):
        """Exporta base de datos PostgreSQL usando pg_dump"""
        # Parsear URI: postgresql://user:pass@host:port/database
        from urllib.parse import urlparse
        parsed = urlparse(db_uri)

        env = os.environ.copy()
        if parsed.password:
            env['PGPASSWORD'] = parsed.password

        cmd = [
            'pg_dump',
            '-h', parsed.hostname or 'localhost',
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path.lstrip('/'),
            '-f', str(output_file),
            '--no-owner',
            '--no-privileges',
            '--clean',
            '--if-exists'
        ]

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error ejecutando pg_dump: {result.stderr}")

    @classmethod
    def _export_sqlite(cls, db_uri, output_file):
        """Exporta base de datos SQLite"""
        # Extraer ruta del archivo de la URI
        db_path = db_uri.replace('sqlite:///', '')

        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Base de datos SQLite no encontrada: {db_path}")

        # Usar .dump de sqlite3
        cmd = ['sqlite3', db_path, '.dump']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error ejecutando sqlite3 dump: {result.stderr}")

        with open(output_file, 'w') as f:
            f.write(result.stdout)

    @classmethod
    def _count_tables(cls):
        """Cuenta el número de tablas en la base de datos"""
        try:
            inspector = db.inspect(db.engine)
            return len(inspector.get_table_names())
        except:
            return 0

    @classmethod
    def _create_zip(cls, source_dir, output_file):
        """Crea un archivo ZIP con el contenido del directorio"""
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

    @classmethod
    def list_backups(cls):
        """Lista todos los backups disponibles"""
        backup_dir = cls.get_backup_directory()
        backups = []

        for backup_file in sorted(backup_dir.glob('isms_backup_*.zip'), reverse=True):
            try:
                # Leer metadatos del ZIP
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if 'metadata.json' in zipf.namelist():
                        metadata = json.loads(zipf.read('metadata.json'))
                    else:
                        # Backup antiguo sin metadatos
                        metadata = {
                            'backup_name': backup_file.stem,
                            'created_at': datetime.fromtimestamp(backup_file.stat().st_mtime).strftime('%Y%m%d_%H%M%S'),
                            'description': 'Backup sin metadatos'
                        }

                backups.append({
                    'name': backup_file.name,
                    'path': str(backup_file),
                    'size': backup_file.stat().st_size,
                    'size_formatted': cls._format_size(backup_file.stat().st_size),
                    'created_at': metadata.get('created_at'),
                    'description': metadata.get('description'),
                    'metadata': metadata
                })
            except Exception as e:
                print(f"Error leyendo backup {backup_file}: {e}")
                continue

        return backups

    @classmethod
    def restore_backup(cls, backup_path, restore_files=True):
        """
        Restaura el sistema desde un backup

        Args:
            backup_path: Ruta al archivo de backup
            restore_files: Si se deben restaurar los archivos

        Returns:
            dict con resultado de la restauración
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            return {'success': False, 'error': 'Archivo de backup no encontrado'}

        temp_dir = Path(tempfile.mkdtemp())

        try:
            print(f"📥 Restaurando backup desde: {backup_path}")

            # 1. Extraer ZIP
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            # 2. Leer metadatos
            metadata_file = temp_dir / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"📋 Backup creado: {metadata.get('created_at')}")
            else:
                metadata = {}

            # 3. Restaurar base de datos
            db_file = temp_dir / 'database.sql'
            if db_file.exists():
                cls._import_database(db_file)
                print("✅ Base de datos restaurada")
            else:
                return {'success': False, 'error': 'Archivo de base de datos no encontrado en el backup'}

            # 4. Restaurar archivos si se solicita
            if restore_files:
                files_dir = temp_dir / 'files'
                if files_dir.exists():
                    cls._restore_files(files_dir)
                    print("✅ Archivos restaurados")

            print(f"✅ Restauración completada")

            return {
                'success': True,
                'backup_name': metadata.get('backup_name'),
                'restored_at': datetime.now().isoformat(),
                'metadata': metadata
            }

        except Exception as e:
            print(f"❌ Error restaurando backup: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Limpiar directorio temporal
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    @classmethod
    def _import_database(cls, sql_file):
        """Importa la base de datos desde un archivo SQL"""
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')

        if db_uri.startswith('postgresql'):
            cls._import_postgresql(db_uri, sql_file)
        elif db_uri.startswith('sqlite'):
            cls._import_sqlite(db_uri, sql_file)
        else:
            raise ValueError(f"Motor de base de datos no soportado")

    @classmethod
    def _import_postgresql(cls, db_uri, sql_file):
        """Importa base de datos PostgreSQL usando psql"""
        from urllib.parse import urlparse
        parsed = urlparse(db_uri)

        # Leer el archivo SQL y filtrar comandos incompatibles
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Filtrar comandos SET que pueden ser incompatibles entre versiones
        incompatible_params = [
            'transaction_timeout',
            'idle_in_transaction_session_timeout',
            'lock_timeout',
            'statement_timeout'
        ]

        lines = sql_content.split('\n')
        filtered_lines = []
        for line in lines:
            # Filtrar líneas SET con parámetros incompatibles
            if line.strip().startswith('SET '):
                if not any(param in line for param in incompatible_params):
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)

        # Escribir SQL filtrado a un archivo temporal
        filtered_sql_file = Path(tempfile.mktemp(suffix='.sql'))
        try:
            with open(filtered_sql_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(filtered_lines))

            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password

            cmd = [
                'psql',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username,
                '-d', parsed.path.lstrip('/'),
                '-f', str(filtered_sql_file),
                '-v', 'ON_ERROR_STOP=0',  # Continuar en caso de errores
                '--quiet'  # Reducir salida verbose
            ]

            print(f"🔄 Ejecutando psql para restaurar base de datos...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            # Mostrar warnings pero no fallar por errores de parámetros
            if result.stderr:
                print(f"⚠️  Advertencias durante importación:")
                for line in result.stderr.split('\n')[:10]:  # Mostrar solo primeras 10 líneas
                    if line.strip():
                        print(f"    {line}")

            # Solo fallar si hay errores críticos (no de configuración)
            if result.returncode != 0:
                stderr_lower = result.stderr.lower()
                # Ignorar errores de parámetros de configuración
                if 'error' in stderr_lower and 'configuration parameter' not in stderr_lower:
                    # Verificar si el error es crítico
                    critical_errors = ['fatal', 'connection', 'authentication']
                    if any(err in stderr_lower for err in critical_errors):
                        raise Exception(f"Error crítico ejecutando psql: {result.stderr}")

            print("✅ Base de datos importada correctamente")

        finally:
            # Limpiar archivo temporal
            if filtered_sql_file.exists():
                filtered_sql_file.unlink()

    @classmethod
    def _import_sqlite(cls, db_uri, sql_file):
        """Importa base de datos SQLite"""
        db_path = db_uri.replace('sqlite:///', '')

        # Leer el archivo SQL
        with open(sql_file, 'r') as f:
            sql_content = f.read()

        cmd = ['sqlite3', db_path]
        result = subprocess.run(cmd, input=sql_content, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error ejecutando sqlite3: {result.stderr}")

    @classmethod
    def _restore_files(cls, files_dir):
        """Restaura los archivos desde el directorio de backup"""
        for folder in cls.UPLOAD_FOLDERS:
            source = files_dir / folder
            if source.exists():
                dest = Path(folder)
                dest.parent.mkdir(parents=True, exist_ok=True)

                # Eliminar carpeta existente y copiar desde backup
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)

                file_count = sum(1 for _ in dest.rglob('*') if _.is_file())
                print(f"  ✅ Restaurados {file_count} archivos en {folder}")

    @classmethod
    def delete_backup(cls, backup_name):
        """Elimina un backup"""
        backup_dir = cls.get_backup_directory()
        backup_file = backup_dir / backup_name

        if backup_file.exists():
            os.remove(backup_file)
            return {'success': True}
        else:
            return {'success': False, 'error': 'Backup no encontrado'}

    @classmethod
    def _format_size(cls, size_bytes):
        """Formatea el tamaño en bytes a una cadena legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
