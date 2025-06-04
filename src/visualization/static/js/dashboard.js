// Dashboard map rendering and controls
let layoutData = null;
let districtLayer, buildingLayer, agentLayer, heatLayer;
let stressChart;
let svg, mainGroup;
let xScale, yScale;
let zoom;

function initializeDashboard() {
    svg = d3.select('#cityMap');
    mainGroup = svg.append('g');
    districtLayer = mainGroup.append('g').attr('id', 'districts');
    buildingLayer = mainGroup.append('g').attr('id', 'buildings');
    agentLayer = mainGroup.append('g').attr('id', 'agents');
    heatLayer = mainGroup.append('g').attr('id', 'heat');

    zoom = d3.zoom().scaleExtent([0.5, 8]).on('zoom', (event) => {
        mainGroup.attr('transform', event.transform);
    });
    svg.call(zoom);

    document.getElementById('showAgents').addEventListener('click', () => toggleLayer(agentLayer, 'showAgents'));
    document.getElementById('showBuildings').addEventListener('click', () => toggleLayer(buildingLayer, 'showBuildings'));
    document.getElementById('showHeatMap').addEventListener('click', () => toggleLayer(heatLayer, 'showHeatMap'));

    fetchLayout();
    fetchRealtime();
    initStressChart();
    setInterval(fetchRealtime, 2000);
}

function toggleLayer(layer, btnId) {
    const btn = document.getElementById(btnId);
    const active = btn.getAttribute('data-active') === 'true';
    btn.setAttribute('data-active', active ? 'false' : 'true');
    btn.classList.toggle('active', !active);
    layer.style('display', active ? 'none' : 'block');
}

async function fetchLayout() {
    const res = await fetch('/api/city-layout');
    layoutData = await res.json();
    setupScales();
    renderLayout();
}

function setupScales() {
    const {bounds} = layoutData;
    xScale = d3.scaleLinear().domain([bounds.min_x, bounds.max_x]).range([0, parseInt(svg.attr('width'))]);
    yScale = d3.scaleLinear().domain([bounds.min_y, bounds.max_y]).range([parseInt(svg.attr('height')), 0]);
}

function renderLayout() {
    districtLayer.selectAll('*').remove();
    buildingLayer.selectAll('*').remove();

    // --- Draw district boundaries ---
    const plotsByDistrict = d3.group(layoutData.plots, p => p.district_id);
    layoutData.districts.forEach(district => {
        const plots = plotsByDistrict.get(district.id) || [];
        const points = plots.map(p => [xScale(p.location.x), yScale(p.location.y)]);
        let polygon = d3.polygonHull(points);

        if (!polygon && points.length) {
            const xs = points.map(p => p[0]);
            const ys = points.map(p => p[1]);
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
                .attr('d', 'M' + polygon.map(p => p.join(',')).join('L') + 'Z')
                .attr('fill', district.color)
                .attr('fill-opacity', 0.1)
                .attr('stroke', district.color)
                .attr('stroke-width', 1.5);
        }
    });

    // --- Draw buildings ---
    const typeStyles = {
        'ResidentialBuilding': { color: '#4caf50', shape: d3.symbolSquare },
        'Employer': { color: '#2196f3', shape: d3.symbolTriangle },
        'LiquorStore': { color: '#9c27b0', shape: d3.symbolWye },
        'Casino': { color: '#ff9800', shape: d3.symbolDiamond }
    };

    const symbol = d3.symbol().size(64);

    buildingLayer.selectAll('path.building')
        .data(layoutData.buildings)
        .enter()
        .append('path')
        .attr('class', 'building')
        .attr('d', d => symbol.type((typeStyles[d.type] || {}).shape || d3.symbolCircle)())
        .attr('transform', d => `translate(${xScale(d.location.x)}, ${yScale(d.location.y)})`)
        .attr('fill', d => (typeStyles[d.type] || {}).color || '#888')
        .attr('stroke', '#000')
        .attr('stroke-width', 0.5);

    updateLegend(typeStyles);
}

async function fetchRealtime() {
    const res = await fetch('/api/realtime-data');
    const data = await res.json();
    updateAgents(data.agents);
    updateHeatMap(data.heat_map_data.stress);
    updateTimeline(data.simulation_state);
    updateStressChart(data.agents);
}

function updateAgents(agents) {
    const tooltip = d3.select('#agentTooltip');
    const circles = agentLayer.selectAll('circle.agent').data(agents, d => d.id);

    circles.enter()
        .append('circle')
        .attr('class', 'agent')
        .attr('r', d => d.visual_properties.size)
        .attr('fill', d => d.visual_properties.color)
        .merge(circles)
        .attr('cx', d => xScale(d.location.x))
        .attr('cy', d => yScale(d.location.y))
        .on('mouseover', (event, d) => {
            tooltip.style('opacity', 1)
                   .html(`Agent ${d.id}<br>Stress: ${d.state.stress.toFixed(2)}`)
                   .style('left', (event.pageX + 10) + 'px')
                   .style('top', (event.pageY - 20) + 'px');
        })
        .on('mouseout', () => tooltip.style('opacity', 0));

    circles.exit().remove();
}

function updateHeatMap(cells) {
    const color = d3.scaleSequential(d3.interpolateYlOrRd).domain([0, 1]);
    const rects = heatLayer.selectAll('rect.heat').data(cells, d => `${d.x},${d.y}`);

    rects.enter()
        .append('rect')
        .attr('class', 'heat')
        .attr('width', 10)
        .attr('height', 10)
        .merge(rects)
        .attr('x', d => xScale(d.x) - 5)
        .attr('y', d => yScale(d.y) - 5)
        .attr('fill', d => color(d.value))
        .attr('opacity', 0.6);

    rects.exit().remove();
}

function initStressChart() {
    const ctx = document.getElementById('stressChart');
    if (ctx && window.Chart) {
        stressChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Agents',
                    data: [],
                    backgroundColor: 'rgba(255,99,132,0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: 'Stress' } },
                    y: { beginAtZero: true, title: { display: true, text: 'Count' } }
                }
            }
        });
    }
}

function updateStressChart(agents) {
    if (!stressChart || !agents) return;
    const bins = new Array(10).fill(0);
    agents.forEach(a => {
        const idx = Math.min(9, Math.floor(a.state.stress * 10));
        bins[idx] += 1;
    });
    stressChart.data.labels = bins.map((_, i) => `${(i/10).toFixed(1)}-${((i+1)/10).toFixed(1)}`);
    stressChart.data.datasets[0].data = bins;
    stressChart.update('none');
}

function updateLegend(typeStyles) {
    const districtLegend = d3.select('#districtLegend');
    const buildingLegend = d3.select('#buildingLegend');

    if (!districtLegend.empty()) {
        districtLegend.html('');
        layoutData.districts.forEach(d => {
            districtLegend.append('div')
                .attr('class', 'legend-item')
                .html(`<div class="legend-color" style="background:${d.color}"></div><small>${d.name}</small>`);
        });
    }

    if (!buildingLegend.empty()) {
        buildingLegend.html('');
        const seen = new Set();
        layoutData.buildings.forEach(b => seen.add(b.type));
        Array.from(seen).forEach(t => {
            const style = typeStyles[t] || {color:'#888', shape:d3.symbolCircle};
            const path = d3.symbol().type(style.shape).size(100)();
            buildingLegend.append('div')
                .attr('class', 'legend-item')
                .html(`<svg width="20" height="20"><path d="${path}" fill="${style.color}" stroke="#000" stroke-width="1"></path></svg><small>${t}</small>`);
        });
    }
}

function updateTimeline(state) {
    const slider = document.getElementById('timelineSlider');
    const span = document.getElementById('timelineValue');
    if (!state || !slider) return;
    const progress = state.time_info.round_progress + state.months_completed;
    slider.value = progress;
    span.textContent = `Month ${state.time_info.month} Round ${state.time_info.current_round}`;
}

async function exportMap() {
    const layout = layoutData;
    const res = await fetch('/api/realtime-data');
    const realtime = await res.json();
    const data = {layout, realtime};
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'map_snapshot.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

if (typeof module !== 'undefined') {
    module.exports = { initializeDashboard };
}
