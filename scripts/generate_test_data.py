#!/usr/bin/env python3
"""
Script para generar datos de prueba completos para el sistema ISMS Manager
Genera: Documentos, Controles SOA, Activos, Servicios, Evaluación de Riesgos,
        Incidentes, No Conformidades, Cambios, Tareas y Plan de Auditorías

Uso:
    python scripts/generate_test_data.py

    O desde la raíz del proyecto:
    python -m scripts.generate_test_data
"""

import sys
import os
from datetime import datetime, timedelta, date
import random

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import create_app
from models import (
    db, User, Role, SOAVersion, SOAControl, Document, DocumentType,
    Asset, AssetCategory, ClassificationLevel, CIALevel, AssetStatus, AssetRelationship, RelationshipType,
    Incident, IncidentCategory, IncidentSeverity, IncidentPriority,
    IncidentStatus, IncidentSource, DetectionMethod, IncidentAsset,
    IncidentTimeline, IncidentAction, ActionType, ActionStatus,
    NonConformity, NCOrigin, NCSeverity, NCStatus, RCAMethod, CorrectiveAction,
    NCActionType, NCActionStatus,
    Change, ChangeType, ChangeCategory, ChangePriority, ChangeStatus,
    RiskLevel, ChangeApproval, ApprovalLevel, ApprovalStatus,
    ChangeTask, ChangeAsset,
    Task, TaskFrequency, PeriodicTaskStatus, TaskPriority, TaskCategory
)
# Import enums and models not in main models.py
from app.models.change import TaskStatus
from app.models.audit import (
    AuditProgram, AuditRecord, AuditType, AuditStatus, AuditConclusion,
    AuditTeamMember, AuditorRole, AuditFinding, FindingType, FindingStatus,
    AuditSchedule, AuditFrequency, ProgramStatus
)


def print_section(title):
    """Imprime un separador de sección"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def get_users_by_role(role_name):
    """Obtiene usuarios por nombre de rol"""
    role = Role.query.filter_by(name=role_name).first()
    if role:
        return User.query.filter_by(role_id=role.id).all()
    return []


def generate_documents():
    """Genera documentos de ejemplo con controles SOA aplicados"""
    print_section("GENERANDO DOCUMENTOS CON CONTROLES SOA")

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    # Obtener controles SOA aplicables
    soa_version = SOAVersion.get_current_version()
    if not soa_version:
        print("⚠️  No se encontró versión SOA activa")
        return

    applicable_controls = SOAControl.query.filter_by(
        soa_version_id=soa_version.id,
        applicability_status='aplicable'
    ).limit(10).all()

    # Obtener tipos de documentos desde la base de datos
    doc_type_policy = DocumentType.query.filter_by(code='policy').first()
    doc_type_procedure = DocumentType.query.filter_by(code='procedure').first()
    doc_type_instruction = DocumentType.query.filter_by(code='instruction').first()
    doc_type_record = DocumentType.query.filter_by(code='record').first()

    if not doc_type_policy or not doc_type_procedure:
        print("⚠️  No se encontraron tipos de documentos. Ejecuta primero el script de inicialización.")
        return

    documents_data = [
        {
            'code': 'POL-001',
            'title': 'Política de Seguridad de la Información',
            'description': 'Política general de seguridad de la información de la organización',
            'type_id': doc_type_policy.id,
            'version': '2.0',
            'controls': applicable_controls[:3],
            'content': 'Esta política establece los lineamientos generales de seguridad...'
        },
        {
            'code': 'PROC-001',
            'title': 'Procedimiento de Gestión de Accesos',
            'description': 'Procedimiento para la gestión de altas, bajas y modificaciones de accesos',
            'type_id': doc_type_procedure.id,
            'version': '1.5',
            'controls': applicable_controls[2:5],
            'content': 'Objetivo: Definir el proceso para gestionar los accesos...'
        },
        {
            'code': 'PROC-002',
            'title': 'Procedimiento de Gestión de Incidentes de Seguridad',
            'description': 'Procedimiento para detección, respuesta y cierre de incidentes',
            'type_id': doc_type_procedure.id,
            'version': '1.0',
            'controls': applicable_controls[4:7],
            'content': 'Este procedimiento define cómo gestionar incidentes de seguridad...'
        },
        {
            'code': 'INST-001',
            'title': 'Instrucción de Configuración de Firewall',
            'description': 'Guía técnica para configuración segura de firewalls',
            'type_id': doc_type_instruction.id if doc_type_instruction else doc_type_procedure.id,
            'version': '1.2',
            'controls': applicable_controls[5:8],
            'content': 'Configuración paso a paso del firewall corporativo...'
        },
        {
            'code': 'REG-001',
            'title': 'Registro de Revisión de Accesos Q1-2025',
            'description': 'Registro de la revisión trimestral de accesos',
            'type_id': doc_type_record.id if doc_type_record else doc_type_procedure.id,
            'version': '1.0',
            'controls': applicable_controls[6:9],
            'content': 'Fecha de revisión: 15/01/2025...'
        }
    ]

    created_count = 0
    for doc_data in documents_data:
        existing = Document.query.filter_by(code=doc_data['code']).first()
        if existing:
            print(f"  ⚠️  Documento '{doc_data['code']}' ya existe, omitiendo...")
            continue

        doc = Document(
            code=doc_data['code'],
            title=doc_data['title'],
            description=doc_data['description'],
            document_type_id=doc_data['type_id'],
            version=doc_data['version'],
            status='approved',
            approval_date=datetime.utcnow() - timedelta(days=random.randint(30, 180)),
            next_review_date=datetime.utcnow() + timedelta(days=random.randint(180, 365)),
            content=doc_data['content'],
            created_by_id=admin.id,
            updated_by_id=admin.id
        )

        # Asociar controles SOA
        doc.related_controls.extend(doc_data['controls'])

        db.session.add(doc)
        created_count += 1
        print(f"  ✓ Documento creado: {doc_data['title']} ({doc_data['code']}) - {len(doc_data['controls'])} controles SOA")

    db.session.commit()
    print(f"\n✅ {created_count} documentos creados exitosamente")


def generate_assets_and_services():
    """Genera activos y servicios de ejemplo"""
    print_section("GENERANDO ACTIVOS Y SERVICIOS")

    admin = User.query.filter_by(username='admin').first()
    ciso_users = get_users_by_role('Responsable de Seguridad (CISO)')

    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    custodian = ciso_users[0] if ciso_users else admin

    assets_data = [
        # Hardware
        {
            'asset_code': 'SRV-001',
            'name': 'Servidor de Aplicaciones Principal',
            'description': 'Servidor que hospeda las aplicaciones críticas del negocio',
            'category': AssetCategory.HARDWARE,
            'classification': ClassificationLevel.CONFIDENTIAL,
            'confidentiality_level': CIALevel.HIGH,
            'integrity_level': CIALevel.HIGH,
            'availability_level': CIALevel.CRITICAL,
            'location': 'Centro de Datos Principal - Rack A3',
            'purchase_cost': 15000.0,
            'manufacturer': 'Dell',
            'model': 'PowerEdge R740'
        },
        {
            'asset_code': 'SRV-002',
            'name': 'Servidor de Base de Datos',
            'description': 'Servidor dedicado para bases de datos corporativas',
            'category': AssetCategory.HARDWARE,
            'classification': ClassificationLevel.RESTRICTED,
            'confidentiality_level': CIALevel.CRITICAL,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.CRITICAL,
            'location': 'Centro de Datos Principal - Rack A4',
            'purchase_cost': 18000.0,
            'manufacturer': 'HP',
            'model': 'ProLiant DL380'
        },
        {
            'asset_code': 'NET-001',
            'name': 'Firewall Principal',
            'description': 'Firewall de perímetro para protección de red',
            'category': AssetCategory.HARDWARE,
            'classification': ClassificationLevel.CONFIDENTIAL,
            'confidentiality_level': CIALevel.HIGH,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.CRITICAL,
            'location': 'Centro de Datos Principal - Rack B1',
            'purchase_cost': 8500.0,
            'manufacturer': 'Fortinet',
            'model': 'FortiGate 600E'
        },
        # Software
        {
            'asset_code': 'APP-001',
            'name': 'Sistema ERP Corporativo',
            'description': 'Sistema de planificación de recursos empresariales',
            'category': AssetCategory.SOFTWARE,
            'classification': ClassificationLevel.RESTRICTED,
            'confidentiality_level': CIALevel.CRITICAL,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.HIGH,
            'location': 'SRV-001',
            'purchase_cost': 50000.0,
            'manufacturer': 'SAP',
            'version': 'S/4HANA 2023'
        },
        {
            'asset_code': 'DB-001',
            'name': 'Base de Datos PostgreSQL Producción',
            'description': 'Base de datos principal de aplicaciones',
            'category': AssetCategory.SOFTWARE,
            'classification': ClassificationLevel.RESTRICTED,
            'confidentiality_level': CIALevel.CRITICAL,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.CRITICAL,
            'location': 'SRV-002',
            'purchase_cost': 0.0,
            'version': '15.3'
        },
        # Información
        {
            'asset_code': 'DATA-001',
            'name': 'Base de Datos de Clientes',
            'description': 'Información personal y comercial de clientes',
            'category': AssetCategory.INFORMATION,
            'classification': ClassificationLevel.RESTRICTED,
            'confidentiality_level': CIALevel.CRITICAL,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.HIGH,
            'location': 'DB-001',
            'current_value': 100000.0
        },
        {
            'asset_code': 'DATA-002',
            'name': 'Información Financiera Corporativa',
            'description': 'Estados financieros y datos contables',
            'category': AssetCategory.INFORMATION,
            'classification': ClassificationLevel.CONFIDENTIAL,
            'confidentiality_level': CIALevel.HIGH,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.HIGH,
            'location': 'APP-001',
            'current_value': 75000.0
        },
        # Servicios
        {
            'asset_code': 'SVC-001',
            'name': 'Servicio de Correo Electrónico (Microsoft 365)',
            'description': 'Servicio cloud de correo electrónico corporativo',
            'category': AssetCategory.SERVICES,
            'classification': ClassificationLevel.CONFIDENTIAL,
            'confidentiality_level': CIALevel.HIGH,
            'integrity_level': CIALevel.HIGH,
            'availability_level': CIALevel.HIGH,
            'location': 'Cloud - Microsoft Azure',
            'purchase_cost': 15000.0,
            'manufacturer': 'Microsoft'
        },
        {
            'asset_code': 'SVC-002',
            'name': 'Servicio de Backup Cloud',
            'description': 'Servicio de copias de seguridad en la nube',
            'category': AssetCategory.SERVICES,
            'classification': ClassificationLevel.CONFIDENTIAL,
            'confidentiality_level': CIALevel.HIGH,
            'integrity_level': CIALevel.CRITICAL,
            'availability_level': CIALevel.HIGH,
            'location': 'Cloud - AWS S3',
            'purchase_cost': 8000.0,
            'manufacturer': 'Amazon Web Services'
        },
        {
            'asset_code': 'SVC-003',
            'name': 'Conexión a Internet Principal',
            'description': 'Enlace de internet dedicado 1Gbps',
            'category': AssetCategory.SERVICES,
            'classification': ClassificationLevel.INTERNAL,
            'confidentiality_level': CIALevel.MEDIUM,
            'integrity_level': CIALevel.HIGH,
            'availability_level': CIALevel.CRITICAL,
            'location': 'ISP - Proveedor Principal',
            'purchase_cost': 12000.0
        }
    ]

    created_assets = []
    created_count = 0

    for asset_data in assets_data:
        existing = Asset.query.filter_by(asset_code=asset_data['asset_code']).first()
        if existing:
            print(f"  ⚠️  Activo '{asset_data['asset_code']}' ya existe, omitiendo...")
            created_assets.append(existing)
            continue

        asset = Asset(
            asset_code=asset_data['asset_code'],
            name=asset_data['name'],
            description=asset_data['description'],
            category=asset_data['category'],
            classification=asset_data['classification'],
            confidentiality_level=asset_data['confidentiality_level'],
            integrity_level=asset_data['integrity_level'],
            availability_level=asset_data['availability_level'],
            physical_location=asset_data['location'],
            purchase_cost=asset_data.get('purchase_cost', 0),
            current_value=asset_data.get('current_value', asset_data.get('purchase_cost', 0)),
            manufacturer=asset_data.get('manufacturer'),
            model=asset_data.get('model'),
            version=asset_data.get('version'),
            status=AssetStatus.ACTIVE,
            acquisition_date=datetime.utcnow() - timedelta(days=random.randint(365, 1095)),
            owner_id=admin.id,
            custodian_id=custodian.id,
            created_by_id=admin.id
        )

        # Calcular valores basados en CIA y clasificación
        # Valor de negocio (1-10) basado en clasificación y CIA
        classification_scores = {
            ClassificationLevel.PUBLIC: 2,
            ClassificationLevel.INTERNAL: 5,
            ClassificationLevel.CONFIDENTIAL: 8,
            ClassificationLevel.RESTRICTED: 10
        }
        cia_scores = {
            CIALevel.LOW: 2,
            CIALevel.MEDIUM: 5,
            CIALevel.HIGH: 8,
            CIALevel.CRITICAL: 10
        }

        classification_value = classification_scores.get(asset.classification, 5)
        cia_avg = (cia_scores.get(asset.confidentiality_level, 5) +
                   cia_scores.get(asset.integrity_level, 5) +
                   cia_scores.get(asset.availability_level, 5)) / 3

        asset.business_value = int((classification_value * 0.6) + (cia_avg * 0.4))
        asset.criticality = int(cia_scores.get(asset.availability_level, 5) * 0.5 +
                               cia_scores.get(asset.integrity_level, 5) * 0.3 +
                               cia_scores.get(asset.confidentiality_level, 5) * 0.2)

        db.session.add(asset)
        created_assets.append(asset)
        created_count += 1
        print(f"  ✓ Activo creado: {asset.name} ({asset.asset_code}) - Valor: {asset.business_value}/10, Criticidad: {asset.criticality}/10")

    db.session.commit()

    # Crear relaciones entre activos
    print("\n  Creando relaciones entre activos...")
    relationships_data = [
        ('APP-001', 'SRV-001', RelationshipType.DEPENDS_ON, 'La aplicación se ejecuta en este servidor'),
        ('APP-001', 'DB-001', RelationshipType.USES, 'La aplicación utiliza esta base de datos'),
        ('DB-001', 'SRV-002', RelationshipType.DEPENDS_ON, 'La base de datos está instalada en este servidor'),
        ('DATA-001', 'DB-001', RelationshipType.STORES, 'Los datos se almacenan en esta base de datos'),
        ('DATA-002', 'APP-001', RelationshipType.PROCESSES, 'La información es procesada por el ERP'),
        ('SRV-001', 'NET-001', RelationshipType.PROTECTS, 'El firewall protege el servidor'),
        ('SRV-002', 'NET-001', RelationshipType.PROTECTS, 'El firewall protege el servidor'),
        ('SVC-002', 'DATA-001', RelationshipType.STORES, 'Backup de datos de clientes'),
        ('SVC-002', 'DATA-002', RelationshipType.STORES, 'Backup de información financiera'),
    ]

    rel_count = 0
    for source_code, target_code, rel_type, description in relationships_data:
        source = Asset.query.filter_by(asset_code=source_code).first()
        target = Asset.query.filter_by(asset_code=target_code).first()

        if source and target:
            existing_rel = AssetRelationship.query.filter_by(
                source_asset_id=source.id,
                target_asset_id=target.id,
                relationship_type=rel_type
            ).first()

            if not existing_rel:
                relationship = AssetRelationship(
                    source_asset_id=source.id,
                    target_asset_id=target.id,
                    relationship_type=rel_type,
                    description=description,
                    criticality=random.randint(5, 9),
                    created_by_id=admin.id
                )
                db.session.add(relationship)
                rel_count += 1

    db.session.commit()
    print(f"  ✓ {rel_count} relaciones creadas")

    print(f"\n✅ {created_count} activos/servicios creados exitosamente")
    return created_assets


def generate_risk_assessment(assets):
    """Genera una evaluación de riesgos basada en los activos"""
    print_section("GENERANDO EVALUACIÓN DE RIESGOS")

    # Nota: Este sistema usa un modelo de riesgos integrado con los activos
    # Los riesgos se calculan automáticamente basados en CIA y valor de negocio

    print("  ℹ️  El sistema ISMS Manager calcula riesgos automáticamente basándose en:")
    print("     - Niveles CIA (Confidencialidad, Integridad, Disponibilidad)")
    print("     - Valor de negocio del activo")
    print("     - Clasificación de información")

    print("\n  Resumen de riesgos por activo:")
    for asset in assets[:5]:  # Mostrar solo los primeros 5
        # Calcular risk score simple basado en CIA y valor
        cia_scores = {
            CIALevel.LOW: 1,
            CIALevel.MEDIUM: 2,
            CIALevel.HIGH: 3,
            CIALevel.CRITICAL: 4
        }
        c_score = cia_scores.get(asset.confidentiality_level, 2)
        i_score = cia_scores.get(asset.integrity_level, 2)
        a_score = cia_scores.get(asset.availability_level, 2)
        risk_score = ((c_score + i_score + a_score) / 3) * (asset.business_value / 10)

        print(f"     {asset.asset_code}: {asset.name}")
        print(f"       Puntuación de riesgo: {risk_score:.2f}")
        print(f"       C:{asset.confidentiality_level.value} I:{asset.integrity_level.value} A:{asset.availability_level.value}")

    print(f"\n✅ Evaluación de riesgos disponible para {len(assets)} activos")


def generate_incidents(assets):
    """Genera incidentes de seguridad de ejemplo"""
    print_section("GENERANDO INCIDENTES DE SEGURIDAD")

    admin = User.query.filter_by(username='admin').first()
    ciso_users = get_users_by_role('Responsable de Seguridad (CISO)')

    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    assigned_user = ciso_users[0] if ciso_users else admin

    incidents_data = [
        {
            'title': 'Intento de acceso no autorizado al servidor de base de datos',
            'description': 'Se detectaron múltiples intentos fallidos de acceso SSH al servidor DB-001',
            'category': IncidentCategory.UNAUTHORIZED_ACCESS,
            'severity': IncidentSeverity.HIGH,
            'priority': IncidentPriority.HIGH,
            'detection_method': DetectionMethod.IDS_IPS,
            'source': IncidentSource.EXTERNAL,
            'affected_asset_codes': ['SRV-002', 'DB-001'],
            'days_ago': 5,
            'status': IncidentStatus.RESOLVED
        },
        {
            'title': 'Detección de malware en estación de trabajo',
            'description': 'El antivirus detectó y bloqueó un troyano en el equipo del departamento de finanzas',
            'category': IncidentCategory.MALWARE,
            'severity': IncidentSeverity.MEDIUM,
            'priority': IncidentPriority.NORMAL,
            'detection_method': DetectionMethod.ANTIVIRUS,
            'source': IncidentSource.EXTERNAL,
            'affected_asset_codes': ['DATA-002'],
            'days_ago': 10,
            'status': IncidentStatus.CLOSED
        },
        {
            'title': 'Correo de phishing dirigido a empleados',
            'description': 'Se recibió un correo suplantando la identidad del CEO solicitando transferencias',
            'category': IncidentCategory.PHISHING,
            'severity': IncidentSeverity.HIGH,
            'priority': IncidentPriority.HIGH,
            'detection_method': DetectionMethod.USER_REPORT,
            'source': IncidentSource.EXTERNAL,
            'affected_asset_codes': ['SVC-001'],
            'days_ago': 3,
            'status': IncidentStatus.IN_PROGRESS
        },
        {
            'title': 'Fallo en el servicio de backup programado',
            'description': 'El backup nocturno falló durante 2 días consecutivos sin alertas',
            'category': IncidentCategory.SYSTEM_FAILURE,
            'severity': IncidentSeverity.MEDIUM,
            'priority': IncidentPriority.HIGH,
            'detection_method': DetectionMethod.MONITORING,
            'source': IncidentSource.INTERNAL,
            'affected_asset_codes': ['SVC-002'],
            'days_ago': 2,
            'status': IncidentStatus.CONTAINED
        }
    ]

    created_count = 0
    for inc_data in incidents_data:
        incident_number = Incident.generate_incident_number()

        discovery_date = datetime.utcnow() - timedelta(days=inc_data['days_ago'])

        incident = Incident(
            incident_number=incident_number,
            title=inc_data['title'],
            description=inc_data['description'],
            category=inc_data['category'],
            severity=inc_data['severity'],
            priority=inc_data['priority'],
            status=inc_data['status'],
            discovery_date=discovery_date,
            reported_date=discovery_date + timedelta(hours=random.randint(1, 4)),
            detection_method=inc_data['detection_method'],
            source=inc_data['source'],
            impact_confidentiality=random.choice([True, False]),
            impact_integrity=random.choice([True, False]),
            impact_availability=inc_data['category'] == IncidentCategory.SYSTEM_FAILURE,
            reported_by_id=admin.id,
            assigned_to_id=assigned_user.id,
            created_by_id=admin.id
        )

        # Si está resuelto o cerrado, añadir fechas
        if inc_data['status'] in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            incident.containment_date = incident.reported_date + timedelta(hours=random.randint(2, 24))
            incident.resolution_date = incident.containment_date + timedelta(hours=random.randint(4, 48))
            incident.resolution = f"Se aplicaron medidas correctivas y se verificó la efectividad. El incidente fue resuelto satisfactoriamente."
            incident.lessons_learned = "Reforzar controles de monitorización y respuesta ante incidentes similares."

            if inc_data['status'] == IncidentStatus.CLOSED:
                incident.closure_date = incident.resolution_date + timedelta(days=random.randint(1, 3))

        db.session.add(incident)
        db.session.flush()  # Para obtener el ID

        # Asociar activos afectados
        for asset_code in inc_data['affected_asset_codes']:
            asset = Asset.query.filter_by(asset_code=asset_code).first()
            if asset:
                inc_asset = IncidentAsset(
                    incident_id=incident.id,
                    asset_id=asset.id,
                    impact_description=f"Activo {asset.name} fue afectado por el incidente"
                )
                db.session.add(inc_asset)

        # Crear entrada en timeline
        timeline = IncidentTimeline(
            incident_id=incident.id,
            timestamp=incident.reported_date,
            action_type=ActionType.CREATED,
            description=f"Incidente creado y reportado",
            user_id=admin.id
        )
        db.session.add(timeline)

        # Añadir acción correctiva si está en progreso o resuelto
        if inc_data['status'] in [IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            action = IncidentAction(
                incident_id=incident.id,
                action_type='Correctiva',
                description=f"Implementar medidas para prevenir recurrencia del incidente",
                responsible_id=assigned_user.id,
                status=ActionStatus.COMPLETED if inc_data['status'] in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED] else ActionStatus.IN_PROGRESS,
                due_date=date.today() + timedelta(days=30),
                completion_date=date.today() - timedelta(days=5) if inc_data['status'] in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED] else None
            )
            db.session.add(action)

        created_count += 1
        print(f"  ✓ Incidente creado: {incident.incident_number} - {inc_data['title'][:60]}...")

    db.session.commit()
    print(f"\n✅ {created_count} incidentes creados exitosamente")


def generate_nonconformities(assets):
    """Genera no conformidades de ejemplo"""
    print_section("GENERANDO NO CONFORMIDADES")

    admin = User.query.filter_by(username='admin').first()
    process_owners = get_users_by_role('Responsable de Proceso')

    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    responsible = process_owners[0] if process_owners else admin

    nonconformities_data = [
        {
            'title': 'Falta de revisión periódica de accesos de usuarios',
            'description': 'Durante la auditoría interna se detectó que no se ha realizado la revisión trimestral de accesos de usuarios en los últimos 6 meses',
            'origin': NCOrigin.INTERNAL_AUDIT,
            'severity': NCSeverity.MAJOR,
            'affected_controls': ['5.18', '5.15'],
            'days_ago': 15,
            'status': NCStatus.IMPLEMENTING
        },
        {
            'title': 'Política de escritorio limpio no implementada',
            'description': 'Se observó documentación confidencial sin protección en varias estaciones de trabajo',
            'origin': NCOrigin.INTERNAL_AUDIT,
            'severity': NCSeverity.MINOR,
            'affected_controls': ['5.10', '5.12'],
            'days_ago': 20,
            'status': NCStatus.CLOSED
        },
        {
            'title': 'Configuración de firewall no documentada',
            'description': 'Las reglas del firewall principal no están documentadas correctamente según el estándar',
            'origin': NCOrigin.SELF_ASSESSMENT,
            'severity': NCSeverity.MINOR,
            'affected_controls': ['8.20', '8.22'],
            'days_ago': 8,
            'status': NCStatus.ACTION_PLAN
        }
    ]

    created_count = 0
    for nc_data in nonconformities_data:
        nc_number = NonConformity.generate_nc_number()

        detection_date = datetime.utcnow() - timedelta(days=nc_data['days_ago'])

        nc = NonConformity(
            nc_number=nc_number,
            title=nc_data['title'],
            description=nc_data['description'],
            origin=nc_data['origin'],
            severity=nc_data['severity'],
            status=nc_data['status'],
            detection_date=detection_date,
            reported_date=detection_date,
            affected_controls=nc_data['affected_controls'],
            target_closure_date=date.today() + timedelta(days=random.randint(30, 90)),
            reported_by_id=admin.id,
            responsible_id=responsible.id,
            created_by_id=admin.id
        )

        # Si tiene análisis de causa raíz
        if nc_data['status'] in [NCStatus.IMPLEMENTING, NCStatus.CLOSED]:
            nc.rca_method = RCAMethod.FIVE_WHYS
            nc.root_cause_analysis = "Se identificó falta de procedimiento documentado y ausencia de recordatorios automáticos"
            nc.root_causes = ["Falta de procedimiento", "Ausencia de automatización"]
            nc.analysis_start_date = detection_date + timedelta(days=2)
            nc.action_plan_date = detection_date + timedelta(days=5)

        # Si está cerrada
        if nc_data['status'] == NCStatus.CLOSED:
            nc.closure_date = detection_date + timedelta(days=random.randint(20, 40))
            nc.is_effective = True
            nc.effectiveness_verification = "Se verificó la implementación de las acciones correctivas y su efectividad"

        db.session.add(nc)
        db.session.flush()

        # Añadir acción correctiva
        if nc_data['status'] in [NCStatus.ACTION_PLAN, NCStatus.IMPLEMENTING, NCStatus.CLOSED]:
            action = CorrectiveAction(
                nonconformity_id=nc.id,
                action_type=NCActionType.CORRECTIVE,
                description=f"Implementar procedimiento documentado para {nc_data['title'].lower()}",
                implementation_plan="1. Crear procedimiento\n2. Aprobar con dirección\n3. Capacitar al personal\n4. Implementar controles",
                responsible_id=responsible.id,
                status=NCActionStatus.VERIFIED if nc_data['status'] == NCStatus.CLOSED else NCActionStatus.IN_PROGRESS,
                due_date=date.today() + timedelta(days=random.randint(20, 60)),
                completion_date=date.today() - timedelta(days=5) if nc_data['status'] == NCStatus.CLOSED else None,
                is_effective=True if nc_data['status'] == NCStatus.CLOSED else None,
                priority=2 if nc_data['severity'] == NCSeverity.MAJOR else 3
            )
            db.session.add(action)

        created_count += 1
        print(f"  ✓ No conformidad creada: {nc.nc_number} - {nc_data['title'][:60]}...")

    db.session.commit()
    print(f"\n✅ {created_count} no conformidades creadas exitosamente")


def generate_changes(assets):
    """Genera solicitudes de cambio de ejemplo"""
    print_section("GENERANDO SOLICITUDES DE CAMBIO")

    admin = User.query.filter_by(username='admin').first()
    ciso_users = get_users_by_role('Responsable de Seguridad (CISO)')

    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    owner_user = ciso_users[0] if ciso_users else admin

    changes_data = [
        {
            'title': 'Actualización del sistema operativo de servidores de producción',
            'description': 'Actualizar servidores de Windows Server 2019 a Windows Server 2022',
            'change_type': ChangeType.INFRASTRUCTURE,
            'category': ChangeCategory.MAJOR,
            'priority': ChangePriority.HIGH,
            'affected_asset_codes': ['SRV-001', 'SRV-002'],
            'days_ahead': 15,
            'status': ChangeStatus.APPROVED
        },
        {
            'title': 'Implementación de autenticación multifactor (MFA)',
            'description': 'Desplegar MFA para todos los usuarios con acceso a sistemas críticos',
            'change_type': ChangeType.SECURITY,
            'category': ChangeCategory.MAJOR,
            'priority': ChangePriority.CRITICAL,
            'affected_asset_codes': ['APP-001', 'SVC-001'],
            'days_ahead': 30,
            'status': ChangeStatus.SCHEDULED
        },
        {
            'title': 'Configuración de reglas de firewall para nuevo servicio',
            'description': 'Abrir puerto 8443 para nueva aplicación web',
            'change_type': ChangeType.NETWORK,
            'category': ChangeCategory.STANDARD,
            'priority': ChangePriority.MEDIUM,
            'affected_asset_codes': ['NET-001'],
            'days_ahead': 7,
            'status': ChangeStatus.IN_PROGRESS
        },
        {
            'title': 'Actualización de certificados SSL',
            'description': 'Renovación de certificados SSL que vencen el próximo mes',
            'change_type': ChangeType.SECURITY,
            'category': ChangeCategory.STANDARD,
            'priority': ChangePriority.HIGH,
            'affected_asset_codes': ['APP-001'],
            'days_ahead': 20,
            'status': ChangeStatus.APPROVED
        }
    ]

    created_count = 0
    for change_data in changes_data:
        change_code = Change.generate_change_code()

        requested_date = datetime.utcnow() - timedelta(days=random.randint(5, 15))
        scheduled_start = datetime.utcnow() + timedelta(days=change_data['days_ahead'])

        change = Change(
            change_code=change_code,
            title=change_data['title'],
            description=change_data['description'],
            change_type=change_data['change_type'],
            category=change_data['category'],
            priority=change_data['priority'],
            status=change_data['status'],
            requested_date=requested_date,
            scheduled_start_date=scheduled_start,
            scheduled_end_date=scheduled_start + timedelta(hours=random.randint(2, 8)),
            estimated_duration=random.randint(2, 8),
            downtime_required=change_data['category'] == ChangeCategory.MAJOR,
            estimated_downtime_minutes=random.randint(30, 240) if change_data['category'] == ChangeCategory.MAJOR else 0,
            requester_id=admin.id,
            owner_id=owner_user.id,
            business_justification=f"Necesario para mejorar la seguridad y el rendimiento del sistema",
            implementation_plan=f"1. Backup del sistema\n2. Implementar cambios\n3. Pruebas\n4. Verificación",
            rollback_plan=f"1. Detener servicios\n2. Restaurar backup\n3. Reiniciar servicios\n4. Verificar funcionamiento",
            risk_assessment="Se ha evaluado el impacto y se han identificado los riesgos asociados",
            risk_level=RiskLevel.MEDIUM,
            impact_availability=change_data['category'] == ChangeCategory.MAJOR,
            affects_production=True,
            approval_required=change_data['category'] in [ChangeCategory.MAJOR, ChangeCategory.EMERGENCY],
            affected_controls=['8.32', '6.3', '8.31'],
            estimated_cost=random.randint(1000, 10000),
            created_by_id=admin.id
        )

        db.session.add(change)
        db.session.flush()

        # Asociar activos afectados
        for asset_code in change_data['affected_asset_codes']:
            asset = Asset.query.filter_by(asset_code=asset_code).first()
            if asset:
                change_asset = ChangeAsset(
                    change_id=change.id,
                    asset_id=asset.id,
                    impact_description=f"Activo {asset.name} será afectado durante el cambio"
                )
                db.session.add(change_asset)

        # Añadir aprobación si es necesaria y está aprobado
        if change_data['status'] in [ChangeStatus.APPROVED, ChangeStatus.SCHEDULED] and change.approval_required:
            approval = ChangeApproval(
                change_id=change.id,
                approval_level=ApprovalLevel.CAB,
                approver_id=owner_user.id,
                status=ApprovalStatus.APPROVED,
                comments="Cambio aprobado por el CAB",
                approved_date=requested_date + timedelta(days=random.randint(1, 3))
            )
            db.session.add(approval)

        # Añadir tareas de implementación
        tasks_data = [
            ('Realizar backup completo del sistema', 1),
            ('Implementar los cambios según plan', 2),
            ('Ejecutar pruebas de verificación', 3),
            ('Documentar cambios realizados', 4)
        ]

        for task_title, order in tasks_data:
            task = ChangeTask(
                change_id=change.id,
                title=task_title,
                description=f"Tarea requerida para completar el cambio: {task_title}",
                order=order,
                assigned_to_id=owner_user.id,
                status=TaskStatus.PENDING,
                estimated_duration=random.randint(30, 120)
            )
            db.session.add(task)

        created_count += 1
        print(f"  ✓ Cambio creado: {change.change_code} - {change_data['title'][:60]}...")

    db.session.commit()
    print(f"\n✅ {created_count} cambios creados exitosamente")


def generate_tasks():
    """Genera tareas periódicas de ejemplo"""
    print_section("GENERANDO TAREAS PERIÓDICAS")

    admin = User.query.filter_by(username='admin').first()
    ciso_users = get_users_by_role('Responsable de Seguridad (CISO)')

    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    assigned_user = ciso_users[0] if ciso_users else admin

    tasks_data = [
        {
            'title': 'Revisión trimestral de accesos de usuarios',
            'description': 'Revisar y validar que los accesos de usuarios sean apropiados',
            'category': TaskCategory.REVISION_ACCESOS,
            'priority': TaskPriority.ALTA,
            'due_days': 15,
            'status': PeriodicTaskStatus.PENDIENTE,
            'iso_control': '5.18'
        },
        {
            'title': 'Verificación mensual de backups',
            'description': 'Verificar que las copias de seguridad se ejecuten correctamente',
            'category': TaskCategory.COPIAS_SEGURIDAD,
            'priority': TaskPriority.CRITICA,
            'due_days': 7,
            'status': PeriodicTaskStatus.EN_PROGRESO,
            'iso_control': '8.13'
        },
        {
            'title': 'Revisión de vulnerabilidades del mes',
            'description': 'Analizar y gestionar vulnerabilidades detectadas en escaneos',
            'category': TaskCategory.GESTION_VULNERABILIDADES,
            'priority': TaskPriority.ALTA,
            'due_days': 10,
            'status': PeriodicTaskStatus.PENDIENTE,
            'iso_control': '8.8'
        },
        {
            'title': 'Actualización del inventario de activos',
            'description': 'Revisar y actualizar el inventario de activos de información',
            'category': TaskCategory.ACTUALIZACION_INVENTARIOS,
            'priority': TaskPriority.MEDIA,
            'due_days': 30,
            'status': PeriodicTaskStatus.PENDIENTE,
            'iso_control': '5.9'
        },
        {
            'title': 'Revisión de logs de seguridad',
            'description': 'Analizar logs de seguridad en busca de eventos anómalos',
            'category': TaskCategory.REVISION_CONTROLES,
            'priority': TaskPriority.ALTA,
            'due_days': 3,
            'status': PeriodicTaskStatus.VENCIDA,
            'iso_control': '8.15'
        },
        {
            'title': 'Capacitación de concienciación en seguridad Q1-2025',
            'description': 'Sesión trimestral de formación en seguridad de la información',
            'category': TaskCategory.FORMACION_CONCIENCIACION,
            'priority': TaskPriority.ALTA,
            'due_days': 45,
            'status': PeriodicTaskStatus.PENDIENTE,
            'iso_control': '6.3'
        }
    ]

    created_count = 0
    for task_data in tasks_data:
        due_date = datetime.utcnow() + timedelta(days=task_data['due_days'])

        # Ajustar fecha si está vencida
        if task_data['status'] == PeriodicTaskStatus.VENCIDA:
            due_date = datetime.utcnow() - timedelta(days=random.randint(1, 5))

        task = Task(
            title=task_data['title'],
            description=task_data['description'],
            category=task_data['category'],
            status=task_data['status'],
            priority=task_data['priority'],
            due_date=due_date,
            iso_control=task_data['iso_control'],
            estimated_hours=random.randint(1, 4),
            progress=50 if task_data['status'] == PeriodicTaskStatus.EN_PROGRESO else 0,
            assigned_to_id=assigned_user.id,
            created_by_id=admin.id
        )

        db.session.add(task)
        created_count += 1

        status_icon = "⏳" if task_data['status'] == PeriodicTaskStatus.PENDIENTE else "🔄" if task_data['status'] == PeriodicTaskStatus.EN_PROGRESO else "⚠️"
        print(f"  {status_icon} Tarea creada: {task_data['title'][:60]}... (vence: {due_date.strftime('%Y-%m-%d')})")

    db.session.commit()
    print(f"\n✅ {created_count} tareas creadas exitosamente")


def generate_audit_program():
    """Genera un programa de auditorías con auditorías planificadas"""
    print_section("GENERANDO PROGRAMA DE AUDITORÍAS")

    admin = User.query.filter_by(username='admin').first()
    auditor_users = get_users_by_role('Auditor Interno')

    if not admin:
        print("⚠️  No se encontró usuario admin")
        return

    lead_auditor = auditor_users[0] if auditor_users else admin

    # Crear programa de auditorías
    current_year = datetime.utcnow().year
    program = AuditProgram(
        year=current_year,
        title=f'Programa de Auditorías Internas {current_year}',
        description=f'Programa anual de auditorías internas del SGSI para el año {current_year}',
        status=ProgramStatus.APPROVED,
        scope='Alcance completo del SGSI: todos los procesos, controles y áreas',
        objectives='1. Verificar conformidad con ISO 27001:2022\n2. Evaluar eficacia de controles\n3. Identificar oportunidades de mejora',
        start_date=date(current_year, 1, 1),
        end_date=date(current_year, 12, 31),
        approved_by_id=admin.id,
        approval_date=date(current_year, 1, 15),
        created_by_id=admin.id
    )

    db.session.add(program)
    db.session.flush()

    print(f"  ✓ Programa de auditorías creado: {program.title}")

    # Crear auditorías planificadas
    audits_data = [
        {
            'title': 'Auditoría Interna Q1 - Controles de Acceso',
            'type': AuditType.INTERNAL_PLANNED,
            'scope': 'Controles de gestión de accesos (Anexo A: 5.15, 5.16, 5.17, 5.18)',
            'areas': 'TI, Sistemas, Recursos Humanos',
            'controls': '5.15, 5.16, 5.17, 5.18',
            'planned_date': date(current_year, 3, 15),
            'status': AuditStatus.COMPLETED,
            'conclusion': AuditConclusion.CONFORMANT_WITH_OBSERVATIONS
        },
        {
            'title': 'Auditoría Interna Q2 - Seguridad de Operaciones',
            'type': AuditType.INTERNAL_PLANNED,
            'scope': 'Controles operacionales de seguridad (Anexo A: 8.1-8.34)',
            'areas': 'Centro de Datos, Operaciones TI, Redes',
            'controls': '8.1, 8.5, 8.8, 8.13, 8.15, 8.20, 8.22, 8.32',
            'planned_date': date(current_year, 6, 20),
            'status': AuditStatus.NOTIFIED,
            'conclusion': None
        },
        {
            'title': 'Auditoría Interna Q3 - Protección de Información',
            'type': AuditType.INTERNAL_PLANNED,
            'scope': 'Controles de protección de información y activos (Anexo A: 5.9-5.14)',
            'areas': 'Todas las áreas con activos de información',
            'controls': '5.9, 5.10, 5.12, 5.13, 5.14',
            'planned_date': date(current_year, 9, 10),
            'status': AuditStatus.PLANNED,
            'conclusion': None
        },
        {
            'title': 'Auditoría Interna Q4 - Gestión de Incidentes y Continuidad',
            'type': AuditType.INTERNAL_PLANNED,
            'scope': 'Gestión de incidentes y continuidad del negocio (Anexo A: 5.24-5.30)',
            'areas': 'CSIRT, Gestión de Incidentes, Continuidad de Negocio',
            'controls': '5.24, 5.25, 5.26, 5.27, 5.29, 5.30',
            'planned_date': date(current_year, 12, 5),
            'status': AuditStatus.PLANNED,
            'conclusion': None
        }
    ]

    created_audits = 0
    for audit_data in audits_data:
        audit_code = AuditRecord.generate_audit_code()

        audit = AuditRecord(
            audit_code=audit_code,
            title=audit_data['title'],
            audit_program_id=program.id,
            audit_type=audit_data['type'],
            status=audit_data['status'],
            scope=audit_data['scope'],
            audit_criteria='ISO/IEC 27001:2022 - Anexo A',
            objectives='Verificar conformidad y eficacia de los controles implementados',
            planned_date=audit_data['planned_date'],
            audited_areas=audit_data['areas'],
            audited_controls=audit_data['controls'],
            lead_auditor_id=lead_auditor.id,
            overall_conclusion=audit_data['conclusion'],
            created_by_id=admin.id
        )

        # Si está completada, añadir información adicional
        if audit_data['status'] == AuditStatus.COMPLETED:
            audit.start_date = audit_data['planned_date']
            audit.end_date = audit_data['planned_date'] + timedelta(days=3)
            audit.report_date = audit_data['planned_date'] + timedelta(days=7)
            audit.opening_meeting_notes = "Reunión de apertura realizada. Se presentó alcance y objetivos."
            audit.closing_meeting_notes = "Reunión de cierre realizada. Se presentaron hallazgos y conclusiones."
            audit.major_findings_count = 0
            audit.minor_findings_count = 2
            audit.observations_count = 3
            audit.total_findings = 5
            audit.conformity_percentage = 95.0
            audit.conclusion_notes = "El área auditada cumple sustancialmente con los requisitos. Se identificaron oportunidades de mejora."
            audit.recommendations = "1. Mejorar documentación de procedimientos\n2. Reforzar capacitación del personal\n3. Implementar recordatorios automáticos"

        db.session.add(audit)
        db.session.flush()

        # Añadir miembro del equipo auditor
        team_member = AuditTeamMember(
            audit_id=audit.id,
            user_id=lead_auditor.id,
            role=AuditorRole.LEAD_AUDITOR,
            assigned_areas=audit_data['areas'],
            is_independent=True
        )
        db.session.add(team_member)

        # Añadir hallazgos si está completada
        if audit_data['status'] == AuditStatus.COMPLETED:
            findings_data = [
                {
                    'type': FindingType.MINOR_NC,
                    'title': 'Revisión de accesos no documentada',
                    'description': 'No se encontró evidencia de revisión de accesos en los últimos 3 meses',
                    'control': '5.18'
                },
                {
                    'type': FindingType.MINOR_NC,
                    'title': 'Política de escritorio limpio no implementada completamente',
                    'description': 'Se observaron documentos confidenciales sin protección en 2 estaciones',
                    'control': '5.10'
                },
                {
                    'type': FindingType.OBSERVATION,
                    'title': 'Procedimiento de gestión de contraseñas desactualizado',
                    'description': 'El procedimiento no incluye requisitos de complejidad actuales',
                    'control': '5.17'
                }
            ]

            for finding_data in findings_data:
                finding_code = AuditFinding.generate_finding_code(audit.audit_code)

                finding = AuditFinding(
                    finding_code=finding_code,
                    audit_id=audit.id,
                    finding_type=finding_data['type'],
                    title=finding_data['title'],
                    description=finding_data['description'],
                    affected_control=finding_data['control'],
                    affected_clause='Anexo A',
                    audit_criteria='ISO/IEC 27001:2022',
                    evidence='Observación directa y revisión documental',
                    risk_level='medium' if finding_data['type'] == FindingType.MINOR_NC else 'low',
                    status=FindingStatus.OPEN,
                    responsible_id=admin.id,
                    created_by_id=lead_auditor.id
                )
                db.session.add(finding)

        created_audits += 1
        print(f"  ✓ Auditoría creada: {audit.audit_code} - {audit_data['title']}")

    # Crear cronograma de auditorías
    schedule_areas = [
        ('Seguridad Física', AuditFrequency.SEMIANNUAL, 'high'),
        ('Gestión de Activos', AuditFrequency.ANNUAL, 'medium'),
        ('Criptografía', AuditFrequency.ANNUAL, 'medium'),
        ('Seguridad en Recursos Humanos', AuditFrequency.ANNUAL, 'medium'),
        ('Seguridad en Comunicaciones', AuditFrequency.SEMIANNUAL, 'high'),
    ]

    for area, frequency, priority in schedule_areas:
        schedule = AuditSchedule(
            audit_program_id=program.id,
            area=area,
            frequency=frequency,
            next_planned_date=date(current_year, random.randint(1, 12), random.randint(1, 28)),
            priority=priority,
            estimated_duration_hours=random.randint(8, 24),
            responsible_area_id=admin.id
        )
        db.session.add(schedule)

    db.session.commit()
    print(f"\n✅ Programa de auditorías creado con {created_audits} auditorías planificadas")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  GENERADOR DE DATOS DE PRUEBA - ISMS MANAGER")
    print("  ISO/IEC 27001:2022")
    print("=" * 80)

    app = create_app()

    with app.app_context():
        print("\n📊 Iniciando generación de datos de prueba...\n")

        try:
            # 1. Generar documentos con controles SOA
            generate_documents()

            # 2. Generar activos y servicios
            assets = generate_assets_and_services()

            # 3. Generar evaluación de riesgos (basada en activos)
            if assets:
                generate_risk_assessment(assets)

            # 4. Generar incidentes
            if assets:
                generate_incidents(assets)

            # 5. Generar no conformidades
            if assets:
                generate_nonconformities(assets)

            # 6. Generar cambios
            if assets:
                generate_changes(assets)

            # 7. Generar tareas periódicas
            generate_tasks()

            # 8. Generar programa de auditorías con auditorías
            generate_audit_program()

            print_section("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("\n  Datos de prueba generados correctamente.")
            print("  Ahora puedes explorar el sistema con datos realistas.\n")
            print("  📍 Accede al sistema en: http://localhost:5000")
            print("  👤 Usuario: admin")
            print("  🔑 Contraseña: [tu contraseña de admin]\n")

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
