const adjacency = require("./adjacency.js");
const graph = {
  nodes: [
    {id: "ROS", label: "Molecule"},
    {id: "DNA_damage", label: "Process"},
    {id: "Cancer", label: "Disease"}
  ],
  edges: [
    {source: "ROS", target: "DNA_damage", type: "CAUSES"},
    {source: "DNA_damage", target: "Cancer", type: "CONTRIBUTES_TO"}
  ]
};

const adj = adjacency({graph});
console.log(adj);
