#!/usr/bin/env python3
"""
Script de Migración: Recálculo de Riesgos con Fórmulas Normalizadas

Este script recalcula todos los riesgos existentes utilizando las nuevas
fórmulas normalizadas a escala 0-100.

IMPORTANTE: Este script debe ejecutarse después de actualizar el código
con las nuevas fórmulas de cálculo.

Fecha: 2025-10-25
Versión: 1.0
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from application import app
from models import db
from app.risks.models import Riesgo, EvaluacionRiesgo
from app.risks.services.risk_calculation_service import RiskCalculationService


def recalcular_todos_los_riesgos():
    """
    Recalcula todos los riesgos en el sistema con las nuevas fórmulas
    """
    print("=" * 80)
    print("RECÁLCULO DE RIESGOS - NORMALIZACIÓN A ESCALA 0-100")
    print("=" * 80)
    print()

    with app.app_context():
        # Obtener todas las evaluaciones
        evaluaciones = EvaluacionRiesgo.query.all()

        if not evaluaciones:
            print("⚠️  No se encontraron evaluaciones de riesgo.")
            return

        print(f"📊 Encontradas {len(evaluaciones)} evaluaciones de riesgo")
        print()

        total_riesgos_recalculados = 0
        total_errores = 0

        for evaluacion in evaluaciones:
            print(f"🔄 Procesando evaluación: {evaluacion.nombre} (ID: {evaluacion.id})")

            # Obtener todos los riesgos de esta evaluación
            riesgos = Riesgo.query.filter_by(evaluacion_id=evaluacion.id).all()

            if not riesgos:
                print(f"   ⚠️  Sin riesgos. Saltando...")
                print()
                continue

            print(f"   📝 Riesgos a recalcular: {len(riesgos)}")

            riesgos_ok = 0
            riesgos_error = 0

            for riesgo in riesgos:
                try:
                    # Guardar valores anteriores para comparación
                    nivel_anterior = riesgo.nivel_riesgo_efectivo
                    prob_anterior = riesgo.probabilidad_efectiva
                    imp_anterior = riesgo.impacto_efectivo

                    # Recalcular
                    RiskCalculationService.recalcular_riesgo(riesgo.id)

                    # Refrescar objeto desde BD
                    db.session.refresh(riesgo)

                    # Mostrar cambio significativo
                    if abs(nivel_anterior - riesgo.nivel_riesgo_efectivo) > 10:
                        print(f"      ⚡ Cambio significativo en {riesgo.codigo}:")
                        print(f"         Riesgo: {nivel_anterior:.2f} → {riesgo.nivel_riesgo_efectivo:.2f}")
                        print(f"         Prob: {prob_anterior:.2f} → {riesgo.probabilidad_efectiva:.2f}")
                        print(f"         Imp: {imp_anterior:.2f} → {riesgo.impacto_efectivo:.2f}")

                    riesgos_ok += 1

                except Exception as e:
                    print(f"      ❌ Error en riesgo {riesgo.codigo}: {str(e)}")
                    riesgos_error += 1
                    db.session.rollback()

            # Commit de esta evaluación
            try:
                db.session.commit()
                print(f"   ✅ Completado: {riesgos_ok} exitosos, {riesgos_error} errores")
                total_riesgos_recalculados += riesgos_ok
                total_errores += riesgos_error
            except Exception as e:
                print(f"   ❌ Error al guardar cambios: {str(e)}")
                db.session.rollback()

            print()

        print("=" * 80)
        print("RESUMEN DE MIGRACIÓN")
        print("=" * 80)
        print(f"✅ Riesgos recalculados exitosamente: {total_riesgos_recalculados}")
        print(f"❌ Errores encontrados: {total_errores}")
        print()

        if total_errores == 0:
            print("🎉 ¡Migración completada exitosamente!")
        else:
            print("⚠️  Migración completada con errores. Revisar log.")

        print()


def verificar_escalas():
    """
    Verifica que los valores estén en las escalas esperadas
    """
    print("=" * 80)
    print("VERIFICACIÓN DE ESCALAS")
    print("=" * 80)
    print()

    with app.app_context():
        riesgos = Riesgo.query.all()

        if not riesgos:
            print("⚠️  No hay riesgos para verificar.")
            return

        print(f"📊 Verificando {len(riesgos)} riesgos...")
        print()

        # Rangos esperados
        prob_fuera_rango = []
        imp_fuera_rango = []
        riesgo_fuera_rango = []

        for r in riesgos:
            # Probabilidad debe estar en 0-10
            if r.probabilidad_efectiva and (r.probabilidad_efectiva < 0 or r.probabilidad_efectiva > 10):
                prob_fuera_rango.append((r.codigo, r.probabilidad_efectiva))

            # Impacto debe estar en 0-10
            if r.impacto_efectivo and (r.impacto_efectivo < 0 or r.impacto_efectivo > 10):
                imp_fuera_rango.append((r.codigo, r.impacto_efectivo))

            # Riesgo debe estar en 0-100
            if r.nivel_riesgo_efectivo and (r.nivel_riesgo_efectivo < 0 or r.nivel_riesgo_efectivo > 100):
                riesgo_fuera_rango.append((r.codigo, r.nivel_riesgo_efectivo))

        # Reportar
        if prob_fuera_rango:
            print(f"⚠️  Probabilidades fuera de rango (0-10): {len(prob_fuera_rango)}")
            for codigo, val in prob_fuera_rango[:5]:  # Mostrar solo primeros 5
                print(f"   - {codigo}: {val}")
            if len(prob_fuera_rango) > 5:
                print(f"   ... y {len(prob_fuera_rango) - 5} más")
            print()
        else:
            print("✅ Todas las probabilidades están en rango (0-10)")

        if imp_fuera_rango:
            print(f"⚠️  Impactos fuera de rango (0-10): {len(imp_fuera_rango)}")
            for codigo, val in imp_fuera_rango[:5]:
                print(f"   - {codigo}: {val}")
            if len(imp_fuera_rango) > 5:
                print(f"   ... y {len(imp_fuera_rango) - 5} más")
            print()
        else:
            print("✅ Todos los impactos están en rango (0-10)")

        if riesgo_fuera_rango:
            print(f"⚠️  Riesgos fuera de rango (0-100): {len(riesgo_fuera_rango)}")
            for codigo, val in riesgo_fuera_rango[:5]:
                print(f"   - {codigo}: {val}")
            if len(riesgo_fuera_rango) > 5:
                print(f"   ... y {len(riesgo_fuera_rango) - 5} más")
            print()
        else:
            print("✅ Todos los riesgos están en rango (0-100)")

        # Estadísticas
        print()
        print("📈 ESTADÍSTICAS:")

        riesgos_con_datos = [r for r in riesgos if r.nivel_riesgo_efectivo]

        if riesgos_con_datos:
            niveles = [r.nivel_riesgo_efectivo for r in riesgos_con_datos]
            probs = [r.probabilidad_efectiva for r in riesgos_con_datos if r.probabilidad_efectiva]
            imps = [r.impacto_efectivo for r in riesgos_con_datos if r.impacto_efectivo]

            print(f"   Riesgo promedio: {sum(niveles)/len(niveles):.2f}")
            print(f"   Riesgo mínimo: {min(niveles):.2f}")
            print(f"   Riesgo máximo: {max(niveles):.2f}")
            print()
            print(f"   Probabilidad promedio: {sum(probs)/len(probs):.2f}")
            print(f"   Impacto promedio: {sum(imps)/len(imps):.2f}")

        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Recalcula riesgos con fórmulas normalizadas'
    )
    parser.add_argument(
        '--verificar',
        action='store_true',
        help='Solo verificar escalas sin recalcular'
    )
    parser.add_argument(
        '--forzar',
        action='store_true',
        help='Forzar recálculo sin confirmación'
    )

    args = parser.parse_args()

    if args.verificar:
        verificar_escalas()
    else:
        if not args.forzar:
            print()
            print("⚠️  ADVERTENCIA:")
            print("Este script recalculará TODOS los riesgos existentes.")
            print("Los valores actuales serán reemplazados con los nuevos cálculos.")
            print()
            respuesta = input("¿Desea continuar? (s/N): ")

            if respuesta.lower() != 's':
                print("Operación cancelada.")
                sys.exit(0)

        recalcular_todos_los_riesgos()

        print()
        print("Ejecutando verificación post-migración...")
        print()
        verificar_escalas()
