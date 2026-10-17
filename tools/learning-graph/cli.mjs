import {readFile} from 'node:fs/promises';
import {buildGraph, pathway, searchTopics} from './graph.mjs';

const [topicsFile, dependenciesFile, action = 'summary', ...args] = process.argv.slice(2);
if (!topicsFile || !dependenciesFile || !['summary', 'search', 'path'].includes(action)) {
  console.error('Usage: node tools/learning-graph/cli.mjs topics.json dependencies.json [summary|search <phrase>|path <topicId> [--hard-only]]');
  process.exitCode = 2;
} else {
  try {
    const [topics, edges] = await Promise.all([topicsFile, dependenciesFile].map(async path => JSON.parse(await readFile(path, 'utf8'))));
    const graph = buildGraph(topics, edges);
    const output = action === 'summary'
      ? {topicCount: graph.byId.size, dependencyCount: graph.edgeCount, acyclic: true}
      : action === 'search' ? searchTopics(graph, args.join(' '))
      : pathway(graph, args[0], {includeSoft: !args.includes('--hard-only')});
    console.log(JSON.stringify(output, null, 2));
  } catch (e) { console.error(`Learning graph validation failed: ${e.message}`); process.exitCode = 1; }
}
