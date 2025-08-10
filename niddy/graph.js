import { Link } from './models/models.js';
import { drawArrow, drawLabel } from './util/drawing.js';

d3.json('./out/graph.json')
    .then((data) => {
        window.addEventListener('resize', handleResize);
        simulateGraph(data);
    })
    .catch(console.error);

// Specify the color scale.
const color = d3.scaleOrdinal(d3.schemeCategory10);

const MARGIN_VALUE = 30;
const NODE_SIZE = 7;
const POINTER_GRAB_RANGE = 75;
const LINK_HIGHLIGHT_COLOR = d3.color('green');

let window_width = window.innerWidth - MARGIN_VALUE;
let window_height = window.innerHeight - MARGIN_VALUE;

let canvas = null;
let context = null;
let simulation = null;

let links = [];
let nodes = [];
let relations = {};

let selectedNode = null;
let selectedNodeLinks = [];

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
    relations = data.outbound;

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
            selectedNode = node;
            simulation.restart();
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

    if (closestNode?.id !== selectedNode?.id) {
        selectedNode = closestNode;
    }
    return closestNode;
}

//Highlight all outgoing links from node
function highlightLinks(node) {
    selectedNodeLinks = [];

    const relatedNodeIds = relations[node.id];

    if (!!relatedNodeIds) {
        const targetNodes = nodes.filter((node) =>
            relatedNodeIds.includes(node.id)
        );

        if (!!targetNodes) {
            targetNodes.forEach((targNode) => {
                const newLink = new Link(node, targNode);
                selectedNodeLinks.push(newLink);
            });
        }
    }
}

// Reheat the simulation when drag starts, and fix the subject position.
function dragStarted(event) {
    highlightLinks(event.subject);
    if (!event.active) simulation.alphaTarget(0.3).restart();
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
    // Add a drag behavior. The _subject_ identifies the closest node to the pointer
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

function draw() {
    context.clearRect(0, 0, window_width, window_height);

    links.forEach((link) => drawLink(link));
    selectedNodeLinks.forEach((sLink) =>
        drawArrow(context, sLink, 3, LINK_HIGHLIGHT_COLOR, NODE_SIZE + 2)
    );

    context.save();
    context.strokeStyle = '#fff';
    context.globalAlpha = 1;

    nodes.forEach((node) => drawNode(node));
    context.restore();
}

function drawLink(link, color = '#999') {
    context.save();
    context.globalAlpha = 0.6;
    context.strokeStyle = color;

    context.beginPath();
    context.moveTo(link.source.x, link.source.y);
    context.lineTo(link.target.x, link.target.y);

    context.stroke();
    context.restore();
}

function drawNode(node) {
    context.beginPath();

    context.moveTo(node.x + NODE_SIZE, node.y);
    context.arc(node.x, node.y, NODE_SIZE, 0, 2 * Math.PI);

    context.fillStyle = color(node.type);
    context.strokeStyle = '#fff';
    context.fill();
    context.stroke();
    context.restore();

    drawLabel(context, node, selectedNode, NODE_SIZE);
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
