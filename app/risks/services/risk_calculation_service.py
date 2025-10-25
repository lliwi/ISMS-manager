"""
Servicio de Cálculo de Riesgos
Motor principal que implementa las fórmulas de cálculo según metodología MAGERIT
"""

import math
from sqlalchemy import and_
from models import db, SOAControl, SOAVersion
from app.risks.models import (
    Riesgo, ActivoInformacion, RecursoInformacion, Amenaza,
    AmenazaRecursoTipo, ControlAmenaza, HistorialRiesgo
)


class RiskCalculationService:
    """Servicio para cálculo automatizado de riesgos"""

    @staticmethod
    def calcular_modulo_normalizador(valor1, valor2):
        """
        Calcula el módulo normalizador |V| = √((v1² + v2²) / 2)

        Normaliza a escala 0-10 para valores de entrada en escala 0-5.
        Si ambos valores son máximos (5), el resultado es √(50/2) = 5

        Args:
            valor1: Primer valor (escala 0-5)
            valor2: Segundo valor (escala 0-5)

        Returns:
            float: Módulo normalizador (escala aproximada 0-7)
        """
        if valor1 == 0 and valor2 == 0:
            return 0
        # Normalización corregida: divide entre 2 en lugar de 50
        # Esto da valores más manejables en escala 0-7 aprox
        return math.sqrt((valor1**2 + valor2**2) / 2.0)

    @staticmethod
    def obtener_frecuencia_amenaza(amenaza, tipo_recurso, dimension):
        """
        Obtiene la frecuencia de ocurrencia de una amenaza para un tipo de recurso

        Args:
            amenaza: Objeto Amenaza
            tipo_recurso: Tipo de recurso (HARDWARE, SOFTWARE, etc.)
            dimension: Dimensión afectada (C, I, D)

        Returns:
            int: Frecuencia (0-5)
        """
        aplicabilidad = AmenazaRecursoTipo.query.filter(
            and_(
                AmenazaRecursoTipo.amenaza_id == amenaza.id,
                AmenazaRecursoTipo.tipo_recurso == tipo_recurso,
                AmenazaRecursoTipo.dimension_afectada == dimension
            )
        ).first()

        return aplicabilidad.frecuencia_base if aplicabilidad else 3  # Valor por defecto

    @staticmethod
    def obtener_controles_aplicables(amenaza, tipo_control):
        """
        Obtiene los controles aplicables a una amenaza

        Args:
            amenaza: Objeto Amenaza
            tipo_control: 'PREVENTIVO' o 'REACTIVO'

        Returns:
            list: Lista de objetos ControlAmenaza
        """
        return ControlAmenaza.query.filter(
            and_(
                ControlAmenaza.amenaza_id == amenaza.id,
                ControlAmenaza.tipo_control == tipo_control
            )
        ).all()

    @staticmethod
    def calcular_nivel_controles(controles_aplicables):
        """
        Calcula el nivel promedio de implementación de controles usando el SOA activo

        Args:
            controles_aplicables: Lista de ControlAmenaza (con control_codigo)

        Returns:
            tuple: (suma_madurez, cantidad_controles, nivel_promedio)
        """
        if not controles_aplicables:
            return 0, 0, 5.0  # Sin controles = máxima vulnerabilidad

        # Obtener la versión SOA activa
        soa_activo = SOAVersion.query.filter_by(is_current=True).first()
        if not soa_activo:
            # Si no hay SOA activo, no podemos calcular (ya no usamos salvaguardas)
            return 0, 0, 5.0

        suma_madurez = 0
        cantidad = 0

        for control_amenaza in controles_aplicables:
            # Buscar el control en el SOA activo directamente por código
            soa_control = SOAControl.query.filter_by(
                control_id=control_amenaza.control_codigo,
                soa_version_id=soa_activo.id,
                applicability_status='aplicable'
            ).first()

            if soa_control and soa_control.maturity_score > 0:
                # Normalizar madurez del SOA (0-6) a escala MAGERIT (0-5)
                # 0 (no implementado) -> 0
                # 6 (optimizado) -> 5
                madurez_normalizada = min(5, soa_control.maturity_score * 5.0 / 6.0)

                # Convertir efectividad de Decimal a float para evitar errores de tipo
                efectividad_float = float(control_amenaza.efectividad)
                suma_madurez += madurez_normalizada * efectividad_float
                cantidad += 1

        if cantidad == 0:
            return 0, 0, 5.0

        nivel = 5 - (suma_madurez / cantidad)
        return suma_madurez, cantidad, max(0, min(5, nivel))


    @staticmethod
    def calcular_riesgo_intrinseco(activo, recurso, amenaza, dimension):
        """
        Calcula el riesgo intrínseco (sin considerar controles)

        Fórmula normalizada a escala 0-100:
            RIESGO = PROBABILIDAD × IMPACTO (ambos en escala 0-10)

            IMPACTO = ((IP + IT) / 2) × (GRAVEDAD_MAX / 5) × 2
            Escala resultante: 0-10

            PROBABILIDAD = ((FRECUENCIA + FACILIDAD_MAX) / 2) × 2
            Escala resultante: 0-10

        Args:
            activo: Objeto ActivoInformacion
            recurso: Objeto RecursoInformacion
            amenaza: Objeto Amenaza
            dimension: 'C', 'I' o 'D'

        Returns:
            dict: Diccionario con todos los valores calculados
        """
        # 1. IMPORTANCIA DEL ACTIVO
        ip = activo.get_valoracion_dimension(dimension)  # 0-5
        # Si no hay recurso, usar valor medio (3)
        it = recurso.importancia_tipologica if recurso else 3  # 1-5

        # 2. IMPACTO INTRÍNSECO (escala 0-10)
        # Gravedad máxima = 5 (sin controles reactivos)
        gravedad_intrinseca = 5.0
        # Fórmula simplificada y normalizada
        impacto_intrinseco = ((ip + it) / 2.0) * (gravedad_intrinseca / 5.0) * 2.0

        # 3. FRECUENCIA DE LA AMENAZA
        tipo_recurso = recurso.tipo_recurso if recurso else 'sw_aplicacion'
        frecuencia = RiskCalculationService.obtener_frecuencia_amenaza(
            amenaza, tipo_recurso, dimension
        )

        # 4. PROBABILIDAD INTRÍNSECA (escala 0-10)
        # Facilidad máxima = 5 (sin controles preventivos)
        facilidad_intrinseca = 5.0
        # Fórmula simplificada y normalizada
        probabilidad_intrinseca = ((frecuencia + facilidad_intrinseca) / 2.0) * 2.0

        # 5. RIESGO INTRÍNSECO (escala 0-100)
        nivel_riesgo_intrinseco = impacto_intrinseco * probabilidad_intrinseca

        # 6. CLASIFICACIÓN
        clasificacion = Riesgo.clasificar_nivel(probabilidad_intrinseca, impacto_intrinseco)

        return {
            'importancia_propia': float(ip),
            'importancia_tipologica': it,
            'modulo_normalizador_impacto': 0,  # No usado en nueva fórmula
            'frecuencia_amenaza': frecuencia,
            'modulo_normalizador_probabilidad': 0,  # No usado en nueva fórmula
            'impacto_intrinseco': round(impacto_intrinseco, 2),
            'probabilidad_intrinseca': round(probabilidad_intrinseca, 2),
            'nivel_riesgo_intrinseco': round(nivel_riesgo_intrinseco, 2),
            'clasificacion_intrinseca': clasificacion
        }

    @staticmethod
    def calcular_riesgo_efectivo(activo, recurso, amenaza, dimension):
        """
        Calcula el riesgo efectivo (considerando controles actuales)

        Fórmula normalizada a escala 0-100:
            RIESGO = PROBABILIDAD × IMPACTO (ambos en escala 0-10)

            IMPACTO = (IP + IT) × (GRAVEDAD / 5) × 2
            GRAVEDAD = 5 - (Σ(Madurez × Efectividad) / N_Reactivos)
            Escala resultante: 0-10

            PROBABILIDAD = (FRECUENCIA + FACILIDAD) / 2 × 2
            FACILIDAD = 5 - (Σ(Madurez × Efectividad) / N_Preventivos)
            Escala resultante: 0-10

        Args:
            activo: Objeto ActivoInformacion
            recurso: Objeto RecursoInformacion
            amenaza: Objeto Amenaza
            dimension: 'C', 'I' o 'D'

        Returns:
            dict: Diccionario con todos los valores calculados
        """
        # 1. IMPORTANCIA DEL ACTIVO
        ip = activo.get_valoracion_dimension(dimension)  # 0-5
        # Si no hay recurso, usar valor medio (3)
        it = recurso.importancia_tipologica if recurso else 3  # 1-5

        # 2. OBTENER CONTROLES REACTIVOS Y CALCULAR GRAVEDAD
        controles_reactivos = RiskCalculationService.obtener_controles_aplicables(
            amenaza, 'REACTIVO'
        )
        suma_reactiva, n_reactivos, gravedad = RiskCalculationService.calcular_nivel_controles(
            controles_reactivos
        )

        # 3. CALCULAR IMPACTO EFECTIVO (escala 0-10)
        # La gravedad reduce el impacto (0=sin daño, 5=daño máximo)
        impacto_efectivo = ((ip + it) / 2.0) * (gravedad / 5.0) * 2.0

        # 4. FRECUENCIA DE LA AMENAZA
        tipo_recurso = recurso.tipo_recurso if recurso else 'sw_aplicacion'
        frecuencia = RiskCalculationService.obtener_frecuencia_amenaza(
            amenaza, tipo_recurso, dimension
        )

        # 5. OBTENER CONTROLES PREVENTIVOS Y CALCULAR FACILIDAD
        controles_preventivos = RiskCalculationService.obtener_controles_aplicables(
            amenaza, 'PREVENTIVO'
        )
        suma_preventiva, n_preventivos, facilidad = RiskCalculationService.calcular_nivel_controles(
            controles_preventivos
        )

        # 6. CALCULAR PROBABILIDAD EFECTIVA (escala 0-10)
        # La facilidad incrementa la probabilidad (0=imposible, 5=muy fácil)
        probabilidad_efectiva = ((frecuencia + facilidad) / 2.0) * 2.0

        # 7. RIESGO EFECTIVO (escala 0-100)
        nivel_riesgo_efectivo = impacto_efectivo * probabilidad_efectiva

        # 8. CLASIFICACIÓN
        clasificacion = Riesgo.clasificar_nivel(probabilidad_efectiva, impacto_efectivo)

        return {
            'importancia_propia': float(ip),
            'importancia_tipologica': it,
            'modulo_normalizador_impacto': 0,  # No usado en nueva fórmula
            'frecuencia_amenaza': frecuencia,
            'modulo_normalizador_probabilidad': 0,  # No usado en nueva fórmula
            'gravedad_vulnerabilidad': round(gravedad, 2),
            'facilidad_explotacion': round(facilidad, 2),
            'num_controles_reactivos': n_reactivos,
            'num_controles_preventivos': n_preventivos,
            'impacto_efectivo': round(impacto_efectivo, 2),
            'probabilidad_efectiva': round(probabilidad_efectiva, 2),
            'nivel_riesgo_efectivo': round(nivel_riesgo_efectivo, 2),
            'clasificacion_efectiva': clasificacion
        }

    @staticmethod
    def calcular_riesgo_residual(activo, recurso, amenaza, dimension, controles_adicionales=None):
        """
        Calcula el riesgo residual (con controles planificados)

        Args:
            activo: Objeto ActivoInformacion
            recurso: Objeto RecursoInformacion
            amenaza: Objeto Amenaza
            dimension: 'C', 'I' o 'D'
            controles_adicionales: Lista de IDs de controles adicionales planificados

        Returns:
            dict: Diccionario con valores residuales
        """
        # Similar al efectivo, pero considerando controles adicionales con madurez objetivo
        # Por ahora, retornamos el mismo que el efectivo
        # TODO: Implementar lógica de controles planificados
        return RiskCalculationService.calcular_riesgo_efectivo(activo, recurso, amenaza, dimension)

    @staticmethod
    def generar_codigo_riesgo(evaluacion_id, activo_id, recurso_id, amenaza_id, dimension):
        """
        Genera un código único para el riesgo

        Formato: R-{EVAL}-{ACTIVO}-{RECURSO}-{AMENAZA}-{DIM}

        Args:
            evaluacion_id: ID de la evaluación
            activo_id: ID del activo
            recurso_id: ID del recurso
            amenaza_id: ID de la amenaza
            dimension: C, I o D

        Returns:
            str: Código único del riesgo
        """
        return f"R-{evaluacion_id}-{activo_id}-{recurso_id}-{amenaza_id}-{dimension}"

    @staticmethod
    def crear_o_actualizar_riesgo(evaluacion_id, activo_id, recurso_id, amenaza_id, dimension):
        """
        Crea o actualiza un riesgo con todos sus cálculos

        Args:
            evaluacion_id: ID de la evaluación
            activo_id: ID del activo
            recurso_id: ID del recurso
            amenaza_id: ID de la amenaza
            dimension: C, I o D

        Returns:
            Riesgo: Objeto Riesgo creado o actualizado
        """
        # Cargar objetos
        activo = ActivoInformacion.query.get(activo_id)
        recurso = RecursoInformacion.query.get(recurso_id) if recurso_id else None
        amenaza = Amenaza.query.get(amenaza_id)

        if not activo or not amenaza:
            raise ValueError("Activo o amenaza no encontrados")

        # Verificar que la amenaza aplica a esta dimensión
        if not amenaza.afecta_dimension(dimension):
            return None  # La amenaza no afecta esta dimensión

        # Verificar que el activo tiene valoración en esta dimensión
        if activo.get_valoracion_dimension(dimension) == 0:
            return None  # El activo no requiere protección en esta dimensión

        # Generar código
        codigo = RiskCalculationService.generar_codigo_riesgo(
            evaluacion_id, activo_id, recurso_id, amenaza_id, dimension
        )

        # Buscar riesgo existente por código
        riesgo = Riesgo.query.filter_by(codigo=codigo).first()

        # Si no se encuentra por código, buscar por evaluacion+activo+amenaza+dimension
        # (para casos donde recurso_id cambió de valor a None o viceversa)
        if not riesgo:
            riesgo = Riesgo.query.filter_by(
                evaluacion_id=evaluacion_id,
                activo_id=activo_id,
                amenaza_id=amenaza_id,
                dimension=dimension
            ).first()

            # Si se encontró con búsqueda alternativa, actualizar código
            if riesgo:
                riesgo.codigo = codigo

        es_nuevo = riesgo is None

        if es_nuevo:
            riesgo = Riesgo(codigo=codigo)

        # Asignar relaciones
        riesgo.evaluacion_id = evaluacion_id
        riesgo.activo_id = activo_id
        riesgo.recurso_id = recurso_id
        riesgo.amenaza_id = amenaza_id
        riesgo.dimension = dimension

        # Calcular riesgo intrínseco
        valores_intrinseco = RiskCalculationService.calcular_riesgo_intrinseco(
            activo, recurso, amenaza, dimension
        )

        # Calcular riesgo efectivo
        valores_efectivo = RiskCalculationService.calcular_riesgo_efectivo(
            activo, recurso, amenaza, dimension
        )

        # Asignar todos los valores al modelo
        for key, value in valores_intrinseco.items():
            if hasattr(riesgo, key):
                setattr(riesgo, key, value)

        for key, value in valores_efectivo.items():
            if hasattr(riesgo, key):
                setattr(riesgo, key, value)

        # Asignar propietario del riesgo (por defecto el propietario del activo)
        if not riesgo.propietario_riesgo_id:
            riesgo.propietario_riesgo_id = activo.propietario_id

        # Guardar
        if es_nuevo:
            db.session.add(riesgo)

        db.session.flush()  # Para obtener el ID

        # Registrar en historial si hubo cambios significativos
        if not es_nuevo:
            RiskCalculationService.registrar_cambio_historial(
                riesgo,
                valores_efectivo['nivel_riesgo_efectivo'],
                valores_efectivo['clasificacion_efectiva'],
                'RECALCULO'
            )

        return riesgo

    @staticmethod
    def generar_todos_los_riesgos(evaluacion_id):
        """
        Genera todos los riesgos posibles para una evaluación

        Crea un riesgo por cada combinación de:
        - Activo (del módulo principal) × Amenaza × Dimensión

        Args:
            evaluacion_id: ID de la evaluación

        Returns:
            int: Cantidad de riesgos generados
        """
        from app.risks.models import ActivoRecurso
        from models import Asset, AssetStatus

        contador = 0

        # Obtener todas las relaciones activo-recurso existentes
        relaciones = ActivoRecurso.query.all()

        if relaciones:
            # Usar el sistema legacy de activos del módulo de riesgos
            for relacion in relaciones:
                activo = relacion.activo
                recurso = relacion.recurso

                # Obtener todas las amenazas aplicables al tipo de recurso
                aplicabilidades = AmenazaRecursoTipo.query.filter_by(
                    tipo_recurso=recurso.tipo_recurso
                ).all()

                for aplicabilidad in aplicabilidades:
                    amenaza = aplicabilidad.amenaza
                    dimension = aplicabilidad.dimension_afectada

                    try:
                        riesgo = RiskCalculationService.crear_o_actualizar_riesgo(
                            evaluacion_id,
                            activo.id,
                            recurso.id,
                            amenaza.id,
                            dimension
                        )

                        if riesgo:
                            contador += 1

                    except Exception as e:
                        print(f"Error generando riesgo (legacy): {e}")
                        continue
        else:
            # Usar activos del módulo principal
            print("Generando riesgos desde activos del módulo principal...")
            activos_principales = Asset.query.filter_by(status=AssetStatus.ACTIVE).all()

            for asset in activos_principales:
                # Crear o obtener ActivoInformacion equivalente
                activo_info = ActivoInformacion.query.filter_by(codigo=asset.asset_code).first()

                if not activo_info:
                    # Mapear CIA levels a valores numéricos (escala 0-5 para módulo riesgos)
                    # CIALevel: CRITICAL=5, HIGH=4, MEDIUM=3, LOW=2
                    conf_val = 5 if str(asset.confidentiality_level) == 'CIALevel.CRITICAL' else \
                              4 if str(asset.confidentiality_level) == 'CIALevel.HIGH' else \
                              3 if str(asset.confidentiality_level) == 'CIALevel.MEDIUM' else 2
                    int_val = 5 if str(asset.integrity_level) == 'CIALevel.CRITICAL' else \
                             4 if str(asset.integrity_level) == 'CIALevel.HIGH' else \
                             3 if str(asset.integrity_level) == 'CIALevel.MEDIUM' else 2
                    disp_val = 5 if str(asset.availability_level) == 'CIALevel.CRITICAL' else \
                              4 if str(asset.availability_level) == 'CIALevel.HIGH' else \
                              3 if str(asset.availability_level) == 'CIALevel.MEDIUM' else 2

                    # Crear activo de información
                    activo_info = ActivoInformacion(
                        codigo=asset.asset_code,
                        nombre=asset.name,
                        descripcion=asset.description or '',
                        tipo_activo='HW' if str(asset.category) == 'AssetCategory.HARDWARE' else \
                                   'SW' if str(asset.category) == 'AssetCategory.SOFTWARE' else \
                                   'DAT' if str(asset.category) == 'AssetCategory.INFORMATION' else 'OT',
                        funcion=asset.description or '',
                        ubicacion=asset.physical_location or '',
                        propietario_id=asset.owner_id,
                        estado='activo',
                        confidencialidad=conf_val,
                        integridad=int_val,
                        disponibilidad=disp_val
                    )
                    activo_info.calcular_importancia_propia()
                    db.session.add(activo_info)
                    db.session.flush()

                # Crear un recurso genérico
                tipo_recurso = 'HARDWARE' if 'HARDWARE' in str(asset.category) else \
                              'SOFTWARE' if 'SOFTWARE' in str(asset.category) else \
                              'DATOS' if 'INFORMATION' in str(asset.category) else 'OTROS'

                recurso = RecursoInformacion.query.filter_by(
                    codigo=f"REC-{asset.asset_code}"
                ).first()

                if not recurso:
                    recurso = RecursoInformacion(
                        codigo=f"REC-{asset.asset_code}",
                        nombre=f"Recurso {asset.name}",
                        descripcion=f"Recurso para {asset.name}",
                        tipo_recurso=tipo_recurso,
                        importancia_tipologica=3,
                        responsable_id=asset.owner_id,
                        ubicacion=asset.physical_location or ''
                    )
                    db.session.add(recurso)
                    db.session.flush()

                # Crear relación activo-recurso
                relacion_existe = ActivoRecurso.query.filter_by(
                    activo_id=activo_info.id,
                    recurso_id=recurso.id
                ).first()

                if not relacion_existe:
                    relacion = ActivoRecurso(
                        activo_id=activo_info.id,
                        recurso_id=recurso.id,
                        tipo_uso='procesa',
                        criticidad=3
                    )
                    db.session.add(relacion)

                # Generar riesgos
                aplicabilidades = AmenazaRecursoTipo.query.filter_by(
                    tipo_recurso=tipo_recurso
                ).all()

                for aplicabilidad in aplicabilidades:
                    amenaza = aplicabilidad.amenaza
                    dimension = aplicabilidad.dimension_afectada

                    try:
                        riesgo = RiskCalculationService.crear_o_actualizar_riesgo(
                            evaluacion_id,
                            activo_info.id,
                            recurso.id,
                            amenaza.id,
                            dimension
                        )

                        if riesgo:
                            contador += 1

                    except Exception as e:
                        print(f"Error generando riesgo para {asset.asset_code}: {e}")
                        continue

        db.session.commit()
        return contador

    @staticmethod
    def recalcular_riesgo(riesgo_id):
        """
        Recalcula un riesgo específico

        Args:
            riesgo_id: ID del riesgo

        Returns:
            Riesgo: Objeto actualizado
        """
        riesgo = Riesgo.query.get(riesgo_id)
        if not riesgo:
            raise ValueError(f"Riesgo {riesgo_id} no encontrado")

        nivel_anterior = riesgo.nivel_riesgo_efectivo
        clasificacion_anterior = riesgo.clasificacion_efectiva

        # Recalcular
        riesgo_actualizado = RiskCalculationService.crear_o_actualizar_riesgo(
            riesgo.evaluacion_id,
            riesgo.activo_id,
            riesgo.recurso_id,
            riesgo.amenaza_id,
            riesgo.dimension
        )

        # Registrar cambio
        if nivel_anterior != riesgo_actualizado.nivel_riesgo_efectivo:
            RiskCalculationService.registrar_cambio_historial(
                riesgo_actualizado,
                nivel_anterior,
                clasificacion_anterior,
                'RECALCULO_MANUAL'
            )

        db.session.commit()
        return riesgo_actualizado

    @staticmethod
    def recalcular_riesgos_evaluacion(evaluacion_id):
        """
        Recalcula todos los riesgos de una evaluación

        Args:
            evaluacion_id: ID de la evaluación

        Returns:
            int: Cantidad de riesgos recalculados
        """
        riesgos = Riesgo.query.filter_by(evaluacion_id=evaluacion_id).all()

        contador = 0
        for riesgo in riesgos:
            try:
                RiskCalculationService.recalcular_riesgo(riesgo.id)
                contador += 1
            except Exception as e:
                print(f"Error recalculando riesgo {riesgo.id}: {e}")
                continue

        return contador

    @staticmethod
    def registrar_cambio_historial(riesgo, nivel_anterior, clasificacion_anterior, tipo_cambio, usuario_id=None):
        """
        Registra un cambio en el historial del riesgo

        Args:
            riesgo: Objeto Riesgo
            nivel_anterior: Nivel de riesgo anterior
            clasificacion_anterior: Clasificación anterior
            tipo_cambio: Tipo de cambio realizado
            usuario_id: ID del usuario que realizó el cambio

        Returns:
            HistorialRiesgo: Registro creado
        """
        historial = HistorialRiesgo(
            riesgo_id=riesgo.id,
            usuario_id=usuario_id,
            nivel_riesgo_efectivo_anterior=nivel_anterior,
            nivel_riesgo_efectivo_nuevo=riesgo.nivel_riesgo_efectivo,
            clasificacion_anterior=clasificacion_anterior,
            clasificacion_nueva=riesgo.clasificacion_efectiva,
            tipo_cambio=tipo_cambio,
            descripcion_cambio=f"Cambio de {clasificacion_anterior} ({nivel_anterior}) a {riesgo.clasificacion_efectiva} ({riesgo.nivel_riesgo_efectivo})"
        )

        db.session.add(historial)
        return historial

    @staticmethod
    def obtener_estadisticas_evaluacion(evaluacion_id):
        """
        Obtiene estadísticas de una evaluación de riesgos

        Args:
            evaluacion_id: ID de la evaluación

        Returns:
            dict: Diccionario con estadísticas
        """
        riesgos = Riesgo.query.filter_by(evaluacion_id=evaluacion_id).all()

        if not riesgos:
            return {
                'total_riesgos': 0,
                'por_clasificacion': {},
                'nivel_riesgo_promedio': 0,
                'nivel_riesgo_maximo': 0,
                'riesgos_sobre_umbral': 0
            }

        # Estadísticas básicas
        total = len(riesgos)
        niveles = [r.nivel_riesgo_efectivo for r in riesgos if r.nivel_riesgo_efectivo]
        promedio = sum(niveles) / len(niveles) if niveles else 0
        maximo = max(niveles) if niveles else 0

        # Por clasificación
        clasificaciones = {}
        for riesgo in riesgos:
            clf = riesgo.clasificacion_efectiva or 'SIN_CLASIFICAR'
            clasificaciones[clf] = clasificaciones.get(clf, 0) + 1

        # Sobre umbral (asumiendo umbral de 12)
        umbral = 12.0
        sobre_umbral = sum(1 for n in niveles if n > umbral)

        return {
            'total_riesgos': total,
            'por_clasificacion': clasificaciones,
            'nivel_riesgo_promedio': round(promedio, 2),
            'nivel_riesgo_maximo': round(maximo, 2),
            'riesgos_sobre_umbral': sobre_umbral,
            'porcentaje_sobre_umbral': round((sobre_umbral / total * 100), 1) if total > 0 else 0
        }
