export class Link {
    constructor(source, target) {
        this.source = source;
        this.target = target;
    }

    setSource(newSource) {
        this.source = newSource;
    }

    setTarget(newTarget) {
        this.target = newTarget;
    }
}

export class Node {
    constructor(x, y, id) {
        this.x = x;
        this.y = y;
        this.id = id;
    }
}
