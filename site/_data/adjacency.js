module.exports = function(data) {
  const edges = data.graph?.edges; // graph must now exist
  if(!edges) return {};

  const adj = {};
  edges.forEach(e => {
    if(!adj[e.source]) adj[e.source] = [];
    adj[e.source].push(e);
  });

  return adj;
};
