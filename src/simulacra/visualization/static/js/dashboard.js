// Enhanced dashboard map rendering and controls
let svg;
let mainGroup;
let districtLayer;
let buildingLayer;
let agentLayer;
let heatLayer;
let xScale;
let yScale;
let zoom;

const dashboardState = {
    layout: null,
    lastRealtime: null,
    lastPopulationMetrics: null,
    heatMapType: 'stress',
    fetchIntervalMs: 2000,
    fetchTimer: null,
    roundHistory: []
};

let healthChart;
let occupancyChart;
let economicChart;
let stressChart;
let trendChart;

function initializeDashboard() {
    svg = d3.select('#cityMap');
    mainGroup = svg.append('g').attr('class', 'map-root');
    districtLayer = mainGroup.append('g').attr('id', 'districts');
    buildingLayer = mainGroup.append('g').attr('id', 'buildings');
    agentLayer = mainGroup.append('g').attr('id', 'agents');
    heatLayer = mainGroup.append('g').attr('id', 'heat');

    setupZoom();
    registerEventHandlers();
    initCharts();
    fetchLayout();
    fetchRealtime();

    const initialInterval = parseFloat(
        document.getElementById('updateInterval')?.value || '2'
    );
    setUpdateInterval(initialInterval);
}

function setupZoom() {
    zoom = d3.zoom()
        .scaleExtent([0.5, 10])
        .on('zoom', (event) => {
            mainGroup.attr('transform', event.transform);
        });
    svg.call(zoom);
    window.addEventListener('resize', handleResize);
}

function registerEventHandlers() {
    const agentBtn = document.getElementById('showAgents');
    const buildingBtn = document.getElementById('showBuildings');
    const heatBtn = document.getElementById('showHeatMap');
    const heatSelect = document.getElementById('heatMapType');
    const updateInput = document.getElementById('updateInterval');

    agentBtn?.addEventListener('click', () => toggleLayer(agentLayer, agentBtn));
    buildingBtn?.addEventListener('click', () => toggleLayer(buildingLayer, buildingBtn));
    heatBtn?.addEventListener('click', () => toggleLayer(heatLayer, heatBtn));

    heatSelect?.addEventListener('change', (event) => {
        dashboardState.heatMapType = event.target.value;
        if (dashboardState.lastRealtime) {
            const cells = dashboardState.lastRealtime.heat_map_data[
                dashboardState.heatMapType
            ] || [];
            updateHeatMap(cells, dashboardState.heatMapType);
        }
    });

    updateInput?.addEventListener('input', (event) => {
        const seconds = parseFloat(event.target.value);
        setUpdateInterval(seconds);
    });

    document.getElementById('pauseBtn')
        ?.addEventListener('click', () => sendSimulationControl('pause'));
    document.getElementById('resumeBtn')
        ?.addEventListener('click', () => sendSimulationControl('resume'));
    document.getElementById('stopBtn')
        ?.addEventListener('click', () => sendSimulationControl('stop'));

    document.getElementById('requestUpdate')
        ?.addEventListener('click', () => fetchRealtime());
}

function toggleLayer(layer, button) {
    const active = button.getAttribute('data-active') === 'true';
    button.setAttribute('data-active', active ? 'false' : 'true');
    button.classList.toggle('active', !active);
    layer.style('display', active ? 'none' : 'block');

    if (button.id === 'showHeatMap') {
        const legend = document.getElementById('heatMapLegend');
        if (legend) {
            legend.style.display = active ? 'none' : 'block';
        }
    }
}

async function fetchLayout() {
    try {
        const response = await fetch('/api/city-layout');
        if (!response.ok) {
            throw new Error(`Layout request failed (${response.status})`);
        }
        dashboardState.layout = await response.json();
        setupScales();
        renderLayout();
    } catch (error) {
        console.error('Failed to load city layout', error);
    }
}

function setupScales() {
    if (!dashboardState.layout) {
        return;
    }

    const { bounds } = dashboardState.layout;
    const { width, height } = getSvgDimensions();
    svg.attr('viewBox', `0 0 ${width} ${height}`);

    xScale = d3.scaleLinear()
        .domain([bounds.min_x, bounds.max_x])
        .range([0, width]);

    yScale = d3.scaleLinear()
        .domain([bounds.min_y, bounds.max_y])
        .range([height, 0]);
}

function getSvgDimensions() {
    const node = svg.node();
    const rect = node.getBoundingClientRect();
    const width = rect.width || node.parentNode.clientWidth || 960;
    const height = rect.height || 540;
    return { width, height };
}

function renderLayout() {
    if (!dashboardState.layout) {
        return;
    }

    districtLayer.selectAll('*').remove();
    buildingLayer.selectAll('*').remove();

    const plotsByDistrict = d3.group(
        dashboardState.layout.plots,
        (plot) => plot.district_id
    );

    dashboardState.layout.districts.forEach((district) => {
        const plots = plotsByDistrict.get(district.id) || [];
        const points = plots.map((plot) => [
            xScale(plot.location.x),
            yScale(plot.location.y)
        ]);
        let polygon = d3.polygonHull(points);

        if (!polygon && points.length) {
            const xs = points.map((point) => point[0]);
            const ys = points.map((point) => point[1]);
            polygon = [
                [Math.min(...xs) - 5, Math.min(...ys) - 5],
                [Math.max(...xs) + 5, Math.min(...ys) - 5],
                [Math.max(...xs) + 5, Math.max(...ys) + 5],
                [Math.min(...xs) - 5, Math.max(...ys) + 5]
            ];
        }

        if (polygon) {
            districtLayer.append('path')
                .attr('class', 'district')
                .attr('d', `M${polygon.map((point) => point.join(',')).join('L')}Z`)
                .attr('fill', district.color)
                .attr('fill-opacity', 0.12)
                .attr('stroke', district.color)
                .attr('stroke-width', 1.5)
                .attr('stroke-opacity', 0.65);
        }
    });

    const typeStyles = {
        ResidentialBuilding: { color: '#4ade80', shape: d3.symbolSquare },
        Employer: { color: '#38bdf8', shape: d3.symbolTriangle },
        LiquorStore: { color: '#a855f7', shape: d3.symbolWye },
        Casino: { color: '#f97316', shape: d3.symbolDiamond }
    };

    const symbol = d3.symbol().size(90);
    buildingLayer.selectAll('path.building')
        .data(dashboardState.layout.buildings)
        .enter()
        .append('path')
        .attr('class', 'building')
        .attr('d', (d) => symbol.type((typeStyles[d.type] || {}).shape || d3.symbolCircle)())
        .attr('transform', (d) => `translate(${xScale(d.location.x)}, ${yScale(d.location.y)})`)
        .attr('fill', (d) => (typeStyles[d.type] || {}).color || '#94a3b8')
        .attr('stroke', '#0f172a')
        .attr('stroke-width', 0.6)
        .attr('fill-opacity', 0.9);

    updateLegend(typeStyles);
}

async function fetchRealtime() {
    toggleUpdateSpinner(true);
    try {
        const response = await fetch('/api/realtime-data');
        if (!response.ok) {
            throw new Error(`Realtime request failed (${response.status})`);
        }
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }

        dashboardState.lastRealtime = data;
        updateConnectionStatus(true);
        updateLastUpdate(data.timestamp);
        updateSimulationStatus(data.simulation_state);
        updateSimulationTime(data.simulation_state);
        updateTopMetrics(data);
        updateAgents(data.agents);
        updateHeatMap(
            data.heat_map_data[dashboardState.heatMapType] || [],
            dashboardState.heatMapType
        );
        updateTimeline(data.simulation_state);
        updateStressChart(data.agents);
        updateHealthChart(data.population_metrics);
        updateOccupancyChart(data.buildings);
        updateEconomicChart(data.economic_indicators);
        updateTrendChart(data.round_metrics);
    } catch (error) {
        console.error('Failed to fetch realtime data', error);
        updateConnectionStatus(false);
    } finally {
        toggleUpdateSpinner(false);
    }
}

function updateTopMetrics(data) {
    const metrics = data.population_metrics;
    const simStats = data.simulation_state?.current_stats || {};

    const totalAgents = metrics?.total_agents
        ?? data.simulation_state?.total_agents
        ?? 0;
    setText('totalAgents', totalAgents.toLocaleString());

    const employmentRate = metrics?.employment_rate
        ?? simStats.employment_rate
        ?? 0;
    setText('employmentRate', formatPercent(employmentRate, 1));

    const housingRate = metrics
        ? 1 - (metrics.homelessness_rate ?? 0)
        : simStats.housing_rate ?? 0;
    setText('housingRate', formatPercent(housingRate, 1));

    const averageWealth = metrics?.mean_wealth
        ?? simStats.average_wealth
        ?? 0;
    setText('avgWealth', formatCurrency(averageWealth));

    updateMetricDelta(
        'agentsDelta',
        totalAgents,
        dashboardState.lastPopulationMetrics?.total_agents,
        'agents'
    );
    updateMetricDelta(
        'employmentDelta',
        employmentRate,
        dashboardState.lastPopulationMetrics?.employment_rate,
        'pts',
        true
    );
    updateMetricDelta(
        'housingDelta',
        housingRate,
        dashboardState.lastPopulationMetrics
            ? 1 - dashboardState.lastPopulationMetrics.homelessness_rate
            : undefined,
        'pts',
        true
    );
    updateMetricDelta(
        'wealthDelta',
        averageWealth,
        dashboardState.lastPopulationMetrics?.mean_wealth,
        'wealth'
    );

    if (metrics) {
        dashboardState.lastPopulationMetrics = metrics;
    }
}

function updateMetricDelta(id, current, previous, unit, isPercent = false) {
    const element = document.getElementById(id);
    if (!element) {
        return;
    }

    if (previous === undefined || previous === null) {
        element.textContent = 'Baseline';
        element.className = 'metric-delta text-muted';
        return;
    }

    const delta = current - previous;
    if (Math.abs(delta) < 1e-6) {
        element.textContent = 'No change';
        element.className = 'metric-delta text-muted';
        return;
    }

    const positive = delta > 0;
    element.className = `metric-delta ${positive ? 'text-success' : 'text-danger'}`;

    if (unit === 'wealth') {
        element.textContent = `${positive ? '+' : '−'}${formatCurrency(Math.abs(delta))}`;
        return;
    }

    if (unit === 'agents') {
        element.textContent = `${positive ? '+' : '−'}${Math.abs(delta).toFixed(0)} agents`;
        return;
    }

    if (isPercent) {
        const normalized = normalizePercent(delta);
        element.textContent = `${positive ? '+' : '−'}${Math.abs(normalized).toFixed(1)} pts`;
        return;
    }

    element.textContent = `${positive ? '+' : '−'}${Math.abs(delta).toFixed(1)} ${unit}`;
}

function updateSimulationStatus(state) {
    const indicator = document.getElementById('simulationStatus');
    const label = document.getElementById('simulationStatusText');
    if (!indicator || !label) {
        return;
    }

    indicator.classList.remove('status-running', 'status-paused', 'status-stopped');

    if (state?.is_running) {
        if (state.is_paused) {
            indicator.classList.add('status-paused');
            label.textContent = 'Paused';
        } else {
            indicator.classList.add('status-running');
            label.textContent = 'Running';
        }
    } else {
        indicator.classList.add('status-stopped');
        label.textContent = 'Stopped';
    }
}

function updateSimulationTime(state) {
    const element = document.getElementById('simulationTime');
    if (!element) {
        return;
    }

    const info = state?.time_info;
    if (!info) {
        element.textContent = '--';
        return;
    }

    element.textContent = `Month ${info.month}, Year ${info.year} • ` +
        `Round ${info.current_round}/${info.max_rounds}`;
}

function updateAgents(agents, instant = false) {
    if (!agentLayer || !agents) {
        return;
    }

    const tooltip = d3.select('#agentTooltip');
    const join = agentLayer.selectAll('path.agent')
        .data(agents, (agent) => agent.id);

    const entered = join.enter()
        .append('path')
        .attr('class', 'agent')
        .attr('fill', (d) => d.visual_properties?.color || '#38bdf8')
        .attr('stroke', '#0f172a')
        .attr('stroke-width', 0.7)
        .attr('opacity', 0);

    const merged = entered.merge(join);
    merged
        .on('mousemove', (event, d) => showAgentTooltip(tooltip, event, d))
        .on('mouseleave', () => hideAgentTooltip(tooltip))
        .transition()
        .duration(instant ? 0 : 900)
        .ease(d3.easeCubicOut)
        .attr('transform', (d) => `translate(${xScale(d.location.x)}, ${yScale(d.location.y)})`)
        .attr('d', (d) => createAgentSymbol(d));

    entered.transition()
        .duration(instant ? 0 : 600)
        .attr('opacity', 0.9);

    join.exit()
        .transition()
        .duration(instant ? 0 : 450)
        .attr('opacity', 0)
        .remove();
}

function createAgentSymbol(agent) {
    const shape = (agent.visual_properties?.shape || 'circle').toLowerCase();
    let symbolType = d3.symbolCircle;
    if (shape === 'square') {
        symbolType = d3.symbolSquare;
    } else if (shape === 'triangle') {
        symbolType = d3.symbolTriangle;
    }

    const size = Math.max(agent.visual_properties?.size || 4, 3);
    return d3.symbol()
        .type(symbolType)
        .size(Math.pow(size * 2.2, 2))();
}

function showAgentTooltip(tooltip, event, agent) {
    if (!tooltip) {
        return;
    }

    const html = [
        `<div class="fw-semibold mb-1">Agent ${agent.id}</div>`,
        `<div class="small text-muted">Wealth: ${formatCurrency(agent.state?.wealth ?? 0)}</div>`,
        `<div class="small text-muted">Stress: ${formatPercent(agent.state?.stress ?? 0, 0)}</div>`,
        `<div class="small text-muted">Mood: ${formatPercent(agent.state?.mood ?? 0, 0)}</div>`,
        `<div class="small text-muted">Self-control: ${
            formatPercent(agent.state?.self_control ?? 0, 0)
        }</div>`,
        `<div class="small text-muted">${agent.state?.employed ? 'Employed' : 'Seeking work'} • ` +
            `${agent.state?.housed ? 'Housed' : 'Unhoused'}</div>`
    ].join('');

    tooltip.html(html)
        .style('left', `${event.pageX + 14}px`)
        .style('top', `${event.pageY - 28}px`)
        .classed('visible', true);
}

function hideAgentTooltip(tooltip) {
    tooltip?.classed('visible', false);
}

function updateHeatMap(cells, type, instant = false) {
    const heatButton = document.getElementById('showHeatMap');
    const active = heatButton?.getAttribute('data-active') !== 'false';
    const legend = document.getElementById('heatMapLegend');

    if (legend) {
        legend.style.display = active ? 'block' : 'none';
    }

    if (!active) {
        heatLayer.selectAll('rect.heat').remove();
        return;
    }

    if (!cells || !cells.length) {
        heatLayer.selectAll('rect.heat')
            .transition()
            .duration(instant ? 0 : 300)
            .attr('opacity', 0)
            .remove();
        updateHeatLegend(type, [0, 1]);
        return;
    }

    const values = cells.map((cell) => cell.value ?? 0);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const scale = getHeatColorScale(type, [min, max]);
    updateHeatLegend(type, [min, max]);

    const cellSize = Math.max(6, Math.min(22, (xScale(1) - xScale(0)) * 0.7));
    const selection = heatLayer.selectAll('rect.heat')
        .data(cells, (cell) => `${cell.x},${cell.y}`);

    selection.enter()
        .append('rect')
        .attr('class', 'heat')
        .attr('width', cellSize)
        .attr('height', cellSize)
        .attr('opacity', 0)
        .attr('x', (d) => xScale(d.x) - cellSize / 2)
        .attr('y', (d) => yScale(d.y) - cellSize / 2)
        .attr('fill', (d) => scale(d.value ?? 0))
        .transition()
        .duration(instant ? 0 : 600)
        .attr('opacity', 0.7);

    selection.transition()
        .duration(instant ? 0 : 600)
        .attr('width', cellSize)
        .attr('height', cellSize)
        .attr('x', (d) => xScale(d.x) - cellSize / 2)
        .attr('y', (d) => yScale(d.y) - cellSize / 2)
        .attr('fill', (d) => scale(d.value ?? 0))
        .attr('opacity', 0.7);

    selection.exit()
        .transition()
        .duration(instant ? 0 : 400)
        .attr('opacity', 0)
        .remove();
}

function getHeatColorScale(type, domain) {
    const [min, max] = domain;
    const adjustedMax = max <= min ? min + 1 : max;
    const scale = d3.scaleSequential();

    if (type === 'wealth') {
        scale.interpolator(d3.interpolateViridis);
    } else if (type === 'addiction') {
        scale.interpolator(d3.interpolatePlasma);
    } else {
        scale.interpolator(d3.interpolateTurbo);
    }

    scale.domain([min, adjustedMax]);
    return scale;
}

function updateHeatLegend(type, domain) {
    const scaleBar = document.getElementById('heatScaleBar');
    const minLabel = document.getElementById('heatScaleMin');
    const maxLabel = document.getElementById('heatScaleMax');
    if (!scaleBar || !minLabel || !maxLabel) {
        return;
    }

    const gradients = {
        stress: 'linear-gradient(90deg,#22d3ee,#fde047,#fb923c,#ef4444)',
        addiction: 'linear-gradient(90deg,#6366f1,#ec4899,#f97316)',
        wealth: 'linear-gradient(90deg,#16a34a,#84cc16,#facc15,#f97316)'
    };

    scaleBar.style.background = gradients[type] || gradients.stress;
    minLabel.textContent = formatHeatValue(domain[0], type);
    maxLabel.textContent = formatHeatValue(domain[1], type);
}

function formatHeatValue(value, type) {
    if (value === undefined || value === null || Number.isNaN(value)) {
        return '--';
    }

    if (type === 'wealth') {
        return formatCurrency(value);
    }

    return formatPercent(value, 0);
}

function updateLegend(typeStyles) {
    const districtLegend = d3.select('#districtLegend');
    const buildingLegend = d3.select('#buildingLegend');

    if (!districtLegend.empty()) {
        districtLegend.html('');
        dashboardState.layout.districts.forEach((district) => {
            districtLegend.append('div')
                .attr('class', 'legend-item')
                .html(
                    `<div class="legend-color" style="background:${district.color}"></div>` +
                    `<small>${district.name}</small>`
                );
        });
    }

    if (!buildingLegend.empty()) {
        buildingLegend.html('');
        const seen = new Set();
        dashboardState.layout.buildings.forEach((building) => {
            seen.add(building.type);
        });

        Array.from(seen).forEach((type) => {
            const style = typeStyles[type] || { color: '#94a3b8', shape: d3.symbolCircle };
            const path = d3.symbol()
                .type(style.shape || d3.symbolCircle)
                .size(120)();
            buildingLegend.append('div')
                .attr('class', 'legend-item')
                .html(
                    `<svg width="22" height="22">` +
                    `<path d="${path}" fill="${style.color || '#94a3b8'}" ` +
                    `stroke="#0f172a" stroke-width="1"></path></svg>` +
                    `<small>${toTitleCase(type)}</small>`
                );
        });
    }
}

function initCharts() {
    if (!window.Chart) {
        return;
    }

    Chart.defaults.color = '#cbd5f5';
    Chart.defaults.font.family = 'Inter, "Segoe UI", sans-serif';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 10;

    const healthCtx = document.getElementById('healthChart');
    if (healthCtx) {
        healthChart = new Chart(healthCtx, {
            type: 'doughnut',
            data: {
                labels: [
                    'Balanced',
                    'High stress',
                    'Addiction risk',
                    'Problem gambling'
                ],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#22c55e',
                        '#f97316',
                        '#a855f7',
                        '#ef4444'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    const occupancyCtx = document.getElementById('occupancyChart');
    if (occupancyCtx) {
        occupancyChart = new Chart(occupancyCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Occupancy rate',
                    data: [],
                    backgroundColor: '#38bdf8',
                    borderRadius: 6
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { maxRotation: 0 } },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => `${value}%`
                        }
                    }
                }
            }
        });
    }

    const economicCtx = document.getElementById('economicChart');
    if (economicCtx) {
        economicChart = new Chart(economicCtx, {
            type: 'radar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Economic indicators',
                    data: [],
                    backgroundColor: 'rgba(56,189,248,0.18)',
                    borderColor: '#38bdf8',
                    pointBackgroundColor: '#38bdf8',
                    pointBorderColor: '#0f172a'
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        suggestedMax: 100,
                        ticks: { display: false },
                        angleLines: { color: 'rgba(148,163,184,0.2)' },
                        grid: { color: 'rgba(148,163,184,0.2)' }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    const stressCtx = document.getElementById('stressChart');
    if (stressCtx) {
        stressChart = new Chart(stressCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Agents',
                    data: [],
                    backgroundColor: 'rgba(239,68,68,0.55)',
                    borderRadius: 4
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: 'Stress band' },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Agent count' }
                    }
                }
            }
        });
    }

    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Employment rate',
                        data: [],
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34,197,94,0.18)',
                        tension: 0.35,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Average stress',
                        data: [],
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56,189,248,0.16)',
                        tension: 0.35,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Mean wealth',
                        data: [],
                        borderColor: '#f97316',
                        backgroundColor: 'rgba(249,115,22,0.15)',
                        tension: 0.25,
                        fill: false,
                        borderDash: [5, 5],
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => `${value}%`
                        },
                        grid: { color: 'rgba(148,163,184,0.2)' }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: {
                            callback: (value) => `$${Math.round(value)}`
                        }
                    }
                }
            }
        });
    }
}

function updateHealthChart(metrics) {
    if (!healthChart || !metrics) {
        return;
    }

    const stressRate = metrics.high_stress_rate ?? 0;
    const addictionRate = metrics.addiction_rate ?? 0;
    const gamblingRate = metrics.problem_gambling_rate ?? 0;
    const combined = stressRate + addictionRate + gamblingRate;
    const balanced = Math.max(0, 1 - Math.min(1, combined));

    healthChart.data.datasets[0].data = [
        normalizePercent(balanced) ?? 0,
        normalizePercent(stressRate) ?? 0,
        normalizePercent(addictionRate) ?? 0,
        normalizePercent(gamblingRate) ?? 0
    ];
    healthChart.update('none');

    const summary = document.getElementById('healthSummary');
    if (summary) {
        summary.textContent = `High stress ${formatPercent(stressRate, 1)}`;
    }
}

function updateOccupancyChart(buildings) {
    if (!occupancyChart || !buildings || !buildings.length) {
        const summary = document.getElementById('occupancySummary');
        if (summary) {
            summary.textContent = 'No occupancy data';
        }
        return;
    }

    const grouped = new Map();
    buildings.forEach((building) => {
        const type = building.building_type || 'Building';
        const rate = building.occupancy_rate ?? 0;
        if (!grouped.has(type)) {
            grouped.set(type, []);
        }
        grouped.get(type).push(rate);
    });

    const labels = [];
    const values = [];
    grouped.forEach((rates, type) => {
        labels.push(toTitleCase(type));
        const avg = rates.reduce((sum, value) => sum + value, 0) / rates.length;
        values.push(normalizePercent(avg) ?? 0);
    });

    occupancyChart.data.labels = labels;
    occupancyChart.data.datasets[0].data = values;
    occupancyChart.update('none');

    const average = values.length
        ? values.reduce((sum, value) => sum + value, 0) / values.length
        : 0;
    const summary = document.getElementById('occupancySummary');
    if (summary) {
        summary.textContent = `Avg occupancy ${average.toFixed(1)}%`;
    }
}

function updateEconomicChart(summary) {
    const badge = document.getElementById('economicSummary');
    if (!economicChart || !summary) {
        if (badge) {
            badge.textContent = 'No economic data';
        }
        return;
    }

    const indicators = summary.indicators || {};
    const labels = Object.keys(indicators);
    if (!labels.length) {
        if (badge) {
            badge.textContent = 'No economic data';
        }
        return;
    }

    economicChart.data.labels = labels.map((label) => toTitleCase(label));
    economicChart.data.datasets[0].data = labels.map((key) => {
        const value = indicators[key];
        return normalizePercent(value) ?? 0;
    });
    economicChart.update('none');

    const jobScore = summary.job_market?.conditions_score;
    const housingScore = summary.housing_market?.conditions_score;
    const growth = indicators.economic_growth ?? 0;
    const parts = [];
    if (jobScore !== undefined) {
        parts.push(`Jobs ${jobScore.toFixed(1)}`);
    }
    if (housingScore !== undefined) {
        parts.push(`Housing ${housingScore.toFixed(1)}`);
    }
    parts.push(`Growth ${formatPercent(growth, 1)}`);
    if (badge) {
        badge.textContent = parts.join(' • ');
    }
}

function updateStressChart(agents) {
    if (!stressChart || !agents) {
        const summary = document.getElementById('stressSummary');
        if (summary) {
            summary.textContent = 'No agent data';
        }
        return;
    }

    const bins = new Array(10).fill(0);
    let totalStress = 0;
    agents.forEach((agent) => {
        const stress = Math.max(0, Math.min(agent.state?.stress ?? 0, 1));
        totalStress += stress;
        const index = Math.min(9, Math.floor(stress * 10));
        bins[index] += 1;
    });

    stressChart.data.labels = bins.map((_, index) => {
        const start = (index / 10).toFixed(1);
        const end = ((index + 1) / 10).toFixed(1);
        return `${start}-${end}`;
    });
    stressChart.data.datasets[0].data = bins;
    stressChart.update('none');

    const average = agents.length ? totalStress / agents.length : 0;
    const summary = document.getElementById('stressSummary');
    if (summary) {
        summary.textContent = `Avg stress ${formatPercent(average, 1)}`;
    }
}

function updateTrendChart(roundMetrics) {
    if (!trendChart || !roundMetrics) {
        return;
    }

    const record = {
        label: formatTrendLabel(roundMetrics.timestamp, roundMetrics.round),
        employment_rate: roundMetrics.employment_rate ?? 0,
        mean_stress: roundMetrics.mean_stress ?? 0,
        mean_wealth: roundMetrics.mean_wealth ?? 0,
        round: roundMetrics.round ?? dashboardState.roundHistory.length + 1
    };

    dashboardState.roundHistory.push(record);
    if (dashboardState.roundHistory.length > 60) {
        dashboardState.roundHistory.shift();
    }

    trendChart.data.labels = dashboardState.roundHistory.map((item) => item.label);
    trendChart.data.datasets[0].data = dashboardState.roundHistory.map((item) => {
        return normalizePercent(item.employment_rate) ?? 0;
    });
    trendChart.data.datasets[1].data = dashboardState.roundHistory.map((item) => {
        return normalizePercent(item.mean_stress) ?? 0;
    });
    const wealthValues = dashboardState.roundHistory.map((item) => item.mean_wealth ?? 0);
    trendChart.data.datasets[2].data = wealthValues;

    const maxWealth = Math.max(...wealthValues, 0);
    trendChart.options.scales.y1.suggestedMax = maxWealth * 1.15 || 100;
    trendChart.update('none');

    updateTrendSummary(record);
}

function updateTrendSummary(record) {
    const badge = document.getElementById('trendSummary');
    if (!badge || !record) {
        return;
    }

    badge.textContent = `Round ${record.round} • ` +
        `Employment ${formatPercent(record.employment_rate, 1)}`;
}

function updateTimeline(state) {
    const slider = document.getElementById('timelineSlider');
    const label = document.getElementById('timelineValue');
    const info = state?.time_info;
    if (!slider || !label || !info) {
        return;
    }

    const progress = state.months_completed + (info.round_progress ?? 0);
    slider.max = Math.max(Number(slider.max) || 0, progress + 1);
    slider.value = progress;

    label.textContent = `Month ${info.month} of Year ${info.year} • ` +
        `Round ${info.current_round}/${info.max_rounds}`;
}

function setUpdateInterval(seconds) {
    const safeSeconds = Number.isFinite(seconds) ? Math.max(0.5, seconds) : 2;
    dashboardState.fetchIntervalMs = safeSeconds * 1000;

    const badge = document.getElementById('intervalValue');
    if (badge) {
        badge.textContent = `${safeSeconds.toFixed(1)} s`;
    }

    if (dashboardState.fetchTimer) {
        clearInterval(dashboardState.fetchTimer);
    }
    dashboardState.fetchTimer = setInterval(
        () => fetchRealtime(),
        dashboardState.fetchIntervalMs
    );
}

async function sendSimulationControl(action) {
    const badge = document.getElementById('controlStatus');
    if (!badge) {
        return;
    }

    try {
        badge.textContent = 'Sending…';
        badge.className = 'badge bg-info bg-opacity-25 text-info';
        const response = await fetch('/api/simulation-control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        const payload = await response.json();
        if (!response.ok || payload.error) {
            throw new Error(payload.error || `Status ${response.status}`);
        }

        badge.textContent = payload.status
            ? toTitleCase(payload.status)
            : 'Updated';
        badge.className = 'badge bg-success bg-opacity-25 text-success';
        setTimeout(resetControlBadge, 2500);
        fetchRealtime();
    } catch (error) {
        console.error('Simulation control failed', error);
        badge.textContent = 'Error';
        badge.className = 'badge bg-danger bg-opacity-25 text-danger';
        setTimeout(resetControlBadge, 3500);
    }
}

function resetControlBadge() {
    const badge = document.getElementById('controlStatus');
    if (!badge) {
        return;
    }
    badge.textContent = 'Ready';
    badge.className = 'badge bg-secondary bg-opacity-25 text-secondary';
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    if (!status) {
        return;
    }

    status.classList.toggle('connected', connected);
    status.classList.toggle('disconnected', !connected);

    if (connected) {
        status.innerHTML = '<i class="fas fa-wifi"></i><span class="ms-1">Live</span>';
    } else {
        status.innerHTML = '<i class="fas fa-exclamation-triangle"></i>' +
            '<span class="ms-1">Disconnected</span>';
    }
}

function toggleUpdateSpinner(show) {
    const spinner = document.getElementById('updateSpinner');
    const wrapper = document.getElementById('lastUpdateWrapper');
    if (!spinner || !wrapper) {
        return;
    }

    spinner.classList.toggle('d-none', !show);
    wrapper.classList.toggle('updating', show);
}

function updateLastUpdate(timestamp) {
    const element = document.getElementById('lastUpdate');
    if (!element) {
        return;
    }

    if (!timestamp) {
        element.textContent = 'Waiting for data…';
        return;
    }

    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
        element.textContent = 'Updated just now';
        return;
    }

    element.textContent = `Updated ${date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })}`;
}

async function exportMap() {
    const layout = dashboardState.layout;
    const response = await fetch('/api/realtime-data');
    const realtime = await response.json();
    const data = { layout, realtime };
    const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'map_snapshot.json';
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function normalizePercent(value) {
    if (value === undefined || value === null || Number.isNaN(value)) {
        return null;
    }
    if (Math.abs(value) <= 1) {
        return value * 100;
    }
    return value;
}

function formatPercent(value, digits = 0) {
    const normalized = normalizePercent(value);
    if (normalized === null) {
        return '--';
    }
    return `${normalized.toFixed(digits)}%`;
}

function formatCurrency(value) {
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    });
    return formatter.format(value ?? 0);
}

function formatTrendLabel(timestamp, round) {
    if (timestamp) {
        const date = new Date(timestamp);
        if (!Number.isNaN(date.getTime())) {
            const month = date.getMonth() + 1;
            const day = date.getDate();
            const time = date.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
            return `${month}/${day} ${time}`;
        }
    }
    if (round !== undefined) {
        return `Round ${round}`;
    }
    return `#${dashboardState.roundHistory.length + 1}`;
}

function toTitleCase(value) {
    return String(value)
        .replace(/([A-Z])/g, ' $1')
        .replace(/[_-]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
        .replace(/^./, (char) => char.toUpperCase());
}

function handleResize() {
    if (!dashboardState.layout) {
        return;
    }

    setupScales();
    renderLayout();
    if (dashboardState.lastRealtime) {
        updateAgents(dashboardState.lastRealtime.agents, true);
        updateHeatMap(
            dashboardState.lastRealtime.heat_map_data[dashboardState.heatMapType] || [],
            dashboardState.heatMapType,
            true
        );
    }
}

if (typeof module !== 'undefined') {
    module.exports = { initializeDashboard };
}
