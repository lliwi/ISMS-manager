# Migración: Normalización de Cálculo de Riesgos

## Descripción

Este directorio contiene el script de migración para recalcular todos los riesgos existentes con las nuevas fórmulas normalizadas a escala 0-100.

## ¿Por qué esta migración?

La implementación anterior de las fórmulas MAGERIT generaba valores de riesgo muy altos (ej: 1120.1) que no estaban normalizados, dificultando:
- La interpretación de los niveles de riesgo
- La comparación entre riesgos
- La definición de umbrales de aceptación

Las nuevas fórmulas utilizan una **escala normalizada**:
- **Probabilidad**: 0-10
- **Impacto**: 0-10
- **Riesgo final**: 0-100

## Cambios Implementados

### 1. Fórmulas de Cálculo

**Anterior (generaba valores muy altos)**:
```
IMPACTO = IP × IT × GRAVEDAD × √((IP² + IT²) / 50)
PROBABILIDAD = FREC × FACIL × √((FREC² + FACIL²) / 50)
```

**Nueva (normalizada a escala 0-100)**:
```
IMPACTO = ((IP + IT) / 2) × (GRAVEDAD / 5) × 10      [escala 0-10]
PROBABILIDAD = ((FREC + FACIL) / 2) × 2              [escala 0-10]
RIESGO = PROBABILIDAD × IMPACTO                       [escala 0-100]
```

### 2. Umbrales de Clasificación

**Anterior**:
- Probabilidad ALTA: ≥ 13
- Probabilidad MEDIA: 6-12.9
- Probabilidad BAJA: < 6

**Nuevo**:
- Probabilidad ALTA: ≥ 7 (escala 0-10)
- Probabilidad MEDIA: 4-6.9
- Probabilidad BAJA: < 4

## Uso del Script

### Prerrequisitos

1. Asegurarse de que la aplicación esté detenida o en modo mantenimiento
2. Hacer backup de la base de datos:
   ```bash
   # PostgreSQL
   pg_dump isms_db > backup_antes_migracion_$(date +%Y%m%d_%H%M%S).sql

   # SQLite
   cp instance/isms.db instance/isms_backup_$(date +%Y%m%d_%H%M%S).db
   ```

### Opción 1: Solo Verificar (sin modificar datos)

Verifica que las escalas estén correctas sin hacer cambios:

```bash
cd /path/to/ISMS\ Manager
python migrations/scripts/recalcular_riesgos_normalizados.py --verificar
```

### Opción 2: Recalcular con Confirmación

Solicita confirmación antes de proceder:

```bash
python migrations/scripts/recalcular_riesgos_normalizados.py
```

El script mostrará:
```
⚠️  ADVERTENCIA:
Este script recalculará TODOS los riesgos existentes.
Los valores actuales serán reemplazados con los nuevos cálculos.

¿Desea continuar? (s/N):
```

### Opción 3: Forzar Recálculo (sin confirmación)

**⚠️ USAR CON PRECAUCIÓN** - No solicita confirmación:

```bash
python migrations/scripts/recalcular_riesgos_normalizados.py --forzar
```

## Salida del Script

El script muestra información detallada del proceso:

```
================================================================================
RECÁLCULO DE RIESGOS - NORMALIZACIÓN A ESCALA 0-100
================================================================================

📊 Encontradas 2 evaluaciones de riesgo

🔄 Procesando evaluación: Evaluación Q1 2025 (ID: 1)
   📝 Riesgos a recalcular: 150
      ⚡ Cambio significativo en R-1-5-3-12-C:
         Riesgo: 1120.10 → 64.80
         Prob: 18.75 → 8.00
         Imp: 59.73 → 8.10
   ✅ Completado: 150 exitosos, 0 errores

🔄 Procesando evaluación: Evaluación Anual 2025 (ID: 2)
   📝 Riesgos a recalcular: 87
   ✅ Completado: 87 exitosos, 0 errores

================================================================================
RESUMEN DE MIGRACIÓN
================================================================================
✅ Riesgos recalculados exitosamente: 237
❌ Errores encontrados: 0

🎉 ¡Migración completada exitosamente!
```

Luego ejecuta una verificación automática:

```
================================================================================
VERIFICACIÓN DE ESCALAS
================================================================================

📊 Verificando 237 riesgos...

✅ Todas las probabilidades están en rango (0-10)
✅ Todos los impactos están en rango (0-10)
✅ Todos los riesgos están en rango (0-100)

📈 ESTADÍSTICAS:
   Riesgo promedio: 35.67
   Riesgo mínimo: 2.40
   Riesgo máximo: 92.50

   Probabilidad promedio: 6.45
   Impacto promedio: 5.52
```

## Verificación Post-Migración

### 1. Verificar Dashboard

Acceder a `http://localhost/riesgos/dashboard` y verificar:
- Los valores de riesgo están entre 0-100
- La matriz de riesgos muestra distribución coherente
- El gráfico de distribución por nivel es correcto

### 2. Verificar Evaluaciones

Revisar evaluaciones individuales en:
`http://localhost/riesgos/evaluaciones/<id>`

Confirmar:
- Estadísticas coherentes
- Top riesgos ordenados correctamente
- Clasificaciones (Muy Alto, Alto, Medio, Bajo, Muy Bajo) apropiadas

### 3. Revisar Umbrales

El **umbral de riesgo objetivo** de las evaluaciones debe ajustarse a la nueva escala:

**Valores sugeridos**:
- **Conservador**: Umbral = 25 (Riesgo BAJO)
- **Moderado**: Umbral = 40 (Riesgo MEDIO)
- **Tolerante**: Umbral = 60 (Riesgo ALTO)

Actualizar en: `Evaluaciones → Editar → Umbral de Riesgo Objetivo`

## Rollback (en caso de problemas)

Si es necesario revertir los cambios:

### PostgreSQL
```bash
# Detener aplicación
systemctl stop isms-manager

# Restaurar backup
psql isms_db < backup_antes_migracion_YYYYMMDD_HHMMSS.sql

# Revertir código a versión anterior
git checkout <commit-anterior>

# Reiniciar aplicación
systemctl start isms-manager
```

### SQLite
```bash
# Restaurar backup
cp instance/isms_backup_YYYYMMDD_HHMMSS.db instance/isms.db

# Revertir código
git checkout <commit-anterior>
```

## Troubleshooting

### Error: "unable to open database file"

**Causa**: Permisos incorrectos o ruta incorrecta

**Solución**:
```bash
# Verificar permisos
ls -la instance/isms.db

# Ajustar permisos si es necesario
chmod 664 instance/isms.db
chown www-data:www-data instance/isms.db  # En producción
```

### Error: "No module named 'application'"

**Causa**: Script ejecutado desde directorio incorrecto

**Solución**:
```bash
# Ejecutar desde el directorio raíz del proyecto
cd /path/to/ISMS\ Manager
python migrations/scripts/recalcular_riesgos_normalizados.py
```

### Valores aún parecen incorrectos

**Causa**: Controles con madurez muy alta o baja

**Solución**: Revisar y ajustar niveles de madurez de controles en:
`http://localhost/riesgos/controles/<id>/salvaguarda`

## Documentación Adicional

- **Metodología completa**: Ver `/docs/METODOLOGIA_CALCULO_RIESGOS.md`
- **Código fuente**: Ver `/app/risks/services/risk_calculation_service.py`
- **Modelo de datos**: Ver `/app/risks/models.py`

## Soporte

Para reportar problemas o dudas sobre la migración:
1. Verificar logs de aplicación en `/logs/`
2. Revisar documentación técnica
3. Contactar al equipo de desarrollo

---

**Fecha de creación**: 2025-10-25
**Versión del script**: 1.0
**Compatibilidad**: ISMS Manager v1.x
