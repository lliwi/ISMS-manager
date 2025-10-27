/**
 * Visualización de Grafo de Relaciones de Activos
 * Usando D3.js Force-Directed Graph
 */

// Variables globales
let svg, g, simulation, link, node, tooltip;
let currentData = null;
let zoom;

// Paleta de colores por categoría
const categoryColors = {
    'Hardware': '#4CAF50',
    'Software': '#2196F3',
    'Información': '#FF9800',
    'Servicios': '#9C27B0',
    'Personas': '#F44336',
    'Instalaciones': '#795548'
};

// Colores por tipo de relación
const relationshipColors = {
    'Depende de': '#e74c3c',
    'Contiene': '#3498db',
    'Conecta con': '#2ecc71',
    'Procesa': '#f39c12',
    'Almacena': '#9b59b6',
    'Utiliza': '#1abc9c',
    'Protege': '#e67e22',
    'Soporta': '#34495e'
};

/**
 * Renderiza el grafo con los datos proporcionados
 */
function renderGraph(data) {
    console.log('=== INICIANDO renderGraph ===');
    console.log('Datos recibidos:', data);

    try {
        currentData = data;

        // Limpiar grafo existente
        console.log('Limpiando SVG existente...');
        d3.select('#graph-svg').selectAll('*').remove();

        if (!data || !data.nodes || data.nodes.length === 0) {
            console.warn('No hay nodos para mostrar');
            showEmptyState();
            return;
        }

        console.log(`✓ Grafo con ${data.nodes.length} nodos y ${data.links.length} enlaces`);

        // Configurar dimensiones
        const container = document.getElementById('graph-container');
        if (!container) {
            console.error('ERROR: No se encuentra el contenedor #graph-container');
            return;
        }
        const width = container.clientWidth;
        const height = container.clientHeight;
        console.log(`✓ Dimensiones del contenedor: ${width}x${height}`);

        // Crear SVG
        console.log('✓ Creando SVG...');
        svg = d3.select('#graph-svg')
            .attr('width', width)
            .attr('height', height);

        // Grupo para zoom y pan
        console.log('✓ Creando grupo para zoom...');
        g = svg.append('g');

        // Configurar zoom
        console.log('✓ Configurando zoom...');
        zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        svg.call(zoom);

        // Crear tooltip
        console.log('✓ Configurando tooltip...');
        tooltip = d3.select('#graph-tooltip');

        // Configurar simulación de fuerzas
        console.log('✓ Creando simulación de fuerzas...');
        simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links)
            .id(d => d.id)
            .distance(d => 150 - (d.criticality * 5)) // Mayor criticidad = más cerca
        )
        .force('charge', d3.forceManyBody()
            .strength(-300)
        )
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide()
            .radius(d => getNodeRadius(d) + 10)
        );

        // Crear marcadores de flecha para enlaces direccionales
        console.log('✓ Creando marcadores de flecha...');
        svg.append('defs').selectAll('marker')
            .data(Object.keys(relationshipColors))
            .enter().append('marker')
            .attr('id', d => `arrow-${d.replace(/\s+/g, '-')}`)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', d => relationshipColors[d]);

        // Crear enlaces
        console.log(`✓ Creando ${data.links.length} enlaces...`);
        link = g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(data.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke', d => relationshipColors[d.type] || '#999')
            .attr('stroke-width', d => Math.max(1, d.criticality / 3))
            .attr('marker-end', d => `url(#arrow-${d.type.replace(/\s+/g, '-')})`)
            .on('mouseover', showLinkTooltip)
            .on('mouseout', hideTooltip);

        // Crear nodos
        console.log(`✓ Creando ${data.nodes.length} nodos...`);
        const nodeGroup = g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(data.nodes)
            .enter().append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', dragStarted)
                .on('drag', dragged)
                .on('end', dragEnded)
            )
            .on('mouseover', showNodeTooltip)
            .on('mouseout', hideTooltip)
            .on('click', showNodeInfo)
            .on('dblclick', goToAsset);

        // Círculos de nodos
        console.log('✓ Añadiendo círculos a nodos...');
        nodeGroup.append('circle')
            .attr('r', d => getNodeRadius(d))
            .attr('fill', d => categoryColors[d.category] || '#95a5a6')
            .attr('opacity', d => d.status === 'Activo' ? 0.9 : 0.5)
            .append('title')
            .text(d => d.name);

        // Etiquetas de nodos
        console.log('✓ Añadiendo etiquetas a nodos...');
        nodeGroup.append('text')
            .attr('dy', d => getNodeRadius(d) + 15)
            .text(d => d.code)
            .style('font-size', '11px');

        // Indicador de criticidad (anillo exterior)
        console.log('✓ Añadiendo indicadores de criticidad...');
        nodeGroup.append('circle')
            .attr('r', d => getNodeRadius(d) + 3)
            .attr('fill', 'none')
            .attr('stroke', d => getCriticalityColor(d.criticality))
            .attr('stroke-width', 2)
            .attr('opacity', 0.6);

        node = nodeGroup;

        // Actualizar posiciones en cada tick de la simulación
        console.log('✓ Configurando simulación...');
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // Configurar botones de acción
        console.log('✓ Configurando botones de acción...');
        setupActionButtons();

        console.log('=== ✅ GRAFO RENDERIZADO CORRECTAMENTE ===');

    } catch (error) {
        console.error('=== ❌ ERROR AL RENDERIZAR GRAFO ===');
        console.error('Error:', error);
        console.error('Stack:', error.stack);
        alert('Error al renderizar el grafo: ' + error.message);
    }
}

/**
 * Calcula el radio del nodo basado en criticidad y valor de negocio
 */
function getNodeRadius(node) {
    const baseCriticality = node.criticality || 5;
    const baseValue = node.business_value || 5;
    return 10 + (baseCriticality * 1.5) + (baseValue * 0.5);
}

/**
 * Obtiene color según nivel de criticidad
 */
function getCriticalityColor(criticality) {
    if (criticality >= 8) return '#c0392b'; // Rojo - Crítico
    if (criticality >= 6) return '#e67e22'; // Naranja - Alto
    if (criticality >= 4) return '#f39c12'; // Amarillo - Medio
    return '#27ae60'; // Verde - Bajo
}

/**
 * Muestra tooltip para nodos
 */
function showNodeTooltip(event, d) {
    const html = `
        <h6><i class="fas fa-cube"></i> ${d.name}</h6>
        <div><strong>Código:</strong> ${d.code}</div>
        <div><strong>Categoría:</strong> <span class="badge" style="background-color: ${categoryColors[d.category]}">${d.category}</span></div>
        <div><strong>Clasificación:</strong> ${d.classification}</div>
        <div><strong>Propietario:</strong> ${d.owner}</div>
        <div class="mt-2">
            <strong>CIA:</strong><br>
            <small>
                C: ${d.confidentiality} |
                I: ${d.integrity} |
                A: ${d.availability}
            </small>
        </div>
        <div class="mt-1">
            <span class="badge bg-danger">Criticidad: ${d.criticality}/10</span>
            <span class="badge bg-success">Valor: ${d.business_value}/10</span>
        </div>
        <div class="mt-2"><small class="text-muted">Doble clic para ver detalles</small></div>
    `;

    tooltip
        .html(html)
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .classed('d-none', false);
}

/**
 * Muestra tooltip para enlaces
 */
function showLinkTooltip(event, d) {
    const sourceNode = currentData.nodes.find(n => n.id === d.source.id);
    const targetNode = currentData.nodes.find(n => n.id === d.target.id);

    const html = `
        <h6><i class="fas fa-link"></i> Relación</h6>
        <div><strong>Origen:</strong> ${sourceNode.name}</div>
        <div><strong>Tipo:</strong> <span class="badge" style="background-color: ${relationshipColors[d.type]}">${d.type}</span></div>
        <div><strong>Destino:</strong> ${targetNode.name}</div>
        ${d.description ? `<div class="mt-2"><small>${d.description}</small></div>` : ''}
        <div class="mt-1">
            <span class="badge bg-warning">Criticidad: ${d.criticality}/10</span>
        </div>
    `;

    tooltip
        .html(html)
        .style('left', (event.pageX + 15) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .classed('d-none', false);
}

/**
 * Oculta tooltip
 */
function hideTooltip() {
    tooltip.classed('d-none', true);
}

/**
 * Muestra información detallada del nodo en el panel
 */
function showNodeInfo(event, d) {
    event.stopPropagation();

    const panel = document.getElementById('node-info-panel');
    const content = document.getElementById('node-info-content');

    // Contar relaciones entrantes y salientes
    const incomingLinks = currentData.links.filter(l => l.target.id === d.id).length;
    const outgoingLinks = currentData.links.filter(l => l.source.id === d.id).length;

    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h5>${d.name}</h5>
                <p class="text-muted mb-2">${d.code}</p>
                <div class="mb-2">
                    <span class="badge" style="background-color: ${categoryColors[d.category]}">${d.category}</span>
                    <span class="badge bg-secondary">${d.status}</span>
                </div>
            </div>
            <div class="col-md-6 text-end">
                <div class="mb-2">
                    <strong>Criticidad:</strong><br>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" role="progressbar"
                             style="width: ${d.criticality * 10}%; background-color: ${getCriticalityColor(d.criticality)}"
                             aria-valuenow="${d.criticality}" aria-valuemin="0" aria-valuemax="10">
                            ${d.criticality}/10
                        </div>
                    </div>
                </div>
                <div>
                    <strong>Valor de Negocio:</strong><br>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar bg-success" role="progressbar"
                             style="width: ${d.business_value * 10}%"
                             aria-valuenow="${d.business_value}" aria-valuemin="0" aria-valuemax="10">
                            ${d.business_value}/10
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <hr>

        <div class="row">
            <div class="col-md-6">
                <p class="mb-1"><strong>Propietario:</strong> ${d.owner}</p>
                <p class="mb-1"><strong>Clasificación:</strong> ${d.classification}</p>
                ${d.department ? `<p class="mb-1"><strong>Departamento:</strong> ${d.department}</p>` : ''}
                ${d.location ? `<p class="mb-1"><strong>Ubicación:</strong> ${d.location}</p>` : ''}
            </div>
            <div class="col-md-6">
                <p class="mb-1"><strong>Confidencialidad:</strong> ${d.confidentiality}</p>
                <p class="mb-1"><strong>Integridad:</strong> ${d.integrity}</p>
                <p class="mb-1"><strong>Disponibilidad:</strong> ${d.availability}</p>
            </div>
        </div>

        <hr>

        <div class="row text-center">
            <div class="col-6">
                <h4 class="text-primary">${outgoingLinks}</h4>
                <small class="text-muted">Relaciones salientes</small>
            </div>
            <div class="col-6">
                <h4 class="text-success">${incomingLinks}</h4>
                <small class="text-muted">Relaciones entrantes</small>
            </div>
        </div>

        <div class="mt-3 text-end">
            <a href="/activos/${d.id}" class="btn btn-sm btn-primary">
                <i class="fas fa-external-link-alt"></i> Ver Detalles Completos
            </a>
        </div>
    `;

    panel.classList.remove('d-none');

    // Resaltar nodo seleccionado
    node.selectAll('circle').attr('opacity', n => n.id === d.id ? 1 : 0.3);
    link.attr('opacity', l => l.source.id === d.id || l.target.id === d.id ? 1 : 0.2);
}

/**
 * Navega a la página de detalles del activo
 */
function goToAsset(event, d) {
    window.location.href = `/activos/${d.id}`;
}

/**
 * Funciones de arrastre (drag)
 */
function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

/**
 * Configura los botones de acción
 */
function setupActionButtons() {
    // Centrar grafo
    document.getElementById('center-graph').addEventListener('click', () => {
        svg.transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity);
    });

    // Exportar como PNG
    document.getElementById('export-png').addEventListener('click', exportToPNG);

    // Pantalla completa
    document.getElementById('fullscreen').addEventListener('click', () => {
        const container = document.getElementById('graph-container');
        if (container.requestFullscreen) {
            container.requestFullscreen();
        }
    });
}

/**
 * Exporta el grafo como imagen PNG
 */
function exportToPNG() {
    const svgElement = document.getElementById('graph-svg');
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    canvas.width = svgElement.clientWidth;
    canvas.height = svgElement.clientHeight;

    img.onload = function() {
        ctx.drawImage(img, 0, 0);
        const pngFile = canvas.toDataURL('image/png');

        const downloadLink = document.createElement('a');
        downloadLink.download = 'grafo_activos_' + new Date().getTime() + '.png';
        downloadLink.href = pngFile;
        downloadLink.click();
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
}

/**
 * Muestra mensaje cuando no hay datos
 */
function showEmptyState() {
    const container = d3.select('#graph-svg');
    const width = container.node().clientWidth;
    const height = container.node().clientHeight;

    const g = container.append('g');

    // Icono
    g.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2 - 40)
        .attr('text-anchor', 'middle')
        .style('font-size', '64px')
        .style('fill', '#ddd')
        .style('font-family', 'Font Awesome 5 Free')
        .text('\uf542'); // Icono de grafo vacío

    // Mensaje principal
    g.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2 + 20)
        .attr('text-anchor', 'middle')
        .style('font-size', '18px')
        .style('fill', '#999')
        .style('font-weight', 'bold')
        .text('No hay activos que mostrar');

    // Submensaje
    g.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2 + 45)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .style('fill', '#bbb')
        .text('Intenta ajustar los filtros o crea nuevos activos');
}

/**
 * Redimensionar grafo cuando cambia el tamaño de la ventana
 */
window.addEventListener('resize', () => {
    if (currentData) {
        renderGraph(currentData);
    }
});
