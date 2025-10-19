# Gestión de Versiones de Controles ISO 27001

## Contexto

El sistema ISMS Manager soporta **múltiples versiones** de controles ISO 27001 para permitir:

1. **Migración gradual** entre versiones (ej: ISO 27001:2013 → ISO 27001:2022)
2. **Coexistencia** de diferentes versiones SOA
3. **Compatibilidad** con futuras actualizaciones de la norma ISO
4. **Personalización** por organización

## Estructura de Versiones

### Tabla: `soa_versions`
```sql
- id (PK)
- version_number (ej: "ISO 27001:2022")
- description
- is_active (boolean)
- created_at
```

### Tabla: `soa_controls`
```sql
- id (PK)
- control_id (ej: "A.5.1")
- title
- description
- category
- soa_version_id (FK → soa_versions)
- applicability_status
- implementation_status
- ...
```

### Constraint importante:
```sql
UNIQUE (control_id, soa_version_id)
```
Esto permite tener `A.5.1` en ISO 27001:2013 y también en ISO 27001:2022 con diferentes descripciones.

## Versiones Soportadas

### ISO 27001:2022 (Actual)
- **93 controles** organizados en 4 categorías:
  - Organizacional (37 controles: A.5.1 - A.5.37)
  - Personas (8 controles: A.6.1 - A.6.8)
  - Físico (14 controles: A.7.1 - A.7.14)
  - Tecnológico (34 controles: A.8.1 - A.8.34)

### ISO 27001:2013 (Anterior)
- **114 controles** en 14 dominios (A.5 - A.18)
- Puede mantenerse para organizaciones que aún no han migrado

## Importación de Controles

### Método 1: Script de importación

```bash
# Ejecutar desde el contenedor web
docker exec ismsmanager-web-1 python3 scripts/import_iso27001_controls.py
```

Este script:
- ✅ Crea la versión si no existe
- ✅ Evita duplicados (por control_id + version_id)
- ✅ Permite actualizar controles existentes
- ✅ Muestra estadísticas de importación

### Método 2: Importación manual vía Python

```python
from application import app
from models import db, SOAControl, SOAVersion
import csv

with app.app_context():
    # Crear versión
    version = SOAVersion(
        version_number="ISO 27001:2022",
        description="Anexo A - ISO/IEC 27001:2022",
        is_active=True
    )
    db.session.add(version)
    db.session.commit()

    # Importar controles desde CSV
    with open('iso27001_2022_controls_complete.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            control = SOAControl(
                control_id=row['control_id'],
                title=row['title'],
                description=row['description'],
                category=row['category'],
                applicability_status=row['applicability_status'],
                implementation_status=row['implementation_status'],
                soa_version_id=version.id
            )
            db.session.add(control)

    db.session.commit()
```

## Migración entre Versiones

### Escenario: Migrar de ISO 27001:2013 a ISO 27001:2022

```python
# 1. Crear nueva versión SOA basada en ISO 27001:2022
nueva_soa = SOAVersion(
    version_number="SOA v2.0 (ISO 27001:2022)",
    description="Migración a ISO 27001:2022",
    is_active=True,
    based_on_version="ISO 27001:2022"
)
db.session.add(nueva_soa)
db.session.commit()

# 2. Importar controles de la nueva versión
# (usar script de importación)

# 3. Marcar versión anterior como inactiva (opcional)
version_anterior = SOAVersion.query.filter_by(
    version_number="SOA v1.0 (ISO 27001:2013)"
).first()
version_anterior.is_active = False
db.session.commit()
```

## Buenas Prácticas

### 1. **No eliminar versiones antiguas**
- Mantener historial para auditorías
- Usar `is_active = False` en lugar de eliminar

### 2. **Versionado semántico para SOA organizacional**
```
SOA v1.0 (ISO 27001:2013) - Primera versión
SOA v2.0 (ISO 27001:2022) - Migración a nueva norma
SOA v2.1 (ISO 27001:2022) - Ajustes menores
```

### 3. **Separar controles de referencia vs SOA organizacional**
- **Controles de referencia**: ISO 27001:2022 oficial (no modificar)
- **SOA organizacional**: Versión personalizada basada en la referencia

### 4. **Documentar cambios en `description`**
```python
version = SOAVersion(
    version_number="SOA v2.0 (ISO 27001:2022)",
    description="""
    Migración a ISO 27001:2022
    - Fecha: 2025-01-15
    - Motivo: Actualización normativa
    - Cambios: 93 controles (vs 114 anteriores)
    - Responsable: CISO
    """
)
```

## Gestión de Futuras Actualizaciones

### Cuando salga ISO 27001:202X

1. **Crear archivo CSV con nuevos controles**
   ```
   iso27001_202X_controls.csv
   ```

2. **Importar como nueva versión**
   ```bash
   # Modificar script para incluir nueva versión
   python3 scripts/import_iso27001_controls.py
   ```

3. **No afecta a organizaciones existentes**
   - Versiones anteriores siguen disponibles
   - Migración es opcional y controlada

4. **Permitir coexistencia temporal**
   - Facilita período de transición
   - Comparación lado a lado

## Preguntas Frecuentes

### ¿Qué pasa con las tareas existentes?

Las tareas tienen un campo `iso_control` (String) que es independiente de la tabla `soa_controls`. Ejemplo:
- Tarea template: `iso_control = "5.1"` (referencia textual)
- Tarea instanciada: puede vincularse a uno o más controles SOA específicos

### ¿Cómo saber qué versión usar?

```python
# Obtener versión activa más reciente
version_activa = SOAVersion.query.filter_by(
    is_active=True
).order_by(SOAVersion.created_at.desc()).first()
```

### ¿Puedo tener múltiples versiones activas?

Sí, es posible. Útil para:
- Organizaciones con múltiples unidades de negocio
- Proceso de migración gradual
- Comparación de versiones

## Archivos Relevantes

- `/iso27001_2022_controls_complete.csv` - Controles ISO 27001:2022
- `/scripts/import_iso27001_controls.py` - Script de importación
- `/app/models/soa.py` - Modelos SOAVersion y SOAControl
- `/migrations/` - Migraciones de base de datos

## Comandos Útiles

```bash
# Ver versiones en la base de datos
docker exec ismsmanager-db-1 psql -U isms -d isms_db -c \
  "SELECT version_number, is_active, created_at FROM soa_versions;"

# Contar controles por versión
docker exec ismsmanager-db-1 psql -U isms -d isms_db -c \
  "SELECT v.version_number, COUNT(c.id) as controles
   FROM soa_versions v
   LEFT JOIN soa_controls c ON v.id = c.soa_version_id
   GROUP BY v.version_number;"

# Importar controles ISO 27001:2022
docker exec ismsmanager-web-1 python3 scripts/import_iso27001_controls.py
```

## Conclusión

El sistema de versiones permite:
- ✅ **Futuro-proof**: Soporta futuras versiones ISO sin cambios de código
- ✅ **Flexibilidad**: Cada organización usa su versión
- ✅ **Historial**: Mantiene registro de cambios normativos
- ✅ **Migración gradual**: No fuerza actualizaciones inmediatas
- ✅ **Personalización**: Permite SOA específicos por organización

Este diseño asegura que el sistema permanezca útil y compatible con futuras actualizaciones de ISO 27001.
