"""
Script Maestro de Inicialización de Catálogos
Precarga todos los catálogos necesarios para el módulo de gestión de riesgos
"""

import sys
from application import create_app
from models import db


def seed_all_catalogs():
    """
    Ejecuta todos los scripts de precarga de catálogos
    """
    print("\n" + "="*80)
    print("🚀 INICIALIZACIÓN DE CATÁLOGOS DE GESTIÓN DE RIESGOS")
    print("="*80)
    print("\nEste script cargará los siguientes catálogos:")
    print("  1. Amenazas MAGERIT 3.2 (aprox. 50 amenazas)")
    print("  2. Controles ISO/IEC 27002:2022 (93 controles)")
    print("\n" + "="*80)

    # Importar módulos de seed
    from app.risks.seed_amenazas import seed_amenazas
    from app.risks.seed_controles import seed_controles

    # Crear contexto de aplicación
    app = create_app()

    with app.app_context():
        try:
            # 1. Cargar amenazas MAGERIT
            print("\n📋 PASO 1/2: Cargando amenazas MAGERIT 3.2...")
            seed_amenazas()

            # 2. Cargar controles ISO 27002
            print("\n📋 PASO 2/2: Cargando controles ISO/IEC 27002:2022...")
            seed_controles()

            # Resumen final
            print("\n" + "="*80)
            print("✅ INICIALIZACIÓN COMPLETADA CON ÉXITO")
            print("="*80)

            # Estadísticas finales desde la base de datos
            from app.risks.models import Amenaza, ControlISO27002

            total_amenazas = Amenaza.query.count()
            total_controles = ControlISO27002.query.count()

            print(f"\n📊 RESUMEN FINAL:")
            print(f"   • Total de amenazas cargadas: {total_amenazas}")
            print(f"   • Total de controles cargados: {total_controles}")
            print(f"\n✨ El módulo de gestión de riesgos está listo para usar.")
            print("="*80 + "\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Operación cancelada por el usuario.")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Error durante la inicialización: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    seed_all_catalogs()
