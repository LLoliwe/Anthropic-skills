/** Original Pryntor graph utilities. No Marble data is bundled with this code. */
export function buildGraph(topicsInput, dependenciesInput) {
  const topics = topicsInput?.topics;
  const edges = dependenciesInput?.dependencies;
  if (!Array.isArray(topics) || !Array.isArray(edges)) throw new Error('Expected {topics:[]} and {dependencies:[]} JSON');
  const byId = new Map();
  for (const t of topics) {
    if (!t || typeof t.id !== 'string' || !t.id || byId.has(t.id)) throw new Error(`Invalid/duplicate topic id: ${t?.id}`);
    if (typeof t.name !== 'string' || !t.name.trim()) throw new Error(`Missing topic name: ${t.id}`);
    byId.set(t.id, t);
  }
  const prereqs = new Map([...byId.keys()].map(id => [id, []]));
  const seenEdges = new Set();
  for (const edge of edges) {
    if (!edge || !byId.has(edge.topicId) || !byId.has(edge.prerequisiteId)) throw new Error('Dangling dependency');
    if (edge.topicId === edge.prerequisiteId) throw new Error(`Self-dependency: ${edge.topicId}`);
    if (!['hard', 'soft'].includes(edge.strength)) throw new Error(`Invalid strength: ${edge.strength}`);
    const key = `${edge.topicId}\0${edge.prerequisiteId}`;
    if (seenEdges.has(key)) throw new Error(`Duplicate dependency: ${edge.topicId}`);
    seenEdges.add(key);
    prereqs.get(edge.topicId).push({id: edge.prerequisiteId, strength: edge.strength, reason: edge.reason ?? ''});
  }
  // Prove acyclicity for ALL nodes, not just the currently viewed pathway.
  const state = new Map();
  function visit(id) {
    if (state.get(id) === 1) throw new Error(`Dependency cycle at ${id}`);
    if (state.get(id) === 2) return;
    state.set(id, 1);
    for (const p of prereqs.get(id)) visit(p.id);
    state.set(id, 2);
  }
  for (const id of byId.keys()) visit(id);
  return {byId, prereqs, edgeCount: edges.length};
}

/** Returns a teaching SEQUENCE, not evidence of mastery or permission to advance. */
export function pathway(graph, targetId, {includeSoft = true} = {}) {
  if (!graph.byId.has(targetId)) throw new Error(`Unknown topic: ${targetId}`);
  const seen = new Set(), order = [];
  function visit(id) {
    if (seen.has(id)) return;
    seen.add(id);
    const links = graph.prereqs.get(id).filter(p => includeSoft || p.strength === 'hard');
    for (const link of links) visit(link.id);
    order.push({id, name: graph.byId.get(id).name, subject: graph.byId.get(id).subject ?? '', prerequisiteCount: links.length});
  }
  visit(targetId);
  return order;
}

export function searchTopics(graph, phrase, limit = 15) {
  if (typeof phrase !== 'string' || !phrase.trim()) return [];
  const q = phrase.trim().toLocaleLowerCase();
  return [...graph.byId.values()].filter(t => t.name.toLocaleLowerCase().includes(q)).slice(0, Math.max(0, Math.min(50, limit))).map(t => ({id: t.id, name: t.name, subject: t.subject}));
}
