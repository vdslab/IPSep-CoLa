import { readFile, writeFile } from "node:fs/promises";
import * as cola from "webcola";
import * as d3 from "d3";
import { parseArgs } from "node:util";

function layout(graph, options) {
  const overlapRemvoal = options?.overlapRemvoal || false;
  const clusters = options?.clusters || null;
  const d3cola = cola
    .d3adaptor(d3)
    .nodes(graph.nodes)
    .links(graph.links)
    .constraints(graph.graph.constraints)
    .linkDistance(100);

  if (clusters) {
    d3cola.groups(clusters);
  }

  if (overlapRemvoal) {
    for (const node of graph.nodes) {
      node.width = node.shape.width + 5;
      node.height = node.shape.height + 5;
    }
    d3cola.avoidOverlaps(true);
  }

  d3cola.start(10, 10, 10, 0, false, false);

  const drawing = {};
  for (const node of graph.nodes) {
    drawing[node.id] = [node.x, node.y];
  }
  return drawing;
}

(async () => {
  const { values } = parseArgs({
    options: {
      graphFile: {
        type: "string",
      },
      output: {
        type: "string",
      },
      overlapRemoval: {
        type: "boolean",
      },
      clusterOverlapRemoval: {
        type: "boolean",
      },
    },
  });
  const graph = JSON.parse(await readFile(values.graphFile));
  for (const link of graph.links) {
    link.source = +link.source;
    link.target = +link.target;
  }
  let clusters;
  if (values.clusterOverlapRemoval) {
    clusters = {};
    graph.nodes.forEach((node, i) => {
      if (!(node.group in clusters)) {
        clusters[node.group] = {
          id: node.group,
          leaves: [],
        };
      }
      clusters[node.group].leaves.push(i);
    });
    clusters = Object.values(clusters);
    for (
      let i = graph.nodes.length;
      i < graph.nodes.length + clusters.length * 2;
      ++i
    ) {
      graph.graph.distance.push([]);
    }
  }
  const drawing = layout(graph, {
    overlapRemvoal: values.overlapRemoval,
    clusters,
  });
  writeFile(values.output, JSON.stringify(drawing));
})();
