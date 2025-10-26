"""
Seed de relaciones Amenaza-Recurso-Tipo según MAGERIT 3.2

Este módulo define qué amenazas del catálogo MAGERIT aplican a cada tipo
de recurso (HARDWARE, SOFTWARE, DATOS, etc.) y en qué dimensiones CIA.

También establece la frecuencia base de ocurrencia para cada combinación.

Escala de frecuencia MAGERIT:
- 0: Nunca ocurre
- 1: Muy rara vez (cada varios años)
- 2: Rara vez (anualmente)
- 3: Ocasionalmente (mensualmente)
- 4: Frecuentemente (semanalmente)
- 5: Muy frecuentemente (diariamente)
"""

from app.risks.models import Amenaza, AmenazaRecursoTipo
from models import db


# Mapeo de amenazas a tipos de recursos
# Formato: {codigo_amenaza: [(tipo_recurso, dimension, frecuencia), ...]}
RELACIONES_AMENAZA_RECURSO = {
    # === GRUPO: NATURALES ===

    # N.1 - Fuego
    'N.1': [
        ('HARDWARE', 'D', 2),  # Afecta disponibilidad de hardware
        ('HARDWARE', 'I', 2),  # Puede destruir integridad física
        ('SOFTWARE', 'D', 2),  # Destruye medios donde está el software
        ('DATOS', 'D', 2),     # Destruye disponibilidad de datos
        ('DATOS', 'I', 2),     # Destruye integridad de datos
        ('INSTALACIONES', 'D', 2),
        ('REDES', 'D', 2),
    ],

    # N.2 - Daños por agua
    'N.2': [
        ('HARDWARE', 'D', 2),
        ('HARDWARE', 'I', 2),
        ('INSTALACIONES', 'D', 2),
        ('REDES', 'D', 2),
    ],

    # N.* - Desastres naturales
    'N.*': [  # Desastres naturales
        ('HARDWARE', 'D', 1),
        ('INSTALACIONES', 'D', 1),
        ('REDES', 'D', 1),
    ],

    # === GRUPO: INDUSTRIALES ===

    # I.1 - Fuego
    'I.1': [
        ('HARDWARE', 'D', 2),
        ('INSTALACIONES', 'D', 2),
    ],

    # I.2 - Daños por agua
    'I.2': [
        ('HARDWARE', 'D', 2),
        ('INSTALACIONES', 'D', 2),
    ],

    # I.3 - Desastres industriales
    'I.3': [
        ('HARDWARE', 'D', 1),
        ('INSTALACIONES', 'D', 1),
    ],

    # I.4 - Contaminación mecánica
    'I.4': [
        ('HARDWARE', 'D', 2),
        ('HARDWARE', 'I', 1),
    ],

    # I.5 - Contaminación electromagnética
    'I.5': [
        ('HARDWARE', 'D', 2),
        ('REDES', 'D', 2),
        ('DATOS', 'I', 2),
    ],

    # I.6 - Avería de origen físico o lógico
    'I.6': [
        ('HARDWARE', 'D', 3),
        ('SOFTWARE', 'D', 3),
        ('REDES', 'D', 3),
    ],

    # I.7 - Corte del suministro eléctrico
    'I.7': [
        ('HARDWARE', 'D', 3),
        ('REDES', 'D', 3),
        ('SERVICIOS', 'D', 3),
    ],

    # I.8 - Condiciones inadecuadas de temperatura o humedad
    'I.8': [
        ('HARDWARE', 'D', 2),
    ],

    # I.9 - Fallo de servicios de comunicaciones
    'I.9': [
        ('REDES', 'D', 3),
        ('SERVICIOS', 'D', 3),
    ],

    # I.10 - Interrupción de otros servicios
    'I.10': [
        ('SERVICIOS', 'D', 2),
    ],

    # I.11 - Degradación de los soportes de almacenamiento
    'I.11': [
        ('HARDWARE', 'D', 2),
        ('DATOS', 'D', 2),
        ('DATOS', 'I', 2),
    ],

    # === GRUPO: ERRORES (no intencionados) ===

    # E.1 - Errores de los usuarios
    'E.1': [
        ('DATOS', 'I', 4),
        ('DATOS', 'D', 3),
        ('DATOS', 'C', 3),
        ('SOFTWARE', 'I', 3),
        ('SERVICIOS', 'D', 3),
    ],

    # E.2 - Errores del administrador
    'E.2': [
        ('DATOS', 'I', 3),
        ('DATOS', 'D', 3),
        ('DATOS', 'C', 3),
        ('SOFTWARE', 'I', 3),
        ('HARDWARE', 'D', 2),
        ('REDES', 'D', 3),
        ('SERVICIOS', 'D', 3),
    ],

    # E.3 - Errores de monitorización
    'E.3': [
        ('SERVICIOS', 'D', 3),
        ('HARDWARE', 'D', 2),
    ],

    # E.4 - Errores de configuración
    'E.4': [
        ('SOFTWARE', 'I', 3),
        ('SOFTWARE', 'D', 3),
        ('REDES', 'D', 3),
        ('SERVICIOS', 'D', 3),
        ('HARDWARE', 'D', 2),
    ],

    # E.7 - Deficiencias en la organización
    'E.7': [
        ('SERVICIOS', 'D', 3),
        ('DATOS', 'I', 2),
    ],

    # E.8 - Difusión de software dañino
    'E.8': [
        ('SOFTWARE', 'I', 4),
        ('SOFTWARE', 'D', 4),
        ('DATOS', 'I', 4),
        ('DATOS', 'D', 3),
        ('DATOS', 'C', 3),
    ],

    # E.9 - Errores de re-encaminamiento
    'E.9': [
        ('REDES', 'D', 2),
        ('DATOS', 'C', 2),
    ],

    # E.10 - Errores de secuencia
    'E.10': [
        ('SOFTWARE', 'I', 3),
        ('DATOS', 'I', 3),
    ],

    # E.15 - Alteración accidental de la información
    'E.15': [
        ('DATOS', 'I', 3),
    ],

    # E.18 - Destrucción de información
    'E.18': [
        ('DATOS', 'D', 2),
        ('DATOS', 'I', 2),
    ],

    # E.19 - Fugas de información
    'E.19': [
        ('DATOS', 'C', 3),
    ],

    # E.20 - Vulnerabilidades de los programas
    'E.20': [
        ('SOFTWARE', 'I', 4),
        ('SOFTWARE', 'D', 3),
        ('DATOS', 'C', 3),
        ('DATOS', 'I', 3),
    ],

    # E.21 - Errores de mantenimiento / actualización
    'E.21': [
        ('SOFTWARE', 'D', 3),
        ('SOFTWARE', 'I', 2),
        ('HARDWARE', 'D', 2),
    ],

    # E.23 - Errores de uso
    'E.23': [
        ('DATOS', 'I', 4),
        ('SERVICIOS', 'D', 3),
    ],

    # E.24 - Denegación de servicio
    'E.24': [
        ('SERVICIOS', 'D', 3),
        ('REDES', 'D', 3),
    ],

    # E.25 - Pérdida de equipos
    'E.25': [
        ('HARDWARE', 'D', 2),
        ('DATOS', 'C', 2),
    ],

    # E.28 - Indisponibilidad del personal
    'E.28': [
        ('SERVICIOS', 'D', 2),
        ('PERSONAL', 'D', 2),
    ],

    # === GRUPO: ATAQUES ===

    # A.3 - Manipulación de los registros de actividad (log)
    'A.3': [
        ('DATOS', 'I', 3),
    ],

    # A.4 - Manipulación de la configuración
    'A.4': [
        ('SOFTWARE', 'I', 3),
        ('HARDWARE', 'I', 2),
    ],

    # A.5 - Suplantación de la identidad del usuario
    'A.5': [
        ('DATOS', 'C', 3),
        ('DATOS', 'I', 3),
        ('SERVICIOS', 'I', 3),
    ],

    # A.6 - Abuso de privilegios de acceso
    'A.6': [
        ('DATOS', 'C', 3),
        ('DATOS', 'I', 3),
        ('SERVICIOS', 'I', 2),
    ],

    # A.7 - Uso no previsto
    'A.7': [
        ('SERVICIOS', 'D', 3),
        ('HARDWARE', 'D', 2),
    ],

    # A.8 - Difusión de software dañino
    'A.8': [
        ('SOFTWARE', 'I', 4),
        ('DATOS', 'I', 4),
        ('DATOS', 'C', 3),
        ('SERVICIOS', 'D', 4),
    ],

    # A.9 - Re-encaminamiento de mensajes
    'A.9': [
        ('REDES', 'C', 3),
        ('DATOS', 'C', 3),
    ],

    # A.10 - Alteración de secuencia
    'A.10': [
        ('DATOS', 'I', 3),
    ],

    # A.11 - Acceso no autorizado
    'A.11': [
        ('DATOS', 'C', 4),
        ('SERVICIOS', 'C', 3),
        ('SOFTWARE', 'C', 3),
    ],

    # A.12 - Análisis de tráfico
    'A.12': [
        ('DATOS', 'C', 3),
    ],

    # A.13 - Repudio
    'A.13': [
        ('DATOS', 'I', 2),
        ('SERVICIOS', 'I', 2),
    ],

    # A.14 - Interceptación de información (escucha)
    'A.14': [
        ('DATOS', 'C', 3),
    ],

    # A.15 - Modificación deliberada de la información
    'A.15': [
        ('DATOS', 'I', 3),
    ],

    # A.18 - Destrucción de información
    'A.18': [
        ('DATOS', 'D', 2),
        ('DATOS', 'I', 2),
    ],

    # A.19 - Divulgación de información
    'A.19': [
        ('DATOS', 'C', 3),
    ],

    # A.22 - Manipulación de programas
    'A.22': [
        ('SOFTWARE', 'I', 3),
    ],

    # A.23 - Manipulación de los equipos
    'A.23': [
        ('HARDWARE', 'I', 2),
        ('HARDWARE', 'D', 2),
    ],

    # A.24 - Denegación de servicio
    'A.24': [
        ('SERVICIOS', 'D', 4),
        ('REDES', 'D', 4),
    ],

    # A.25 - Robo de equipos o documentos
    'A.25': [
        ('HARDWARE', 'D', 2),
        ('DATOS', 'C', 2),
    ],

    # A.26 - Ataque destructivo
    'A.26': [
        ('HARDWARE', 'D', 2),
        ('DATOS', 'D', 2),
        ('SERVICIOS', 'D', 2),
    ],

    # A.27 - Ocupación enemiga
    'A.27': [
        ('INSTALACIONES', 'D', 1),
        ('HARDWARE', 'D', 1),
    ],

    # A.28 - Indisponibilidad del personal
    'A.28': [
        ('SERVICIOS', 'D', 2),
        ('PERSONAL', 'D', 2),
    ],

    # A.29 - Extorsión
    'A.29': [
        ('DATOS', 'C', 2),
        ('SERVICIOS', 'D', 2),
    ],

    # A.30 - Ingeniería social (piratería)
    'A.30': [
        ('DATOS', 'C', 3),
        ('SERVICIOS', 'I', 2),
    ],
}


def seed_amenaza_recurso(force_reload=False, interactive=True):
    """
    Carga las relaciones amenaza-recurso-tipo en la base de datos

    Args:
        force_reload: Si True, elimina y recarga todas las relaciones
        interactive: Si True, pide confirmación al usuario
    """
    # Verificar si ya existen datos
    existing_count = AmenazaRecursoTipo.query.count()

    if existing_count > 0 and not force_reload:
        if interactive:
            print(f"\n⚠️  Ya existen {existing_count} relaciones amenaza-recurso en la base de datos.")
            respuesta = input("¿Deseas recargar las relaciones? (s/N): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada.")
                return
        else:
            print(f"  → Amenaza-recurso relationships already exist ({existing_count} relationships)")
            return

    # Eliminar relaciones existentes si force_reload
    if force_reload and existing_count > 0:
        print(f"🗑️  Eliminando {existing_count} relaciones existentes...")
        AmenazaRecursoTipo.query.delete()
        db.session.commit()

    print("\n📋 Cargando relaciones amenaza-recurso según MAGERIT 3.2...")

    contador_creados = 0
    contador_errores = 0
    stats_por_tipo = {}
    stats_por_dimension = {}

    for codigo_amenaza, relaciones in RELACIONES_AMENAZA_RECURSO.items():
        # Buscar la amenaza por código
        amenaza = Amenaza.query.filter_by(codigo=codigo_amenaza).first()

        if not amenaza:
            print(f"  ⚠️  Amenaza {codigo_amenaza} no encontrada, omitiendo...")
            contador_errores += 1
            continue

        for tipo_recurso, dimension, frecuencia in relaciones:
            try:
                # Verificar si ya existe
                existe = AmenazaRecursoTipo.query.filter_by(
                    amenaza_id=amenaza.id,
                    tipo_recurso=tipo_recurso,
                    dimension_afectada=dimension
                ).first()

                if existe:
                    # Actualizar frecuencia
                    existe.frecuencia_base = frecuencia
                else:
                    # Crear nueva relación
                    relacion = AmenazaRecursoTipo(
                        amenaza_id=amenaza.id,
                        tipo_recurso=tipo_recurso,
                        dimension_afectada=dimension,
                        frecuencia_base=frecuencia
                    )
                    db.session.add(relacion)
                    contador_creados += 1

                # Actualizar estadísticas
                stats_por_tipo[tipo_recurso] = stats_por_tipo.get(tipo_recurso, 0) + 1
                stats_por_dimension[dimension] = stats_por_dimension.get(dimension, 0) + 1

            except Exception as e:
                print(f"  ❌ Error creando relación {codigo_amenaza}-{tipo_recurso}-{dimension}: {e}")
                contador_errores += 1
                continue

    # Guardar cambios
    try:
        db.session.commit()
        print(f"\n✅ Relaciones amenaza-recurso cargadas exitosamente")
        print(f"  → Creadas: {contador_creados}")
        if contador_errores > 0:
            print(f"  → Errores: {contador_errores}")

        print(f"\n📊 Estadísticas por tipo de recurso:")
        for tipo, count in sorted(stats_por_tipo.items()):
            print(f"  • {tipo}: {count} relaciones")

        print(f"\n📊 Estadísticas por dimensión:")
        for dim, count in sorted(stats_por_dimension.items()):
            dim_nombre = {'C': 'Confidencialidad', 'I': 'Integridad', 'D': 'Disponibilidad'}
            print(f"  • {dim_nombre[dim]}: {count} relaciones")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al guardar en la base de datos: {e}")
        raise


if __name__ == '__main__':
    print("Este módulo debe ejecutarse desde el contexto de la aplicación Flask")
    print("Usa: flask seed-amenaza-recurso")
