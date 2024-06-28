import * as cola from "webcola";
import * as d3 from "d3";
import { writeFileSync } from "fs";
import { pythonDataDir, loadJSON } from "../cola/loadJson.js";
import path from "path";

const jsonDir = path.join(pythonDataDir, "json");
const graphDir = path.join(jsonDir, "download");
const distDir = path.join(jsonDir, "dist");

const files = ["no_cycle_tree.json"];

const graphs = files.map((file) => {
  const graph = loadJSON(file, graphDir);
  const dist = loadJSON(file, distDir);
  return { graph, name: file.split(".")[0], dist };
});

const d3cola = cola.d3adaptor(d3);
graphs.forEach(({ graph, name, dist }) => {
  for (let i = 0; i < 1; i++) {
    d3cola
      .nodes(graph?.nodes)
      .links(graph?.links)
      .constraints(graph?.constraints)
      .distanceMatrix(dist)
      .start(10, 15, 20, 15, false, true);

    const nodes = graph.nodes.map(({ x, y, variable: { weight, index } }) => ({
      x,
      y,
      weight,
      index,
    }));
    nodes.sort((a, b) => a.index - b.index);

    const graphPosData = { nodes, distanceMatrix: dist };

    if (i === 0) {
      // const n0 = graph.nodes[0];
      // const e0 = graph.links[0];
      // console.log(e0)
      // console.log(n0.variable);
      console.log("have matrix", !!d3cola.distanceMatrix());
    }

    writeFileSync(
      `src/data/cola/${name}_${i}.json`,
      JSON.stringify(graphPosData),
      (err) => {
        console.log(err);
      }
    );
  }
});
