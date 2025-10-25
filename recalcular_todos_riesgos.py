#!/usr/bin/env python
"""
Script para recalcular todos los riesgos del sistema
Aplica los nuevos controles del catálogo controles_amenazas
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from application import create_app
from app.risks.services.risk_calculation_service import RiskCalculationService
from app.risks.models import EvaluacionRiesgo, Riesgo
from models import db

def recalcular_todos():
    """Recalcula todos los riesgos de todas las evaluaciones"""
    app = create_app()

    with app.app_context():
        # Obtener todas las evaluaciones
        evaluaciones = EvaluacionRiesgo.query.all()

        print(f"📊 Encontradas {len(evaluaciones)} evaluaciones")
        print("=" * 60)

        total_riesgos = 0
        total_recalculados = 0

        for evaluacion in evaluaciones:
            print(f"\n🔄 Evaluación {evaluacion.id}: {evaluacion.nombre}")

            riesgos = Riesgo.query.filter_by(evaluacion_id=evaluacion.id).all()
            print(f"   Riesgos a recalcular: {len(riesgos)}")

            recalculados = 0
            errores = 0

            for i, riesgo in enumerate(riesgos, 1):
                try:
                    # Mostrar progreso cada 50 riesgos
                    if i % 50 == 0:
                        print(f"   Progreso: {i}/{len(riesgos)} ({i*100//len(riesgos)}%)")

                    RiskCalculationService.recalcular_riesgo(riesgo.id)
                    recalculados += 1
                except Exception as e:
                    errores += 1
                    if errores <= 5:  # Solo mostrar primeros 5 errores
                        print(f"   ❌ Error en riesgo {riesgo.id}: {e}")

            total_riesgos += len(riesgos)
            total_recalculados += recalculados

            print(f"   ✅ Recalculados: {recalculados}")
            if errores > 0:
                print(f"   ⚠️  Errores: {errores}")

        print("\n" + "=" * 60)
        print(f"🎉 COMPLETADO")
        print(f"   Total riesgos: {total_riesgos}")
        print(f"   Recalculados: {total_recalculados}")
        print(f"   Errores: {total_riesgos - total_recalculados}")
        print("=" * 60)

if __name__ == '__main__':
    print("🚀 Iniciando recálculo de todos los riesgos...")
    print("   Esto puede tomar varios minutos...\n")
    recalcular_todos()
