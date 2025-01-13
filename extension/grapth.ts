import {ascending, create, hierarchy, linkHorizontal, tree as treeD3} from "d3"

const data = {
    name: "Eve",
    children: [
      {name: "Cain"},
      {name: "Seth", children: [{name: "Enos"}, {name: "Noam"}]},
      {name: "Abel"},
      {name: "Awan", children: [{name: "Enoch"}]},
      {name: "Azura"}
    ]
};

const width = 928;

// Compute the tree height; this approach will allow the height of the
// SVG to scale according to the breadth (width) of the tree layout.
const root = hierarchy(data);
const dx = 10;
const dy = width / (root.height + 1);

// Create a tree layout.
const tree = treeD3<any>().nodeSize([dx, dy]);

// Sort the tree and apply the layout.
root.sort((a, b) => ascending(a.data.name, b.data.name));
tree(root);

// Compute the extent of the tree. Note that x and y are swapped here
// because in the tree layout, x is the breadth, but when displayed, the
// tree extends right rather than down.
let x0 = Infinity;
let x1 = -x0;
root.each(d => {
if (!d.x) return;
if (d.x > x1) x1 = d.x;
if (d.x < x0) x0 = d.x;
});

// Compute the adjusted height of the tree.
const height = x1 - x0 + dx * 2;

const svg = create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-dy / 3, x0 - dx, width, height])
    .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

const link = svg.append("g")
    .attr("fill", "none")
    .attr("stroke", "#555")
    .attr("stroke-opacity", 0.4)
    .attr("stroke-width", 1.5)
.selectAll()
    .data(root.links())
    .join("path")
    .attr("d", linkHorizontal()
        .x(d => d.y)
        .y(d => d.x));

const node = svg.append("g")
    .attr("stroke-linejoin", "round")
    .attr("stroke-width", 3)
.selectAll()
.data(root.descendants())
.join("g")
    .attr("transform", d => `translate(${d.y},${d.x})`);

node.append("circle")
    .attr("fill", d => d.children ? "#555" : "#999")
    .attr("r", 2.5);

node.append("text")
    .attr("dy", "0.31em")
    .attr("x", d => d.children ? -6 : 6)
    .attr("text-anchor", d => d.children ? "end" : "start")
    .text(d => d.data.name)
    .attr("stroke", "white")
    .attr("paint-order", "stroke");
  
svg.node();