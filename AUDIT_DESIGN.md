# Diseño del Módulo de Gestión de Auditorías ISO 27001

## 📋 Requisitos Normativos

### ISO 27001:2022 - Cláusula 9.2 (Auditoría Interna)
- ✅ Auditorías a intervalos planificados
- ✅ Programa de auditoría definiendo frecuencia, métodos, responsabilidades y requisitos
- ✅ Criterios y alcance de auditoría establecidos
- ✅ Selección de auditores objetivos e imparciales
- ✅ Resultados reportados a dirección pertinente
- ✅ Conservación de información documentada
- ✅ Acciones correctivas sin demora indebida

### ISO 19011:2018 (Directrices para auditoría)
- Programa de auditoría
- Competencia de auditores
- Gestión de equipo auditor
- Preparación y conducción de auditorías
- Seguimiento de hallazgos

## 🗂️ Modelo de Datos

### 1. **AuditProgram** (Programa Anual de Auditorías)
```python
- id: Integer
- year: Integer (2025)
- title: String (Programa de Auditorías Internas 2025)
- description: Text
- status: Enum (draft, approved, in_progress, completed)
- scope: Text (alcance general del programa)
- objectives: Text (objetivos del programa)
- start_date: Date
- end_date: Date
- approved_by_id: FK(User) - Dirección que aprueba
- approval_date: Date
- created_by_id: FK(User)
- created_at, updated_at
```

### 2. **Audit** (Auditoría Individual) - AMPLIADO
```python
- id: Integer
- audit_code: String (AUD-2025-001)
- title: String
- audit_program_id: FK(AuditProgram) - NULL si es auditoría extraordinaria
- audit_type: Enum (internal_planned, internal_extraordinary, external_certification,
                     external_surveillance, management_review, supplier_audit)
- scope: Text (procesos, áreas, controles auditados)
- audit_criteria: Text (ISO 27001:2022, procedimientos internos, etc.)
- objectives: Text
- status: Enum (planned, notified, preparation, in_progress, reporting,
                 completed, closed, cancelled)
-
- # Fechas del ciclo de vida
- planned_date: Date
- notification_date: Date (cuándo se notificó al auditado)
- start_date: Date (inicio de auditoría en campo)
- end_date: Date (fin de auditoría)
- report_date: Date (fecha del informe)
- closure_date: Date (fecha de cierre tras verificar acciones)
-
- # Equipo auditor
- lead_auditor_id: FK(User)
- auditors: Relationship(AuditTeamMember)
-
- # Áreas/Procesos auditados
- audited_areas: Text (JSON array)
- audited_controls: Text (JSON array de códigos ISO)
-
- # Documentos
- audit_plan_file: String (ruta al plan de auditoría)
- audit_report_file: String (ruta al informe final)
- audit_report_document_id: FK(Document) - relación con gestión documental
- opening_meeting_notes: Text
- closing_meeting_notes: Text
-
- # Resultados
- conformity_percentage: Float (% de conformidad)
- total_findings: Integer
- major_findings_count: Integer
- minor_findings_count: Integer
- observations_count: Integer
- opportunities_count: Integer
-
- # Conclusiones
- overall_conclusion: Enum (conformant, conformant_with_observations,
                            non_conformant, not_applicable)
- conclusion_notes: Text
- recommendations: Text
-
- # Seguimiento
- requires_followup: Boolean
- followup_date: Date
-
- created_at, updated_at, created_by_id, updated_by_id
```

### 3. **AuditTeamMember** (Miembros del Equipo Auditor)
```python
- id: Integer
- audit_id: FK(Audit)
- user_id: FK(User)
- role: Enum (lead_auditor, auditor, technical_expert, observer)
- assigned_areas: Text (áreas específicas asignadas)
- is_independent: Boolean (verificar independencia)
- conflict_of_interest_declaration: Text
- created_at: DateTime
```

### 4. **AuditFinding** (Hallazgos de Auditoría)
```python
- id: Integer
- finding_code: String (HAL-2025-001-01)
- audit_id: FK(Audit)
- finding_type: Enum (major_nc, minor_nc, observation, opportunity_improvement)
- title: String
- description: Text (descripción detallada del hallazgo)
-
- # Referencia normativa
- affected_control: String (código control ISO, ej: "5.9")
- affected_clause: String (cláusula ISO, ej: "9.2")
- audit_criteria: String (criterio específico no cumplido)
-
- # Área afectada
- department: String
- process: String
- responsible_id: FK(User) - responsable del área auditada
-
- # Evidencia
- evidence: Text
- evidence_files: Text (JSON array de archivos)
-
- # Análisis
- root_cause: Text
- risk_level: Enum (low, medium, high, critical)
- potential_impact: Text
-
- # Estado
- status: Enum (open, action_plan_pending, action_plan_approved,
                 in_treatment, resolved, verified, closed, deferred)
-
- # Seguimiento
- corrective_action_id: FK(CorrectiveAction)
-
- created_at, updated_at, created_by_id
```

### 5. **CorrectiveAction** (Acciones Correctivas de Hallazgos)
```python
- id: Integer
- action_code: String (AC-2025-001)
- finding_id: FK(AuditFinding)
- action_type: Enum (immediate, corrective, preventive)
-
- # Planificación
- description: Text (descripción de la acción)
- implementation_plan: Text
- responsible_id: FK(User)
- verifier_id: FK(User) - quien verificará
-
- # Fechas
- planned_start_date: Date
- planned_completion_date: Date
- actual_completion_date: Date
- verification_date: Date
-
- # Estado
- status: Enum (planned, in_progress, completed, verified, rejected, cancelled)
-
- # Efectividad
- effectiveness_verified: Boolean
- effectiveness_notes: Text
- effectiveness_verification_date: Date
-
- # Recursos
- estimated_cost: Float
- actual_cost: Float
- resources_needed: Text
-
- # Seguimiento
- progress_percentage: Integer (0-100)
- progress_notes: Text
- blocking_issues: Text
-
- created_at, updated_at
```

### 6. **AuditChecklistTemplate** (Plantillas de Listas de Verificación)
```python
- id: Integer
- name: String
- description: Text
- audit_type: Enum (internal, external, specific_process)
- scope: String (ej: "ISO 27001 Anexo A completo", "Controles 5.x")
- items: Text (JSON array de ítems de verificación)
- is_active: Boolean
- version: String
- created_at, updated_at, created_by_id
```

### 7. **AuditChecklist** (Lista de Verificación de Auditoría)
```python
- id: Integer
- audit_id: FK(Audit)
- template_id: FK(AuditChecklistTemplate) - NULL si es personalizada
- auditor_id: FK(User)
- area: String
- items_data: Text (JSON con resultados de cada ítem)
- completion_percentage: Integer
- created_at, updated_at
```

### 8. **AuditEvidence** (Evidencias de Auditoría)
```python
- id: Integer
- audit_id: FK(Audit)
- finding_id: FK(AuditFinding) - NULL si es evidencia general
- evidence_type: Enum (document, record, interview, observation, screenshot, log)
- title: String
- description: Text
- file_path: String
- file_size: Integer
- collected_by_id: FK(User)
- collection_date: DateTime
- reference: String (referencia cruzada)
- notes: Text
- created_at: DateTime
```

### 9. **AuditDocument** (Documentos de Auditoría)
```python
- id: Integer
- audit_id: FK(Audit)
- document_type: Enum (audit_plan, audit_report, opening_meeting,
                       closing_meeting, checklist, evidence, other)
- title: String
- description: Text
- file_path: String (ruta al archivo físico)
- document_id: FK(Document) - relación con gestión documental del SGSI
- version: String
- uploaded_by_id: FK(User)
- upload_date: DateTime
- is_final: Boolean (si es versión definitiva)
- notes: Text
- created_at, updated_at
```

### 10. **AuditorQualification** (Calificación de Auditores)
```python
- id: Integer
- user_id: FK(User)
- qualification_type: Enum (lead_auditor, auditor, auditor_in_training, technical_expert)
- certification_body: String
- certification_number: String
- certification_date: Date
- expiry_date: Date
- scope: Text (alcance de competencia: ISO 27001, ISO 9001, etc.)
- training_hours: Integer
- audit_hours_completed: Integer (para mantener competencia)
- is_active: Boolean
- notes: Text
- created_at, updated_at
```

### 11. **AuditSchedule** (Cronograma de Auditorías)
```python
- id: Integer
- audit_program_id: FK(AuditProgram)
- area: String
- process: String
- frequency: Enum (annual, semiannual, quarterly, monthly, on_demand)
- last_audit_date: Date
- next_planned_date: Date
- responsible_area_id: FK(User)
- priority: Enum (high, medium, low)
- estimated_duration_hours: Integer
- notes: Text
- created_at, updated_at
```

### 12. **AuditMetrics** (Métricas y KPIs de Auditoría)
```python
- id: Integer
- audit_program_id: FK(AuditProgram) - NULL para métricas globales
- period: String (2025-Q1)
-
- # Métricas de ejecución
- planned_audits: Integer
- completed_audits: Integer
- cancelled_audits: Integer
- compliance_rate: Float (% de cumplimiento del programa)
-
- # Métricas de hallazgos
- total_findings: Integer
- major_nc: Integer
- minor_nc: Integer
- observations: Integer
-
- # Métricas de efectividad
- findings_closed_on_time: Integer
- findings_overdue: Integer
- average_closure_time_days: Float
- recurrent_findings: Integer
-
- # Métricas de recursos
- total_audit_hours: Float
- average_audit_duration: Float
-
- calculated_at: DateTime
- created_at: DateTime
```

## 🔄 Flujos de Trabajo

### **Ciclo de Vida de Auditoría**

```
1. PLANNED (Planificada)
   ↓ (Notificar al auditado)
2. NOTIFIED (Notificada)
   ↓ (Preparar documentación y checklist)
3. PREPARATION (Preparación)
   ↓ (Reunión de apertura e inicio de auditoría)
4. IN_PROGRESS (En progreso)
   ↓ (Recopilación de evidencias y hallazgos)
5. REPORTING (Elaboración de informe)
   ↓ (Revisión y aprobación del informe)
6. COMPLETED (Completada)
   ↓ (Seguimiento de acciones correctivas)
7. CLOSED (Cerrada - todas las acciones verificadas)
```

### **Ciclo de Vida de Hallazgo**

```
1. OPEN (Abierto)
   ↓ (Asignar responsable y solicitar plan de acción)
2. ACTION_PLAN_PENDING (Plan de acción pendiente)
   ↓ (Aprobar plan)
3. ACTION_PLAN_APPROVED (Plan aprobado)
   ↓ (Implementar acción)
4. IN_TREATMENT (En tratamiento)
   ↓ (Completar implementación)
5. RESOLVED (Resuelto - pendiente de verificación)
   ↓ (Verificar efectividad)
6. VERIFIED (Verificado - efectividad confirmada)
   ↓ (Cerrar formalmente)
7. CLOSED (Cerrado)
```

### **Ciclo de Acción Correctiva**

```
1. PLANNED (Planificada)
   ↓
2. IN_PROGRESS (En progreso)
   ↓
3. COMPLETED (Completada)
   ↓
4. VERIFIED (Verificada)
   ↓
   Si es efectiva → Cerrar hallazgo
   Si no es efectiva → Nuevo plan de acción
```

## ⚙️ Funcionalidades del Módulo

### **Gestión del Programa Anual**
- ✅ Crear programa anual de auditorías
- ✅ Definir frecuencia por área/proceso
- ✅ Calendario visual de auditorías
- ✅ Asignación de recursos (auditores)
- ✅ Seguimiento de cumplimiento del programa

### **Planificación de Auditorías**
- ✅ Crear auditoría (planificada o extraordinaria)
- ✅ Definir alcance, criterios y objetivos
- ✅ Seleccionar equipo auditor
- ✅ Verificar independencia de auditores
- ✅ Generar plan de auditoría
- ✅ Notificación automática a auditados

### **Ejecución de Auditorías**
- ✅ Listas de verificación (checklists) personalizables
- ✅ Registro de hallazgos en tiempo real
- ✅ Captura de evidencias (archivos, fotos, documentos)
- ✅ Actas de reunión (apertura/cierre)
- ✅ Registro de entrevistas

### **Gestión de Hallazgos**
- ✅ Clasificación (NC Mayor, NC Menor, Observación, Oportunidad de Mejora)
- ✅ Asignación de responsables
- ✅ Análisis de causa raíz
- ✅ Plan de acción correctiva
- ✅ Seguimiento y alertas de vencimiento
- ✅ Verificación de efectividad

### **Gestión Documental de Auditorías**
- ✅ Adjuntar plan de auditoría
- ✅ Adjuntar informe de auditoría (PDF, Word, etc.)
- ✅ Vincular documentos del SGSI
- ✅ Actas de reuniones (apertura/cierre)
- ✅ Listas de verificación completadas
- ✅ Evidencias fotográficas y documentales
- ✅ Control de versiones de documentos
- ✅ Archivo histórico de auditorías

### **Informes y Reportes**
- ✅ Generación automática de informe de auditoría
- ✅ Dashboard de métricas (KPIs)
- ✅ Gráficos de tendencias de hallazgos
- ✅ Reporte de cumplimiento del programa
- ✅ Análisis de recurrencia de hallazgos
- ✅ Informe ejecutivo para la dirección
- ✅ Exportación a PDF/Excel

### **Gestión de Auditores**
- ✅ Registro de calificaciones y certificaciones
- ✅ Control de competencias y vigencia
- ✅ Registro de horas de auditoría
- ✅ Evaluación de desempeño de auditores
- ✅ Detección de conflictos de interés

### **Integraciones**
- ✅ Vinculación con controles SOA
- ✅ Generación de No Conformidades
- ✅ Creación de tareas de seguimiento
- ✅ Relación con documentos del SGSI
- ✅ Notificaciones automáticas por email

## 📊 KPIs y Métricas Clave

### **Métricas de Programa**
- % de cumplimiento del programa anual
- Número de auditorías planificadas vs realizadas
- Auditorías completadas a tiempo

### **Métricas de Hallazgos**
- Total de hallazgos por tipo
- Tasa de hallazgos por auditoría
- Hallazgos recurrentes
- % de hallazgos cerrados en plazo
- Tiempo promedio de cierre

### **Métricas de Conformidad**
- % de conformidad global del SGSI
- Áreas/procesos con mayor no conformidad
- Evolución temporal de conformidad
- Controles ISO más deficientes

### **Métricas de Efectividad**
- % de acciones correctivas efectivas
- Tiempo promedio de implementación
- % de verificaciones exitosas
- Reincidencia de hallazgos

## 🎯 Mejores Prácticas Implementadas

### **ISO 19011:2018**
- ✅ Enfoque basado en riesgo para programación
- ✅ Competencia y evaluación de auditores
- ✅ Gestión del programa de auditoría
- ✅ Principios de auditoría (integridad, evidencia, independencia)

### **Ciclo PDCA**
- ✅ Plan: Programa anual y planificación
- ✅ Do: Ejecución de auditorías
- ✅ Check: Hallazgos y análisis
- ✅ Act: Acciones correctivas y mejora

### **Trazabilidad**
- ✅ Registro completo de evidencias
- ✅ Cadena de seguimiento de hallazgos
- ✅ Historial de cambios
- ✅ Auditoría de acciones (audit log)

### **Automatización**
- ✅ Cálculo automático de métricas
- ✅ Alertas de vencimientos
- ✅ Generación de informes
- ✅ Notificaciones a responsables

## 🔐 Control de Acceso (RBAC)

### **Roles y Permisos**

**Auditor Líder (Lead Auditor)**
- Crear y planificar auditorías
- Asignar equipo auditor
- Registrar hallazgos
- Emitir informes
- Verificar acciones correctivas

**Auditor Interno**
- Participar en auditorías asignadas
- Registrar evidencias
- Proponer hallazgos (requiere aprobación del líder)

**Responsable de Área (Auditado)**
- Ver auditorías de su área
- Responder a hallazgos
- Crear planes de acción
- Actualizar estado de acciones

**Responsable del SGSI / CISO**
- Aprobar programa de auditoría
- Ver todas las auditorías
- Aprobar planes de acción
- Verificar efectividad
- Acceso a todos los reportes

**Administrador del Sistema**
- Configurar plantillas
- Gestionar calificaciones de auditores
- Configurar métricas

## 📝 Información Documentada Requerida

### **Obligatoria ISO 27001**
- ✅ Programa de auditoría interna
- ✅ Planes de auditoría
- ✅ Informes de auditoría
- ✅ Evidencias de auditoría
- ✅ Planes de acción correctiva
- ✅ Verificación de efectividad

### **Recomendada**
- Calificaciones de auditores
- Listas de verificación
- Actas de reuniones de auditoría
- Análisis de tendencias
- Métricas del programa

## 🚀 Roadmap de Implementación

### **Fase 1: Funcionalidades Base** (MVP)
1. Modelo de datos completo
2. CRUD de auditorías
3. Gestión de hallazgos básica
4. Planes de acción correctiva
5. Reportes básicos
6. Adjuntar informe de auditoría

### **Fase 2: Funcionalidades Avanzadas**
1. Programa anual de auditorías
2. Listas de verificación dinámicas
3. Gestión de evidencias con archivos
4. Dashboard de métricas
5. Generación automática de informes

### **Fase 3: Optimización y Mejora**
1. Calificación de auditores
2. Análisis de recurrencia
3. Alertas y notificaciones automáticas
4. Integraciones con otros módulos
5. Exportación de reportes (PDF, Excel)

### **Fase 4: Inteligencia y Automatización**
1. Sugerencias de hallazgos basadas en IA
2. Predicción de riesgos de incumplimiento
3. Optimización automática del programa
4. Análisis de tendencias predictivo
