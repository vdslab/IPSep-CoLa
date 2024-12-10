import * as cola from "webcola";
import * as d3 from "d3";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { loadJSON } from "../cola/loadJson.js";
import path from "path";

const graphDir = path.join("src", "data", "random_tree");
const dirs = [];
for (let node_n = 100; node_n <= 2000; node_n += 100) {
  dirs.push({
    path: path.join(graphDir, node_n.toString()),
    basename: node_n.toString(),
  });
}

for (const { path: dirPath, basename } of dirs) {
  const files = Array(20)
    .fill(0)
    .map((_, i) => `node_n=${basename}_${i}.json`);
  const graphs = files.map((file) => {
    const graphJson = loadJSON(file, dirPath);
    // const align_const = graphJson.graph.alignment;
    // graphJson.graph.constraints = align_const;
    //   graphJson.graph.constraints.concat(align_const);
    const graph = graphJson.graph;
    const length = graphJson.length;
    const dist = graphJson.dist.map((row) => row.map((v) => v * length));

    return {
      graph,
      name: file.split(".")[0],
      dist,
      length,
      basename,
    };
  });

  const saveDir = path.join("result", basename);
  if (!existsSync(saveDir)) {
    mkdirSync(saveDir);
  }
  graphs.forEach(({ graph, name, dist, length }, i) => {
    console.log(name);
    const d3cola = cola.d3adaptor(d3);
    d3cola
      .nodes(graph?.nodes)
      .links(graph?.links)
      .constraints(graph?.constraints)
      // .defaultNodeSize(1)
      // .constraints([])
      .distanceMatrix(dist)
      .start(10, 10, 10, 0, false, false);

    const nodes = graph.nodes.map(
      ({ x, y, index /*, variable: { weight, index }*/ }) => ({
        x,
        y,
        // weight,
        index,
      })
    );
    nodes.sort((a, b) => a.index - b.index);

    const graphPosData = { nodes, distanceMatrix: dist, length };

    writeFileSync(
      path.join(saveDir, `${i}.json`),
      JSON.stringify(graphPosData),
      (err) => {
        console.log(err);
      }
    );
  });
  console.log("cola end");
}
