import { readFile, writeFile } from "node:fs/promises";
import * as cola from "webcola";
import * as d3 from "d3";
import { parseArgs } from "node:util";

function layout(graph, options) {
  const overlapRemvoal = options?.overlapRemvoal || false;
  const d3cola = cola
    .d3adaptor(d3)
    .nodes(graph.nodes)
    .links(graph.links)
    .constraints(graph.graph.constraints)
    .distanceMatrix(graph.graph.distance);

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
    },
  });
  const graph = JSON.parse(await readFile(values.graphFile));
  const drawing = layout(graph, {
    overlapRemvoal: true,
  });
  writeFile(values.output, JSON.stringify(drawing));
})();
