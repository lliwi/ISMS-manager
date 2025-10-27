# Plantillas de Tareas Periódicas ISO/IEC 27001:2023

## 📋 Descripción

Este módulo proporciona un conjunto completo de plantillas de tareas periódicas recomendadas por la norma **ISO/IEC 27001:2023** para la gestión efectiva de un Sistema de Gestión de Seguridad de la Información (SGSI).

## 🎯 Objetivo

Facilitar el cumplimiento de los requisitos de seguimiento, medición y control operacional del SGSI mediante la implementación de tareas periódicas estructuradas y basadas en las mejores prácticas de la norma ISO 27001.

## 📦 Contenido

El sistema incluye **más de 30 plantillas de tareas** que cubren todos los aspectos del SGSI:

### Capítulo 5: Liderazgo
- ✅ Revisión anual de políticas de seguridad (Control A.5.1)
- ✅ Actualización de contactos con autoridades (Control A.5.5)

### Capítulo 6: Planificación
- ✅ Evaluación anual de riesgos (6.1.2 / 8.2)
- ✅ Revisión semestral del plan de tratamiento de riesgos (6.1.3 / 8.3)
- ✅ Revisión trimestral de objetivos de seguridad (6.2)

### Capítulo 7: Soporte
- ✅ Evaluación anual de competencias (7.2)
- ✅ Sesiones trimestrales de concienciación (7.3 / Control A.6.3)
- ✅ Revisión semestral de documentación del SGSI (7.5)

### Capítulo 8: Operación
- ✅ Revisión mensual de procedimientos operacionales (8.1 / Control A.5.37)

### Capítulo 9: Evaluación del Desempeño
- ✅ Revisión trimestral de indicadores de desempeño (9.1)
- ✅ Auditoría interna semestral (9.2)
- ✅ Revisión semestral por la dirección (9.3)

### Capítulo 10: Mejora
- ✅ Revisión trimestral de no conformidades y acciones correctivas (10.2)

### Anexo A: Controles de Seguridad

#### Controles Organizacionales
- ✅ Actualización mensual de inventario de activos (A.5.9)
- ✅ Revisión trimestral de derechos de acceso (A.5.18)
- ✅ Revisión semestral de proveedores (A.5.19/A.5.20)
- ✅ Revisión trimestral de gestión de incidentes (A.5.24-5.28)
- ✅ Prueba anual del plan de continuidad (A.5.29/A.5.30)
- ✅ Revisión anual de cumplimiento legal (A.5.31)
- ✅ Revisión independiente anual (A.5.35)

#### Controles de Personas
- ✅ Verificación anual de antecedentes (A.6.1)

#### Controles Físicos
- ✅ Revisión mensual de seguridad física (A.7.4)

#### Controles Tecnológicos
- ✅ Verificación mensual de protección contra malware (A.8.7)
- ✅ Escaneo mensual de vulnerabilidades (A.8.8)
- ✅ Verificación semanal de copias de seguridad (A.8.13)
- ✅ Pruebas trimestrales de restauración (A.8.13/A.8.14)
- ✅ Revisión semanal de registros de eventos (A.8.15/A.8.16)
- ✅ Revisión mensual de software instalado (A.8.19)
- ✅ Revisión quincenal de gestión de cambios (A.8.32)

## 🚀 Instalación

### Opción 1: Instalación en Nueva Implementación

Si estás realizando una nueva instalación del ISMS Manager, las plantillas se crearán automáticamente durante el primer arranque.

### Opción 2: Instalación Manual

Para instalar las plantillas en un sistema existente:

#### Desde dentro del contenedor Docker:

```bash
# Acceder al contenedor
docker exec -it isms-manager bash

# Ejecutar el script de instalación
./install_iso27001_tasks.sh

# O ejecutar directamente el script Python
python init_iso27001_tasks.py
```

#### Desde el host (usando docker exec):

```bash
# Ejecutar directamente
docker exec -it isms-manager python init_iso27001_tasks.py
```

## 📊 Características de las Plantillas

Cada plantilla de tarea incluye:

- **Título descriptivo** basado en el control ISO 27001
- **Descripción detallada** con alcance y objetivos
- **Categoría** según tipo de actividad
- **Frecuencia** recomendada (semanal, mensual, trimestral, semestral, anual)
- **Prioridad** según criticidad (baja, media, alta, crítica)
- **Referencia ISO 27001** (capítulo y control del Anexo A)
- **Estimación de horas** para planificación de recursos
- **Rol responsable predeterminado** (CISO, Admin, Auditor)
- **Días de notificación anticipada**
- **Lista de verificación (checklist)** con pasos a seguir
- **Requisitos de evidencia** según control
- **Requisitos de aprobación** según criticidad

## 🎯 Uso del Sistema

### 1. Acceso a Plantillas

Accede a las plantillas desde:
```
http://localhost/tareas/templates
```

### 2. Generación de Tareas

Desde cada plantilla puedes:
- Ver detalles completos
- Generar nueva tarea basada en la plantilla
- Activar/desactivar plantilla
- Modificar parámetros según necesidades

### 3. Gestión de Tareas

Las tareas generadas desde plantillas incluyen:
- Asignación automática al rol predeterminado
- Fecha de vencimiento calculada según frecuencia
- Checklist precargado
- Sistema de notificaciones automáticas
- Registro de evidencias
- Workflow de aprobación si es requerido

## ⚙️ Personalización

### Modificar Frecuencias

Puedes ajustar las frecuencias de las tareas según las necesidades específicas de tu organización:

1. Accede a la plantilla en `/tareas/templates`
2. Edita la plantilla
3. Cambia la frecuencia según tu política
4. Las nuevas tareas generadas usarán la nueva frecuencia

### Adaptar Checklists

Los checklists pueden personalizarse para reflejar tus procedimientos internos:

1. Edita la plantilla correspondiente
2. Modifica, añade o elimina ítems del checklist
3. Guarda los cambios

### Asignar Responsables

Por defecto, las tareas se asignan a roles (CISO, Admin, Auditor), pero puedes:

1. Modificar el rol predeterminado en la plantilla
2. Asignar usuarios específicos al generar cada tarea
3. Reasignar tareas existentes según necesidad

## 📈 Frecuencias Recomendadas por ISO 27001

La norma no especifica frecuencias exactas, pero las buenas prácticas establecen:

| Frecuencia | Actividades |
|------------|-------------|
| **Semanal** | Copias de seguridad, registros de eventos, monitorización |
| **Quincenal** | Gestión de cambios, revisiones operacionales |
| **Mensual** | Vulnerabilidades, inventarios, protección malware, seguridad física |
| **Trimestral** | Controles, objetivos, incidentes, accesos, formación, restauración |
| **Semestral** | Auditorías, revisión dirección, proveedores, documentación, riesgos |
| **Anual** | Políticas, riesgos completos, competencias, continuidad, legal, revisión independiente |

## 🔄 Ciclo de Mejora Continua

El sistema de tareas periódicas soporta el ciclo PDCA (Plan-Do-Check-Act):

1. **Plan**: Plantillas con objetivos y procedimientos claros
2. **Do**: Ejecución de tareas con checklists guiados
3. **Check**: Revisión de evidencias y resultados
4. **Act**: Lecciones aprendidas y mejoras en plantillas

## 📝 Documentación de Evidencias

Cada tarea puede incluir:
- Archivos adjuntos como evidencias
- Comentarios y observaciones
- Registro de tiempo invertido
- Resultados y hallazgos
- Aprobaciones cuando requerido

Todo queda registrado en el historial de auditoría del SGSI.

## 🔐 Control de Accesos

El sistema respeta los roles definidos en el SGSI:

- **Administrador del Sistema**: Acceso total
- **CISO / Responsable de Seguridad**: Todas las tareas de seguridad
- **Auditor Interno**: Tareas de auditoría + lectura de otras
- **Propietarios de Procesos**: Tareas de su ámbito
- **Usuarios Generales**: Consulta según permisos

## 🎓 Capacitación

Se recomienda:

1. Formar a los responsables en el uso del sistema de tareas
2. Explicar la importancia de cada tipo de tarea para el SGSI
3. Establecer procedimientos de escalado para tareas vencidas
4. Revisar periódicamente la eficacia del sistema

## 📊 Indicadores de Desempeño

El sistema permite medir:

- ✅ Porcentaje de tareas completadas a tiempo
- ⏰ Tiempo promedio de ejecución por tipo de tarea
- 📈 Tendencias en hallazgos por categoría
- 🎯 Cumplimiento de objetivos de seguridad
- 🔄 Eficacia de acciones correctivas

## 🆘 Soporte

Si necesitas ayuda:

1. Consulta la documentación completa en `/docs`
2. Revisa el CLAUDE.md del proyecto
3. Contacta con el equipo de desarrollo

## 📚 Referencias

- ISO/IEC 27001:2023 - Requisitos del SGSI
- ISO/IEC 27002:2022 - Código de buenas prácticas
- UNE-ISO/IEC 27001:2023 - Versión en español

## ⚖️ Licencia

Este módulo es parte del sistema ISMS Manager y está sujeto a su licencia.

---

**Fecha de última actualización**: Octubre 2025
**Versión**: 1.0
**Basado en**: ISO/IEC 27001:2023
