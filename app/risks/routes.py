"""
Rutas del Módulo de Gestión de Riesgos
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.risks import bp
from app.risks.models import (
    ActivoInformacion, RecursoInformacion, ProcesoNegocio,
    Amenaza, ControlISO27002, EvaluacionRiesgo, Riesgo,
    SalvaguardaImplantada, TratamientoRiesgo, DeclaracionAplicabilidad,
    ActivoRecurso, ActivoProceso, HistorialRiesgo
)
from app.risks.services.risk_calculation_service import RiskCalculationService
from models import db
from datetime import datetime


# ==================== DASHBOARD PRINCIPAL ====================

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal del módulo de riesgos"""

    # Obtener estadísticas generales
    total_activos = ActivoInformacion.query.count()
    total_riesgos = Riesgo.query.count()

    # Top 10 riesgos más críticos
    top_riesgos = Riesgo.query.order_by(
        Riesgo.nivel_riesgo_efectivo.desc()
    ).limit(10).all()

    # Matriz de riesgos (probabilidad x impacto)
    # Normalizar valores MAGERIT (que pueden ser > 5) a escala 1-5
    matriz_riesgos = {}
    distribucion_riesgos = {
        'MUY_ALTO': 0,
        'ALTO': 0,
        'MEDIO': 0,
        'BAJO': 0,
        'MUY_BAJO': 0
    }
    riesgos_criticos = 0

    riesgos_all = Riesgo.query.all()
    for riesgo in riesgos_all:
        if riesgo.probabilidad_efectiva and riesgo.impacto_efectivo:
            # Normalizar a escala 1-5 para la matriz visual
            # Nueva escala normalizada: prob 0-10, impacto 0-10
            prob_norm = min(5, max(1, round(riesgo.probabilidad_efectiva / 2)))  # 0-10 -> 1-5
            imp_norm = min(5, max(1, round(riesgo.impacto_efectivo / 2)))        # 0-10 -> 1-5
            nivel_norm = prob_norm * imp_norm  # Nivel normalizado 1-25

            # Agregar a matriz
            key = (prob_norm, imp_norm)
            matriz_riesgos[key] = matriz_riesgos.get(key, 0) + 1

            # Clasificar por nivel de riesgo efectivo (escala 0-100)
            nivel_riesgo = riesgo.nivel_riesgo_efectivo
            if nivel_riesgo >= 80:
                distribucion_riesgos['MUY_ALTO'] += 1
                riesgos_criticos += 1
            elif nivel_riesgo >= 60:
                distribucion_riesgos['ALTO'] += 1
                riesgos_criticos += 1
            elif nivel_riesgo >= 40:
                distribucion_riesgos['MEDIO'] += 1
            elif nivel_riesgo >= 20:
                distribucion_riesgos['BAJO'] += 1
            else:
                distribucion_riesgos['MUY_BAJO'] += 1

    stats = {
        'total_activos': total_activos,
        'total_riesgos': total_riesgos,
        'riesgos_criticos': riesgos_criticos
    }

    # Debug: log matriz_riesgos
    print(f"DEBUG Dashboard - Total riesgos: {total_riesgos}")
    print(f"DEBUG Dashboard - Matriz riesgos: {matriz_riesgos}")
    print(f"DEBUG Dashboard - Distribución: {distribucion_riesgos}")

    return render_template(
        'risks/dashboard.html',
        stats=stats,
        top_riesgos=top_riesgos,
        distribucion_riesgos=distribucion_riesgos,
        matriz_riesgos=matriz_riesgos
    )


# ==================== GESTIÓN DE ACTIVOS ====================

@bp.route('/activos')
@login_required
def listar_activos():
    """Listado de activos de información"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Filtros
    tipo = request.args.get('tipo')
    criticidad = request.args.get('criticidad')
    search = request.args.get('search')

    query = ActivoInformacion.query

    if tipo:
        query = query.filter_by(tipo=tipo)
    if search:
        query = query.filter(
            db.or_(
                ActivoInformacion.nombre.ilike(f'%{search}%'),
                ActivoInformacion.descripcion.ilike(f'%{search}%')
            )
        )

    pagination = query.order_by(ActivoInformacion.nombre).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Estadísticas
    from sqlalchemy import func
    stats = {
        'criticos': ActivoInformacion.query.filter(
            db.or_(
                ActivoInformacion.confidencialidad >= 4,
                ActivoInformacion.integridad >= 4,
                ActivoInformacion.disponibilidad >= 4
            )
        ).count(),
        'altos': ActivoInformacion.query.filter(
            db.or_(
                ActivoInformacion.confidencialidad == 3,
                ActivoInformacion.integridad == 3,
                ActivoInformacion.disponibilidad == 3
            )
        ).count(),
        'procesos': ProcesoNegocio.query.count()
    }

    return render_template(
        'risks/activos_list.html',
        activos=pagination.items,
        pagination=pagination,
        stats=stats
    )


@bp.route('/activos/nuevo', methods=['GET', 'POST'])
@login_required
def activos_create():
    """Crear nuevo activo"""
    if request.method == 'POST':
        try:
            activo = ActivoInformacion(
                codigo=request.form.get('codigo'),
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion'),
                tipo_activo=request.form.get('tipo_activo'),
                funcion=request.form.get('funcion'),
                ubicacion=request.form.get('ubicacion'),
                propietario_id=request.form.get('propietario_id') or current_user.id,
                confidencialidad=int(request.form.get('confidencialidad', 0)),
                integridad=int(request.form.get('integridad', 0)),
                disponibilidad=int(request.form.get('disponibilidad', 0)),
                justificacion_c=request.form.get('justificacion_c'),
                justificacion_i=request.form.get('justificacion_i'),
                justificacion_d=request.form.get('justificacion_d')
            )

            # Calcular importancia propia
            activo.calcular_importancia_propia()

            db.session.add(activo)
            db.session.commit()

            flash(f'Activo {activo.codigo} creado exitosamente', 'success')
            return redirect(url_for('risks.activos_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear activo: {str(e)}', 'error')

    return render_template('risks/assets/form.html', activo=None)


@bp.route('/activos/<int:id>')
@login_required
def activos_view(id):
    """Ver detalle de un activo"""
    activo = ActivoInformacion.query.get_or_404(id)

    # Obtener recursos asociados
    recursos_asociados = db.session.query(RecursoInformacion).join(
        ActivoRecurso
    ).filter(ActivoRecurso.activo_id == id).all()

    # Obtener procesos asociados
    procesos_asociados = db.session.query(ProcesoNegocio).join(
        ActivoProceso
    ).filter(ActivoProceso.activo_id == id).all()

    # Obtener riesgos del activo
    riesgos = Riesgo.query.filter_by(activo_id=id).order_by(
        Riesgo.nivel_riesgo_efectivo.desc()
    ).limit(20).all()

    return render_template(
        'risks/assets/view.html',
        activo=activo,
        recursos_asociados=recursos_asociados,
        procesos_asociados=procesos_asociados,
        riesgos=riesgos
    )


@bp.route('/activos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def activos_edit(id):
    """Editar activo existente"""
    activo = ActivoInformacion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            activo.nombre = request.form.get('nombre')
            activo.descripcion = request.form.get('descripcion')
            activo.tipo_activo = request.form.get('tipo_activo')
            activo.funcion = request.form.get('funcion')
            activo.ubicacion = request.form.get('ubicacion')
            activo.confidencialidad = int(request.form.get('confidencialidad', 0))
            activo.integridad = int(request.form.get('integridad', 0))
            activo.disponibilidad = int(request.form.get('disponibilidad', 0))
            activo.justificacion_c = request.form.get('justificacion_c')
            activo.justificacion_i = request.form.get('justificacion_i')
            activo.justificacion_d = request.form.get('justificacion_d')

            # Recalcular importancia
            activo.calcular_importancia_propia()

            db.session.commit()

            flash(f'Activo {activo.codigo} actualizado exitosamente', 'success')
            return redirect(url_for('risks.activos_view', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar activo: {str(e)}', 'error')

    return render_template('risks/assets/form.html', activo=activo)


@bp.route('/activos/<int:id>/eliminar', methods=['POST'])
@login_required
def activos_delete(id):
    """Eliminar activo (soft delete)"""
    activo = ActivoInformacion.query.get_or_404(id)

    try:
        activo.estado = 'retirado'
        db.session.commit()
        flash(f'Activo {activo.codigo} marcado como retirado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar activo: {str(e)}', 'error')

    return redirect(url_for('risks.activos_list'))


# ==================== GESTIÓN DE RECURSOS ====================

@bp.route('/recursos')
@login_required
def recursos_list():
    """Listado de recursos de información"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Filtros
    tipo = request.args.get('tipo')
    estado = request.args.get('estado', 'operativo')
    search = request.args.get('search')

    query = RecursoInformacion.query

    if tipo:
        query = query.filter_by(tipo_recurso=tipo)
    if estado:
        query = query.filter_by(estado=estado)
    if search:
        query = query.filter(
            db.or_(
                RecursoInformacion.codigo.ilike(f'%{search}%'),
                RecursoInformacion.nombre.ilike(f'%{search}%')
            )
        )

    pagination = query.order_by(RecursoInformacion.codigo).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'risks/resources/list.html',
        recursos=pagination.items,
        pagination=pagination,
        tipos_recurso=RecursoInformacion.TIPOS_RECURSO
    )


@bp.route('/recursos/nuevo', methods=['GET', 'POST'])
@login_required
def recursos_create():
    """Crear nuevo recurso"""
    if request.method == 'POST':
        try:
            tipo_recurso = request.form.get('tipo_recurso')

            recurso = RecursoInformacion(
                codigo=request.form.get('codigo'),
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion'),
                tipo_recurso=tipo_recurso,
                importancia_tipologica=RecursoInformacion.get_importancia_tipologica_default(tipo_recurso),
                responsable_id=request.form.get('responsable_id') or current_user.id,
                ubicacion=request.form.get('ubicacion')
            )

            db.session.add(recurso)
            db.session.commit()

            flash(f'Recurso {recurso.codigo} creado exitosamente', 'success')
            return redirect(url_for('risks.recursos_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear recurso: {str(e)}', 'error')

    return render_template('risks/resources/form.html', recurso=None)


@bp.route('/recursos/<int:id>')
@login_required
def recursos_view(id):
    """Ver detalle de un recurso"""
    recurso = RecursoInformacion.query.get_or_404(id)

    # Obtener activos asociados
    activos_asociados = db.session.query(ActivoInformacion).join(
        ActivoRecurso
    ).filter(ActivoRecurso.recurso_id == id).all()

    # Obtener riesgos del recurso
    riesgos = Riesgo.query.filter_by(recurso_id=id).order_by(
        Riesgo.nivel_riesgo_efectivo.desc()
    ).limit(20).all()

    return render_template(
        'risks/resources/view.html',
        recurso=recurso,
        activos_asociados=activos_asociados,
        riesgos=riesgos
    )


@bp.route('/recursos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def recursos_edit(id):
    """Editar recurso existente"""
    recurso = RecursoInformacion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            recurso.nombre = request.form.get('nombre')
            recurso.descripcion = request.form.get('descripcion')
            recurso.tipo_recurso = request.form.get('tipo_recurso')
            recurso.ubicacion = request.form.get('ubicacion')

            db.session.commit()

            flash(f'Recurso {recurso.codigo} actualizado exitosamente', 'success')
            return redirect(url_for('risks.recursos_view', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar recurso: {str(e)}', 'error')

    return render_template('risks/resources/form.html', recurso=recurso)


# ==================== EVALUACIONES DE RIESGO ====================

@bp.route('/evaluaciones')
@login_required
def evaluaciones_list():
    """Listado de evaluaciones de riesgo"""
    evaluaciones = EvaluacionRiesgo.query.order_by(
        EvaluacionRiesgo.fecha_inicio.desc()
    ).all()

    return render_template('risks/evaluations/list.html', evaluaciones=evaluaciones)


@bp.route('/evaluaciones/nueva', methods=['GET', 'POST'])
@login_required
def evaluaciones_create():
    """Crear nueva evaluación de riesgo"""
    if request.method == 'POST':
        try:
            evaluacion = EvaluacionRiesgo(
                nombre=request.form.get('nombre'),
                descripcion=request.form.get('descripcion'),
                fecha_inicio=datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date(),
                umbral_riesgo_objetivo=float(request.form.get('umbral_riesgo_objetivo', 12.0)),
                alcance_descripcion=request.form.get('alcance_descripcion'),
                responsable_evaluacion_id=current_user.id,
                version=request.form.get('version', '1.0'),
                estado='en_curso'
            )

            db.session.add(evaluacion)
            db.session.flush()  # Para obtener el ID

            # Generar todos los riesgos automáticamente
            cantidad_riesgos = RiskCalculationService.generar_todos_los_riesgos(evaluacion.id)

            db.session.commit()

            flash(f'Evaluación creada exitosamente. Se generaron {cantidad_riesgos} riesgos.', 'success')
            return redirect(url_for('risks.evaluaciones_view', id=evaluacion.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear evaluación: {str(e)}', 'error')

    return render_template('risks/evaluations/form.html', evaluacion=None)


@bp.route('/evaluaciones/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def evaluaciones_edit(id):
    """Editar una evaluación existente"""
    evaluacion = EvaluacionRiesgo.query.get_or_404(id)

    if request.method == 'POST':
        try:
            evaluacion.nombre = request.form.get('nombre')
            evaluacion.descripcion = request.form.get('descripcion')
            evaluacion.fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date()
            evaluacion.umbral_riesgo_objetivo = float(request.form.get('umbral_riesgo_objetivo', 12.0))
            evaluacion.alcance_descripcion = request.form.get('alcance_descripcion')
            evaluacion.version = request.form.get('version', '1.0')

            db.session.commit()

            flash(f'Evaluación actualizada exitosamente', 'success')
            return redirect(url_for('risks.evaluaciones_view', id=evaluacion.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar evaluación: {str(e)}', 'error')

    return render_template('risks/evaluations/form.html', evaluacion=evaluacion)


@bp.route('/evaluaciones/<int:id>/eliminar', methods=['POST'])
@login_required
def evaluaciones_delete(id):
    """Eliminar una evaluación"""
    evaluacion = EvaluacionRiesgo.query.get_or_404(id)

    try:
        # Eliminar todos los riesgos asociados
        Riesgo.query.filter_by(evaluacion_id=id).delete()

        # Eliminar la evaluación
        db.session.delete(evaluacion)
        db.session.commit()

        flash(f'Evaluación "{evaluacion.nombre}" eliminada exitosamente', 'success')
        return redirect(url_for('risks.evaluaciones_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar evaluación: {str(e)}', 'error')
        return redirect(url_for('risks.evaluaciones_view', id=id))


@bp.route('/evaluaciones/<int:id>')
@login_required
def evaluaciones_view(id):
    """Ver detalle de una evaluación"""
    evaluacion = EvaluacionRiesgo.query.get_or_404(id)

    # Obtener estadísticas
    estadisticas = RiskCalculationService.obtener_estadisticas_evaluacion(id)

    # Top riesgos
    riesgos_criticos = Riesgo.query.filter_by(
        evaluacion_id=id
    ).order_by(Riesgo.nivel_riesgo_efectivo.desc()).limit(10).all()

    # Distribución por activo
    riesgos_por_activo = db.session.query(
        ActivoInformacion.nombre,
        db.func.count(Riesgo.id).label('cantidad'),
        db.func.avg(Riesgo.nivel_riesgo_efectivo).label('promedio')
    ).join(Riesgo).filter(
        Riesgo.evaluacion_id == id
    ).group_by(ActivoInformacion.nombre).order_by(
        db.desc('promedio')
    ).limit(10).all()

    return render_template(
        'risks/evaluations/view.html',
        evaluacion=evaluacion,
        estadisticas=estadisticas,
        riesgos_criticos=riesgos_criticos,
        riesgos_por_activo=riesgos_por_activo
    )


@bp.route('/evaluaciones/<int:id>/riesgos')
@login_required
def evaluaciones_riesgos(id):
    """Listado de riesgos de una evaluación"""
    evaluacion = EvaluacionRiesgo.query.get_or_404(id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Filtros
    clasificacion = request.args.get('clasificacion')
    dimension = request.args.get('dimension')
    activo_id = request.args.get('activo_id', type=int)

    query = Riesgo.query.filter_by(evaluacion_id=id)

    if clasificacion:
        query = query.filter_by(clasificacion_efectiva=clasificacion)
    if dimension:
        query = query.filter_by(dimension=dimension)
    if activo_id:
        query = query.filter_by(activo_id=activo_id)

    pagination = query.order_by(Riesgo.nivel_riesgo_efectivo.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Lista de activos para filtro
    activos = ActivoInformacion.query.filter_by(estado='activo').all()

    return render_template(
        'risks/evaluations/riesgos.html',
        evaluacion=evaluacion,
        riesgos=pagination.items,
        pagination=pagination,
        activos=activos,
        clasificaciones=Riesgo.CLASIFICACIONES,
        dimensiones=Riesgo.DIMENSIONES
    )


@bp.route('/evaluaciones/<int:id>/recalcular', methods=['POST'])
@login_required
def evaluaciones_recalcular(id):
    """Recalcular todos los riesgos de una evaluación"""
    evaluacion = EvaluacionRiesgo.query.get_or_404(id)

    try:
        cantidad = RiskCalculationService.recalcular_riesgos_evaluacion(id)
        flash(f'Se recalcularon {cantidad} riesgos exitosamente', 'success')
    except Exception as e:
        flash(f'Error al recalcular riesgos: {str(e)}', 'error')

    return redirect(url_for('risks.evaluaciones_view', id=id))


# ==================== RIESGOS ====================

@bp.route('/riesgos/<int:id>')
@login_required
def riesgos_view(id):
    """Ver detalle de un riesgo"""
    riesgo = Riesgo.query.get_or_404(id)

    # Obtener historial
    historial = HistorialRiesgo.query.filter_by(
        riesgo_id=id
    ).order_by(HistorialRiesgo.fecha_registro.desc()).limit(20).all()

    # Obtener controles aplicables
    controles_preventivos = RiskCalculationService.obtener_controles_aplicables(
        riesgo.amenaza, 'PREVENTIVO'
    )
    controles_reactivos = RiskCalculationService.obtener_controles_aplicables(
        riesgo.amenaza, 'REACTIVO'
    )

    return render_template(
        'risks/riesgos/view.html',
        riesgo=riesgo,
        historial=historial,
        controles_preventivos=controles_preventivos,
        controles_reactivos=controles_reactivos
    )


@bp.route('/riesgos/<int:id>/recalcular', methods=['POST'])
@login_required
def riesgos_recalcular(id):
    """Recalcular un riesgo específico"""
    try:
        riesgo = RiskCalculationService.recalcular_riesgo(id)
        flash(f'Riesgo recalculado. Nivel actual: {riesgo.clasificacion_efectiva}', 'success')
    except Exception as e:
        flash(f'Error al recalcular riesgo: {str(e)}', 'error')

    return redirect(url_for('risks.riesgos_view', id=id))


# ==================== CATÁLOGOS ====================

@bp.route('/amenazas')
@login_required
def amenazas_list():
    """Catálogo de amenazas"""
    grupo = request.args.get('grupo')

    query = Amenaza.query
    if grupo:
        query = query.filter_by(grupo=grupo)

    amenazas = query.order_by(Amenaza.codigo).all()

    return render_template(
        'risks/threats/list.html',
        amenazas=amenazas,
        grupos=Amenaza.GRUPOS
    )


@bp.route('/controles')
@login_required
def controles_list():
    """Catálogo de controles ISO 27002"""
    categoria = request.args.get('categoria')

    query = ControlISO27002.query
    if categoria:
        query = query.filter_by(categoria=categoria)

    controles = query.order_by(ControlISO27002.codigo).all()

    return render_template(
        'risks/controls/list.html',
        controles=controles,
        categorias=ControlISO27002.CATEGORIAS
    )


@bp.route('/controles/<int:id>')
@login_required
def controles_view(id):
    """Ver detalle de un control"""
    control = ControlISO27002.query.get_or_404(id)

    # Obtener salvaguarda implementada
    salvaguarda = SalvaguardaImplantada.query.filter_by(control_id=id).first()

    return render_template(
        'risks/controls/view.html',
        control=control,
        salvaguarda=salvaguarda
    )


@bp.route('/controles/<int:id>/salvaguarda', methods=['GET', 'POST'])
@login_required
def controles_salvaguarda(id):
    """Actualizar salvaguarda de un control"""
    control = ControlISO27002.query.get_or_404(id)
    salvaguarda = SalvaguardaImplantada.query.filter_by(control_id=id).first()

    if request.method == 'POST':
        try:
            if not salvaguarda:
                salvaguarda = SalvaguardaImplantada(control_id=id)
                db.session.add(salvaguarda)

            salvaguarda.nivel_madurez = int(request.form.get('nivel_madurez', 0))
            salvaguarda.descripcion_implementacion = request.form.get('descripcion_implementacion')
            salvaguarda.evidencias = request.form.get('evidencias')
            salvaguarda.responsable_id = current_user.id
            salvaguarda.estado = request.form.get('estado', 'implementado')
            salvaguarda.aplica = request.form.get('aplica') == 'true'
            salvaguarda.justificacion_no_aplica = request.form.get('justificacion_no_aplica')

            db.session.commit()

            flash(f'Salvaguarda actualizada. Nivel de madurez: {salvaguarda.nivel_madurez_texto}', 'success')
            return redirect(url_for('risks.controles_view', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar salvaguarda: {str(e)}', 'error')

    return render_template(
        'risks/controls/salvaguarda_form.html',
        control=control,
        salvaguarda=salvaguarda
    )


# ==================== API ENDPOINTS ====================

@bp.route('/api/estadisticas/<int:evaluacion_id>')
@login_required
def api_estadisticas(evaluacion_id):
    """API: Obtener estadísticas de una evaluación"""
    try:
        estadisticas = RiskCalculationService.obtener_estadisticas_evaluacion(evaluacion_id)
        return jsonify(estadisticas)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/api/riesgos/matriz/<int:evaluacion_id>')
@login_required
def api_matriz_riesgos(evaluacion_id):
    """API: Datos para matriz de riesgos (scatter plot)"""
    riesgos = Riesgo.query.filter_by(evaluacion_id=evaluacion_id).all()

    datos = [
        {
            'id': r.id,
            'codigo': r.codigo,
            'activo': r.activo.nombre if r.activo else '',
            'amenaza': r.amenaza.nombre if r.amenaza else '',
            'probabilidad': float(r.probabilidad_efectiva) if r.probabilidad_efectiva else 0,
            'impacto': float(r.impacto_efectivo) if r.impacto_efectivo else 0,
            'nivel': float(r.nivel_riesgo_efectivo) if r.nivel_riesgo_efectivo else 0,
            'clasificacion': r.clasificacion_efectiva
        }
        for r in riesgos
    ]

    return jsonify(datos)


@bp.route('/api/activos/search')
@login_required
def api_activos_search():
    """API: Búsqueda de activos para autocomplete"""
    q = request.args.get('q', '')

    activos = ActivoInformacion.query.filter(
        db.or_(
            ActivoInformacion.codigo.ilike(f'%{q}%'),
            ActivoInformacion.nombre.ilike(f'%{q}%')
        )
    ).filter_by(estado='activo').limit(20).all()

    resultados = [
        {
            'id': a.id,
            'codigo': a.codigo,
            'nombre': a.nombre,
            'tipo': a.tipo_activo
        }
        for a in activos
    ]

    return jsonify(resultados)


# ==================== CATÁLOGOS ====================

@bp.route('/catalogo/amenazas')
@login_required
def catalogo_amenazas():
    """Catálogo de amenazas MAGERIT 3.2"""
    # Filtros
    search = request.args.get('search')
    grupo = request.args.get('grupo')

    query = Amenaza.query

    if search:
        query = query.filter(
            db.or_(
                Amenaza.codigo.ilike(f'%{search}%'),
                Amenaza.nombre.ilike(f'%{search}%'),
                Amenaza.descripcion.ilike(f'%{search}%')
            )
        )

    if grupo:
        query = query.filter_by(grupo=grupo)

    amenazas = query.order_by(Amenaza.grupo, Amenaza.codigo).all()

    # Agrupar por tipo
    from itertools import groupby
    amenazas_por_grupo = {}
    for grupo_key, grupo_amenazas in groupby(amenazas, lambda x: x.grupo):
        amenazas_por_grupo[grupo_key] = list(grupo_amenazas)

    # Estadísticas
    from sqlalchemy import func
    stats_query = db.session.query(
        Amenaza.grupo,
        func.count(Amenaza.id).label('count')
    ).group_by(Amenaza.grupo).all()

    stats = {grupo: count for grupo, count in stats_query}

    return render_template(
        'risks/catalogo_amenazas.html',
        amenazas_por_grupo=amenazas_por_grupo,
        stats=stats
    )


# ==================== RIESGOS A TRATAR ====================

@bp.route('/riesgos-a-tratar')
@login_required
def riesgos_a_tratar():
    """Vista de riesgos que requieren tratamiento según el umbral objetivo"""

    # Obtener la evaluación activa
    evaluacion_activa = EvaluacionRiesgo.query.filter(
        EvaluacionRiesgo.estado.in_(['en_curso', 'completada', 'aprobada'])
    ).order_by(EvaluacionRiesgo.created_at.desc()).first()

    if not evaluacion_activa:
        flash('No hay evaluaciones de riesgo activas', 'warning')
        return redirect(url_for('risks.dashboard'))

    # Obtener umbral de riesgo objetivo
    umbral = float(evaluacion_activa.umbral_riesgo_objetivo or 50.0)

    # Obtener todos los riesgos de la evaluación activa que superen el umbral
    riesgos_query = Riesgo.query.filter(
        Riesgo.evaluacion_id == evaluacion_activa.id,
        Riesgo.nivel_riesgo_efectivo > umbral
    ).order_by(Riesgo.nivel_riesgo_efectivo.desc())

    riesgos_all = riesgos_query.all()

    # Clasificar riesgos según su estado de tratamiento
    sin_tratamiento = []
    tratamiento_planificado = []
    tratamiento_en_progreso = []
    tratamiento_implementado = []

    for riesgo in riesgos_all:
        # Obtener el tratamiento más reciente del riesgo
        tratamiento = TratamientoRiesgo.query.filter_by(
            riesgo_id=riesgo.id
        ).order_by(TratamientoRiesgo.created_at.desc()).first()

        if not tratamiento:
            sin_tratamiento.append({
                'riesgo': riesgo,
                'tratamiento': None
            })
        elif tratamiento.estado == 'planificado':
            tratamiento_planificado.append({
                'riesgo': riesgo,
                'tratamiento': tratamiento
            })
        elif tratamiento.estado == 'en_progreso':
            tratamiento_en_progreso.append({
                'riesgo': riesgo,
                'tratamiento': tratamiento
            })
        else:  # implementado, verificado
            tratamiento_implementado.append({
                'riesgo': riesgo,
                'tratamiento': tratamiento
            })

    # Estadísticas
    stats = {
        'total': len(riesgos_all),
        'sin_tratamiento': len(sin_tratamiento),
        'planificado': len(tratamiento_planificado),
        'en_progreso': len(tratamiento_en_progreso),
        'implementado': len(tratamiento_implementado),
        'riesgo_total_efectivo': sum(float(r.nivel_riesgo_efectivo or 0) for r in riesgos_all),
        'umbral': umbral
    }

    return render_template(
        'risks/riesgos_a_tratar.html',
        sin_tratamiento=sin_tratamiento,
        tratamiento_planificado=tratamiento_planificado,
        tratamiento_en_progreso=tratamiento_en_progreso,
        tratamiento_implementado=tratamiento_implementado,
        stats=stats,
        evaluacion=evaluacion_activa,
        umbral=umbral
    )


# ==================== VISTAS DE RIESGOS POR SERVICIO ====================

def get_risks_for_service(service):
    """
    Obtiene todos los riesgos asociados a un servicio a través de sus activos.
    Vincula Asset (código) con ActivoInformacion (código) y luego con Riesgo.

    Args:
        service: Instancia de Service

    Returns:
        list: Lista de objetos Riesgo asociados al servicio
    """
    # Obtener códigos de los activos del servicio
    asset_codes = [asset.asset_code for asset in service.assets if asset.asset_code]

    if not asset_codes:
        return []

    # Buscar ActivoInformacion por código
    activos_info = ActivoInformacion.query.filter(
        ActivoInformacion.codigo.in_(asset_codes)
    ).all()

    activos_ids = [activo.id for activo in activos_info]

    if not activos_ids:
        return []

    # Obtener riesgos asociados a esos activos
    riesgos = Riesgo.query.filter(
        Riesgo.activo_id.in_(activos_ids)
    ).order_by(Riesgo.nivel_riesgo_efectivo.desc()).all()

    return riesgos


def calculate_service_risk_stats(service):
    """
    Calcula estadísticas de riesgos para un servicio.

    Args:
        service: Instancia de Service

    Returns:
        dict: Diccionario con estadísticas de riesgos
    """
    riesgos = get_risks_for_service(service)

    if not riesgos:
        return {
            'total': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'avg_level': 0,
            'max_level': 0
        }

    high_count = len([r for r in riesgos if r.clasificacion_efectiva in ['ALTO', 'MUY_ALTO']])
    medium_count = len([r for r in riesgos if r.clasificacion_efectiva == 'MEDIO'])
    low_count = len([r for r in riesgos if r.clasificacion_efectiva in ['BAJO', 'MUY_BAJO']])

    niveles = [float(r.nivel_riesgo_efectivo or 0) for r in riesgos]
    avg_level = sum(niveles) / len(niveles) if niveles else 0
    max_level = max(niveles) if niveles else 0

    return {
        'total': len(riesgos),
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'avg_level': round(avg_level, 2),
        'max_level': round(max_level, 2)
    }


@bp.route('/servicios')
@login_required
def risks_by_service():
    """Vista general de riesgos agrupados por servicio"""
    from app.blueprints.services import Service, ServiceStatus

    # Obtener todos los servicios activos
    services = Service.query.filter_by(status=ServiceStatus.ACTIVE).all()

    # Calcular estadísticas de riesgos para cada servicio
    services_with_risks = []
    total_risks = 0
    services_with_high_risks = 0
    total_avg_risk = []

    for service in services:
        stats = calculate_service_risk_stats(service)

        if stats['total'] > 0:
            services_with_risks.append({
                'service': service,
                'stats': stats
            })
            total_risks += stats['total']

            if stats['high_count'] > 0:
                services_with_high_risks += 1

            total_avg_risk.append(stats['avg_level'])

    # Ordenar por número de riesgos altos/muy altos
    services_with_risks.sort(key=lambda x: x['stats']['high_count'], reverse=True)

    # Estadísticas generales
    general_stats = {
        'total_services': len(services_with_risks),
        'total_risks': total_risks,
        'services_with_high_risks': services_with_high_risks,
        'avg_risk_level': round(sum(total_avg_risk) / len(total_avg_risk), 2) if total_avg_risk else 0,
        'services_without_risks': len(services) - len(services_with_risks)
    }

    return render_template(
        'risks/risks_by_service.html',
        services_with_risks=services_with_risks,
        stats=general_stats
    )


@bp.route('/servicios/<int:service_id>')
@login_required
def service_risks_detail(service_id):
    """Vista detallada de riesgos de un servicio específico"""
    from app.blueprints.services import Service

    service = Service.query.get_or_404(service_id)
    riesgos = get_risks_for_service(service)

    # Obtener umbral de riesgo de la evaluación activa
    evaluacion_activa = EvaluacionRiesgo.query.filter(
        EvaluacionRiesgo.estado.in_(['en_curso', 'completada', 'aprobada'])
    ).order_by(EvaluacionRiesgo.created_at.desc()).first()

    umbral = float(evaluacion_activa.umbral_riesgo_objetivo or 50.0) if evaluacion_activa else 50.0

    # Clasificar riesgos por nivel
    sin_tratamiento = []
    a_tratar = []
    altos_muy_altos = []
    medios = []
    bajos = []

    for riesgo in riesgos:
        # Verificar si tiene tratamiento
        tratamiento = TratamientoRiesgo.query.filter_by(
            riesgo_id=riesgo.id
        ).order_by(TratamientoRiesgo.created_at.desc()).first()

        # Clasificar sin tratamiento
        if not tratamiento or tratamiento.estado == 'planificado':
            sin_tratamiento.append(riesgo)

        # Clasificar riesgos a tratar (superan umbral)
        nivel = float(riesgo.nivel_riesgo_efectivo or 0)
        if nivel > umbral:
            a_tratar.append(riesgo)

        # Clasificar por nivel de riesgo efectivo
        if nivel >= 50:  # Alto/Muy Alto
            altos_muy_altos.append(riesgo)
        elif nivel >= 25:  # Medio
            medios.append(riesgo)
        else:  # Bajo/Muy Bajo
            bajos.append(riesgo)

    # Construir estadísticas
    stats = {
        'total': len(riesgos),
        'sin_tratamiento': sin_tratamiento,
        'a_tratar': a_tratar,
        'altos_muy_altos': altos_muy_altos,
        'medios': medios,
        'bajos': bajos,
        'umbral': umbral
    }

    return render_template(
        'risks/service_risks_detail.html',
        service=service,
        stats=stats
    )


