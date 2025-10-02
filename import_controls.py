#!/usr/bin/env python3
"""Script temporal para importar controles SOA desde CSV"""

from app import create_app
from models import db, SOAControl, SOAVersion
import csv
from datetime import datetime

def import_controls():
    app = create_app()

    with app.app_context():
        # Obtener la versión SOA actual
        version = SOAVersion.query.filter_by(is_current=True).first()

        if not version:
            print("ERROR: No hay una versión SOA activa")
            return

        print(f"Importando controles a la versión: {version.version_number}")

        # Leer el archivo CSV
        csv_file = 'tests/data/controles_soa_ejemplo.csv'

        added_count = 0

        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)

            for row in csv_reader:
                control_id = row.get('control_id')

                if not control_id or not control_id.strip():
                    continue

                # Verificar si ya existe
                existing = SOAControl.query.filter_by(
                    control_id=control_id,
                    soa_version_id=version.id
                ).first()

                if existing:
                    print(f"  - Control {control_id} ya existe, omitiendo...")
                    continue

                # Crear nuevo control
                is_applicable = row.get('is_applicable', 'TRUE').upper() == 'TRUE'

                # Determinar applicability_status
                if is_applicable:
                    applicability_status = 'aplicable'
                else:
                    applicability_status = 'no_aplicable'

                # Determinar implementation_status
                impl_status = row.get('implementation_status', 'not_implemented').lower()
                if impl_status in ['implemented', 'pending', 'not_implemented']:
                    implementation_status = impl_status
                else:
                    implementation_status = 'not_implemented'

                # Determinar maturity_level
                maturity = row.get('maturity_level', 'no_implementado').lower()
                valid_maturity = ['no_implementado', 'inicial', 'repetible', 'definido', 'controlado', 'cuantificado', 'optimizado']
                if maturity not in valid_maturity:
                    maturity = 'no_implementado'

                control = SOAControl(
                    control_id=control_id,
                    soa_version_id=version.id,
                    title=row.get('title', ''),
                    description=row.get('description', ''),
                    category=row.get('category', ''),
                    applicability_status=applicability_status,
                    implementation_status=implementation_status,
                    maturity_level=maturity,
                    justification=row.get('justification', ''),
                    transfer_details=row.get('transfer_details', ''),
                    evidence=row.get('evidence', '')
                )

                # Fecha objetivo
                target_date_str = row.get('target_date', '')
                if target_date_str and target_date_str.strip():
                    try:
                        control.target_date = datetime.strptime(target_date_str.strip(), '%Y-%m-%d').date()
                    except ValueError:
                        pass

                db.session.add(control)
                added_count += 1
                print(f"  + Añadido control: {control_id} - {control.title}")

        db.session.commit()
        print(f"\n✅ Importación completada: {added_count} controles añadidos")

if __name__ == '__main__':
    import_controls()
