function closestPointOnCircleEdge(source, target, radius) {
    const vx = source.x - target.x;
    const vy = source.y - target.y;
    const distance = Math.hypot(vx, vy);
    if (distance === 0)
        throw new Error(
            'Source and target are identical — direction undefined.'
        );
    const unitx = vx / distance;
    const unity = vy / distance;
    return { x: target.x + unitx * radius, y: target.y + unity * radius };
}

export function drawArrow(
    context,
    link,
    arrowWidth,
    color = '#999',
    node_size
) {
    //variables to be used when creating the arrow
    let headlen = 10;
    let angle = Math.atan2(
        link.target.y - link.source.y,
        link.target.x - link.source.x
    );

    const newTargetCoords = closestPointOnCircleEdge(
        link.source,
        link.target,
        node_size
    );
    const [targetX, targetY] = [newTargetCoords.x, newTargetCoords.y];

    context.save();
    context.globalAlpha = 0.6;
    context.strokeStyle = color;

    //starting path of the arrow from the start square to the end square
    //and drawing the stroke
    context.beginPath();
    context.moveTo(link.source.x, link.source.y);
    context.lineTo(targetX, targetY);
    context.lineWidth = arrowWidth;
    context.stroke();

    context.globalAlpha = 1;
    context.strokeStyle = 'black';
    //starting a new path from the head of the arrow to one of the sides of
    //the point
    context.beginPath();
    context.moveTo(targetX, targetY);
    context.lineTo(
        targetX - headlen * Math.cos(angle - Math.PI / 7),
        targetY - headlen * Math.sin(angle - Math.PI / 7)
    );

    //path from the side point of the arrow, to the other side point
    context.lineTo(
        targetX - headlen * Math.cos(angle + Math.PI / 7),
        targetY - headlen * Math.sin(angle + Math.PI / 7)
    );

    //path from the side point back to the tip of the arrow, and then
    //again to the opposite side point
    context.lineTo(targetX, targetY);
    context.lineTo(
        targetX - headlen * Math.cos(angle - Math.PI / 7),
        targetY - headlen * Math.sin(angle - Math.PI / 7)
    );

    //draws the paths created above
    context.stroke();
    context.restore();
}

export function drawLabel(
    context,
    node,
    selectedNode,
    node_size,
    labelColor = 'black',
    outlineColor = 'orange'
) {
    if (node.id === selectedNode?.id) {
        context.font = '14px bold-serif';
        context.fillStyle = labelColor; // Set text color
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(node.id, node.x - node_size, node.y - node_size * 2);
        context.strokeStyle = d3.color(outlineColor);
        context.stroke();
        context.restore();
    }
}
