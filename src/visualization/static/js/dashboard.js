// Dashboard map rendering and controls
let layoutData = null;
let agentLayer, buildingLayer, heatLayer;
let svg, mainGroup;
let xScale, yScale;
let zoom;

function initializeDashboard() {
    svg = d3.select('#cityMap');
    mainGroup = svg.append('g');
    agentLayer = mainGroup.append('g').attr('id', 'agents');
    buildingLayer = mainGroup.append('g').attr('id', 'buildings');
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
    buildingLayer.selectAll('*').remove();

    // Buildings
    buildingLayer.selectAll('rect.building')
        .data(layoutData.buildings)
        .enter()
        .append('rect')
        .attr('class', 'building')
        .attr('x', d => xScale(d.location.x) - 4)
        .attr('y', d => yScale(d.location.y) - 4)
        .attr('width', 8)
        .attr('height', 8)
        .attr('fill', '#888')
        .attr('stroke', '#000')
        .attr('stroke-width', 0.5);
}

async function fetchRealtime() {
    const res = await fetch('/api/realtime-data');
    const data = await res.json();
    updateAgents(data.agents);
    updateHeatMap(data.heat_map_data.stress);
    updateTimeline(data.simulation_state);
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
