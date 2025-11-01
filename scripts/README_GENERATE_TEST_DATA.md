# Script de Generación de Datos de Prueba

Este script genera datos de prueba completos y realistas para el sistema ISMS Manager.

## 📋 Contenido Generado

El script crea los siguientes elementos:

### 1. **Documentos con Controles SOA** (5 documentos)
- Política de Seguridad de la Información
- Procedimientos de gestión de accesos e incidentes
- Instrucciones técnicas
- Registros de revisiones
- Cada documento está vinculado a controles SOA aplicables

### 2. **Activos y Servicios** (10 activos)
- **Hardware**: Servidores, firewalls, equipos de red
- **Software**: Aplicaciones (ERP), bases de datos
- **Información**: Datos de clientes, información financiera
- **Servicios**: Email (Microsoft 365), backup cloud, internet
- Incluye relaciones de dependencia entre activos

### 3. **Evaluación de Riesgos**
- Cálculo automático de riesgos basado en:
  - Niveles CIA (Confidencialidad, Integridad, Disponibilidad)
  - Valor de negocio del activo
  - Clasificación de información

### 4. **Incidentes de Seguridad** (4 incidentes)
- Intentos de acceso no autorizado
- Detección de malware
- Correos de phishing
- Fallos en servicios
- Con diferentes estados: nuevo, en progreso, resuelto, cerrado

### 5. **No Conformidades** (3 no conformidades)
- Detectadas en auditorías y autoevaluaciones
- Con análisis de causa raíz
- Acciones correctivas asociadas
- Diferentes niveles de severidad (mayor/menor)

### 6. **Solicitudes de Cambio** (4 cambios)
- Actualizaciones de sistemas operativos
- Implementación de MFA
- Cambios en firewall
- Renovación de certificados SSL
- Con planes de implementación y rollback

### 7. **Tareas Periódicas** (6 tareas)
- Revisión de accesos
- Verificación de backups
- Gestión de vulnerabilidades
- Actualización de inventarios
- Análisis de logs
- Capacitación en seguridad

### 8. **Programa de Auditorías** (1 programa + 4 auditorías)
- Programa anual de auditorías internas
- Auditorías trimestrales planificadas (Q1, Q2, Q3, Q4)
- Cronograma de auditorías por área
- Hallazgos y acciones correctivas

## 🚀 Cómo Ejecutar el Script

### Opción 1: Desde la carpeta scripts (recomendado)

```bash
cd /home/llibert/Documents/development/flask/ISMS\ Manager
python scripts/generate_test_data.py
```

### Opción 2: Como módulo de Python

```bash
cd /home/llibert/Documents/development/flask/ISMS\ Manager
python -m scripts.generate_test_data
```

### Opción 3: Ejecutar directamente (si está en el path)

```bash
cd /home/llibert/Documents/development/flask/ISMS\ Manager/scripts
./generate_test_data.py
```

## ⚙️ Requisitos Previos

Antes de ejecutar el script, asegúrate de:

1. **Tener el entorno virtual activado**:
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # o
   .venv\Scripts\activate  # Windows
   ```

2. **Tener la base de datos inicializada**:
   ```bash
   flask db upgrade
   ```

3. **Tener al menos un usuario admin creado**:
   - El script requiere un usuario 'admin' para asignar responsabilidades
   - Puedes crear uno manualmente o usar el script de inicialización

4. **Tener una versión SOA activa**:
   - El script asocia documentos a controles SOA
   - Ejecuta primero el script de importación de controles ISO 27001 si es necesario

5. **Tener roles creados**:
   - El script busca usuarios con diferentes roles
   - Roles requeridos: Administrador del Sistema, Responsable de Seguridad (CISO), Auditor Interno, Responsable de Proceso

## 📊 Salida del Script

El script mostrará en consola:

```
================================================================================
  GENERADOR DE DATOS DE PRUEBA - ISMS MANAGER
  ISO/IEC 27001:2022
================================================================================

📊 Iniciando generación de datos de prueba...

================================================================================
  GENERANDO DOCUMENTOS CON CONTROLES SOA
================================================================================

  ✓ Documento creado: Política de Seguridad de la Información (POL-001) - 3 controles SOA
  ✓ Documento creado: Procedimiento de Gestión de Accesos (PROC-001) - 3 controles SOA
  ...

✅ 5 documentos creados exitosamente

================================================================================
  GENERANDO ACTIVOS Y SERVICIOS
================================================================================

  ✓ Activo creado: Servidor de Aplicaciones Principal (SRV-001) - Valor: 8/10, Criticidad: 9/10
  ...

✅ 10 activos/servicios creados exitosamente

[...]

================================================================================
  ✅ PROCESO COMPLETADO EXITOSAMENTE
================================================================================

  Datos de prueba generados correctamente.
  Ahora puedes explorar el sistema con datos realistas.

  📍 Accede al sistema en: http://localhost:5000
  👤 Usuario: admin
  🔑 Contraseña: [tu contraseña de admin]
```

## 🔍 Verificación de Datos

Después de ejecutar el script, puedes verificar los datos creados:

1. **Documentos**: Ve a "Gestión Documental" → verás 5 documentos
2. **Activos**: Ve a "Gestión de Activos" → verás 10 activos con sus relaciones
3. **Incidentes**: Ve a "Gestión de Incidentes" → verás 4 incidentes
4. **No Conformidades**: Ve a "No Conformidades" → verás 3 NC con acciones
5. **Cambios**: Ve a "Gestión de Cambios" → verás 4 solicitudes de cambio
6. **Tareas**: Ve a "Tareas" → verás 6 tareas periódicas
7. **Auditorías**: Ve a "Auditorías" → verás el programa anual con 4 auditorías

## ⚠️ Notas Importantes

- **No ejecutes el script múltiples veces** sin limpiar la base de datos, ya que creará datos duplicados (el script detecta algunos duplicados por código único)
- El script **NO elimina datos existentes**, solo añade nuevos
- Los datos generados son **ficticios** pero realistas y coherentes con ISO 27001:2022
- Las fechas se generan de forma relativa a la fecha actual para mantener relevancia
- Los valores de criticidad y riesgo se calculan automáticamente según las fórmulas del sistema

## 🧹 Limpiar Datos de Prueba

Si quieres eliminar los datos de prueba y empezar de nuevo:

```bash
# Opción 1: Recrear la base de datos completa
flask db downgrade base
flask db upgrade

# Opción 2: Eliminar manualmente los datos desde la interfaz web
# (más seguro si ya tienes otros datos importantes)
```

## 🐛 Solución de Problemas

### Error: "No se encontró usuario admin"
**Solución**: Crea un usuario admin primero
```bash
python init_new_installation.py
```

### Error: "No se encontró versión SOA activa"
**Solución**: Importa los controles ISO 27001
```bash
python scripts/import_iso27001_controls.py
```

### Error: ImportError al importar modelos
**Solución**: Verifica que estés ejecutando desde la raíz del proyecto
```bash
cd /home/llibert/Documents/development/flask/ISMS\ Manager
python scripts/generate_test_data.py
```

### Error: Base de datos no inicializada
**Solución**: Ejecuta las migraciones
```bash
flask db upgrade
```

## 📖 Más Información

- Documentación del proyecto: `/docs`
- Guía de ISO 27001: Anexo A de la norma ISO/IEC 27001:2022
- Issues y soporte: Repositorio del proyecto

## 🎯 Casos de Uso

Este script es útil para:

1. **Desarrollo y pruebas**: Probar funcionalidades con datos realistas
2. **Demos**: Mostrar el sistema a clientes o stakeholders
3. **Capacitación**: Entrenar usuarios con datos de ejemplo
4. **Testing**: Verificar el rendimiento con volumen de datos
5. **QA**: Pruebas de integración y aceptación

---

**Autor**: Sistema ISMS Manager
**Versión**: 1.0
**Última actualización**: 2025-01-11
