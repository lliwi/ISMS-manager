#!/usr/bin/env python3
"""
Script para importar controles ISO 27001 a la base de datos
Soporta múltiples versiones y evita duplicados
"""

import csv
import sys
import os
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import app
from models import db, SOAControl, SOAVersion


def get_or_create_version(version_number, description, is_active=True):
    """
    Obtiene o crea una versión SOA
    """
    version = SOAVersion.query.filter_by(version_number=version_number).first()

    if not version:
        version = SOAVersion(
            version_number=version_number,
            description=description,
            is_active=is_active,
            created_at=datetime.utcnow()
        )
        db.session.add(version)
        db.session.commit()
        print(f"✓ Versión creada: {version_number}")
    else:
        print(f"→ Versión ya existe: {version_number}")

    return version


def import_controls_from_csv(csv_file, version_id, skip_existing=True):
    """
    Importa controles desde un archivo CSV

    Args:
        csv_file: Ruta al archivo CSV
        version_id: ID de la versión SOA
        skip_existing: Si True, omite controles que ya existen (default: True)
    """

    if not os.path.exists(csv_file):
        print(f"✗ Error: Archivo no encontrado: {csv_file}")
        return 0

    imported = 0
    skipped = 0
    errors = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                control_id = row['control_id'].strip()

                # Verificar si ya existe el control para esta versión
                existing = SOAControl.query.filter_by(
                    control_id=control_id,
                    soa_version_id=version_id
                ).first()

                if existing:
                    if skip_existing:
                        print(f"  ⊗ Control ya existe: {control_id} (omitido)")
                        skipped += 1
                        continue
                    else:
                        # Actualizar control existente
                        existing.title = row['title'].strip()
                        existing.description = row['description'].strip()
                        existing.category = row['category'].strip()
                        existing.applicability_status = row.get('applicability_status', 'aplicable').strip()
                        existing.implementation_status = row.get('implementation_status', 'not_implemented').strip()
                        existing.updated_at = datetime.utcnow()
                        print(f"  ↻ Control actualizado: {control_id}")
                        imported += 1
                        continue

                # Crear nuevo control
                control = SOAControl(
                    control_id=control_id,
                    title=row['title'].strip(),
                    description=row['description'].strip(),
                    category=row['category'].strip(),
                    applicability_status=row.get('applicability_status', 'aplicable').strip(),
                    implementation_status=row.get('implementation_status', 'not_implemented').strip(),
                    soa_version_id=version_id,
                    created_at=datetime.utcnow()
                )

                db.session.add(control)
                print(f"  ✓ Control importado: {control_id} - {row['title'][:50]}...")
                imported += 1

            except Exception as e:
                print(f"  ✗ Error procesando {row.get('control_id', 'unknown')}: {e}")
                errors += 1
                continue

    db.session.commit()

    print(f"\n{'='*60}")
    print(f"Resumen de importación:")
    print(f"  • Importados: {imported}")
    print(f"  • Omitidos: {skipped}")
    print(f"  • Errores: {errors}")
    print(f"{'='*60}\n")

    return imported


def main():
    """
    Función principal
    """
    print("\n" + "="*60)
    print("IMPORTADOR DE CONTROLES ISO 27001")
    print("="*60 + "\n")

    with app.app_context():
        # Opción 1: Importar ISO 27001:2022 (93 controles)
        print("1. Importando controles ISO 27001:2022...")
        version_2022 = get_or_create_version(
            version_number="ISO 27001:2022",
            description="Anexo A - ISO/IEC 27001:2022 - 93 controles organizados en 4 categorías",
            is_active=True
        )

        csv_file_2022 = os.path.join(
            os.path.dirname(__file__),
            '..',
            'iso27001_2022_controls_complete.csv'
        )

        if os.path.exists(csv_file_2022):
            imported_2022 = import_controls_from_csv(csv_file_2022, version_2022.id)
            print(f"✓ Importados {imported_2022} controles de ISO 27001:2022\n")
        else:
            print(f"⚠ Archivo no encontrado: {csv_file_2022}\n")

        # Opción 2: Verificar si existen controles de versión anterior
        version_2013 = SOAVersion.query.filter_by(version_number="ISO 27001:2013").first()
        if version_2013:
            control_count = SOAControl.query.filter_by(soa_version_id=version_2013.id).count()
            print(f"→ Detectada versión anterior: ISO 27001:2013 ({control_count} controles)")
            print(f"  Estas versiones pueden coexistir en el sistema.\n")

        # Estadísticas finales
        total_versions = SOAVersion.query.count()
        total_controls = SOAControl.query.count()

        print("="*60)
        print("ESTADO FINAL DE LA BASE DE DATOS:")
        print(f"  • Versiones SOA: {total_versions}")
        print(f"  • Controles totales: {total_controls}")

        # Desglose por versión
        versions = SOAVersion.query.all()
        for v in versions:
            count = SOAControl.query.filter_by(soa_version_id=v.id).count()
            status = "✓ Activa" if v.is_active else "✗ Inactiva"
            print(f"    - {v.version_number}: {count} controles [{status}]")

        print("="*60 + "\n")


if __name__ == '__main__':
    main()
