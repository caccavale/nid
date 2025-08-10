d3.json('./out/graph.json')
    .then((data) => {
        window.addEventListener('resize', handleResize);
        simulateGraph(data);
    })
    .catch(console.error);

const MARGIN_VALUE = 30;
const NODE_SIZE = 7;
const POINTER_GRAB_RANGE = 75;

let window_width = window.innerWidth - MARGIN_VALUE;
let window_height = window.innerHeight - MARGIN_VALUE;

let canvas = null;
let context = null;
let simulation = null;

let links = [];
let nodes = [];
let relations = {};
let currentNodeToLabel = null;

const distanceToNodeFunction = (sourceCoords, nodeCoords) => {
    const [x, y] = sourceCoords;
    const [nodeX, nodeY] = nodeCoords;
    return (
        Math.pow(x - (nodeX + NODE_SIZE * 2), 2) +
        Math.pow(y - (nodeY + NODE_SIZE), 2)
    );
};

function handleResize() {
    window_width = window.innerWidth - MARGIN_VALUE;
    window_height = window.innerHeight - MARGIN_VALUE;
    canvas?.attr('width', window_width).attr('height', window_height);
}

function setupData(data) {
    // The force simulation mutates links and nodes, so create a copy
    // so that re-evaluating this cell produces the same result.
    links = data.links.map((d) => ({ ...d }));
    nodes = data.nodes.map((d) => ({ ...d }));
    relations = data.relations;

    nodes.forEach((node) => {
        node.x = window_width;
        node.y = window_height;
    });

    canvas = d3
        .select('canvas')
        .attr('width', window_width)
        .attr('height', window_height)
        .on('mousemove', handleMouseMove);

    context = canvas.node().getContext('2d');
}

function handleMouseMove(event) {
    nodes.forEach((node) => {
        if (isOnTopOfNode(event, node)) {
            currentNodeToLabel = node;
            simulation.alpha(0).restart();
        }
    });
}

function isOnTopOfNode(event, node) {
    const [px, py] = d3.pointer(event, canvas);
    const distanceSquared = distanceToNodeFunction([px, py], [node.x, node.y]);

    return distanceSquared < POINTER_GRAB_RANGE;
}

function findClosestNodeToTarget(event) {
    let closestNode = null;

    nodes.forEach((node) => {
        if (isOnTopOfNode(event, node)) {
            closestNode = node;
        }
    });

    if (closestNode?.id !== currentNodeToLabel?.id) {
        currentNodeToLabel = closestNode;
    }
    return closestNode;
}

// Reheat the simulation when drag starts, and fix the subject position.
function dragStarted(event) {
    if (!event.active) simulation.alphaTarget(0.7).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

// Update the subject (dragged node) position during drag.
function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

// Restore the target alpha so the simulation cools after dragging ends.
// Unfix the subject position now that it’s no longer being dragged.
function dragEnded(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

function setupDrag() {
    // Add a drag behavior. The _subject_ identifies the closest node to the pointer,
    // conditional on the distance being less than 20 pixels.
    d3.select(canvas)
        .node()
        .call(
            d3
                .drag()
                .subject(findClosestNodeToTarget)
                .on('start', dragStarted)
                .on('drag', dragged)
                .on('end', dragEnded)
        );
}

function drawLabel(node) {
    if (node.id === currentNodeToLabel?.id) {
        context.font = '14px bold-serif';
        context.fillStyle = 'black'; // Set text color
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(node.id, node.x - 5, node.y - (NODE_SIZE + 5));
        context.strokeStyle = d3.color('orange');
        context.stroke();
        context.restore();
    }
}

function draw() {
    // Specify the color scale.
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    context.clearRect(0, 0, window_width, window_height);

    context.save();
    context.globalAlpha = 0.6;
    context.strokeStyle = '#999';
    context.beginPath();
    links.forEach(drawLink);
    context.stroke();
    context.restore();

    context.save();
    context.strokeStyle = '#fff';
    context.globalAlpha = 1;
    nodes.forEach((node) => {
        context.beginPath();
        drawNode(node);
        context.fillStyle = color(node.group);
        context.strokeStyle = '#fff';
        context.fill();
        context.stroke();
        context.restore();
        drawLabel(node);
    });
    context.restore();
}

function drawLink(d) {
    context.moveTo(d.source.x, d.source.y);
    context.lineTo(d.target.x, d.target.y);
}

function drawNode(d) {
    context.moveTo(d.x + NODE_SIZE, d.y);
    context.arc(d.x, d.y, NODE_SIZE, 0, 2 * Math.PI);
}

function simulateGraph(data) {
    setupData(data);

    // Create a simulation with several forces.
    simulation = d3
        .forceSimulation(nodes)
        .force(
            'link',
            d3
                .forceLink(links)
                .id((d) => d.id)
                .distance(30)
        )
        .force('charge', d3.forceManyBody().strength(-6))
        .force('x', d3.forceX(window_width / 2))
        .force('y', d3.forceY(window_height / 2))
        .on('tick', draw);

    setupDrag();
}
