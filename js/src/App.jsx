import * as cola from "webcola";
import * as d3 from "d3";
import { useEffect, useState } from "react";

function App() {
  const [graph, setGraph] = useState();

  useEffect(() => {
    fetch("/no_cycle_tree.json", {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => setGraph(data));
  }, []);

  const handleSelectChange = (e) => {
    const filePath = `/${e.target.value}.json`;
    fetch(filePath, {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => setGraph(data));
  };

  const d3cola = cola.d3adaptor(d3);
  const width = 1000;
  const height = 1000;
  if (graph) {
    d3cola
      .nodes(graph?.nodes)
      .links(graph?.links)
      // .constraints(graph?.constraints)
      .flowLayout("y", 30)
      .size([width, height])
      .symmetricDiffLinkLengths(20)
      .start(10, 15, 20, 15, false, true);
  }

  const xScale = d3
    .scaleLinear()
    .domain(d3.extent(!graph ? [0, width] : graph.nodes.map((node) => node.x)))
    .range([0, width])
    .nice();

  const yScale = d3
    .scaleLinear()
    .domain(d3.extent(!graph ? [0, height] : graph.nodes.map(({ y }) => y)))
    .range([0, height])
    .nice();

  const nodes = graph?.nodes;
  const links = graph?.links;

  return (
    <>
      <select onChange={handleSelectChange} defaultValue={"no_cycle_tree"}>
        <option value="3elt">3elt</option>
        <option value="1138_bus">1138_bus</option>
        <option value="dwt_1005">dwt_1005</option>
        <option value="dwt_2680">dwt_2680</option>
        <option value="poli">poli</option>
        <option value="USpowerGrid">USpowerGrid</option>
        <option value="qh882">qh882</option>
      </select>
      <button
        onClick={() => {
          const pos = graph.nodes.map(({ x, y, index, name }) => ({
            x,
            y,
            index,
            name,
          }));

          const blob = new Blob([JSON.stringify(pos)], {
            type: "application/json",
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "position.json";
          a.click();
        }}
      >
        download position
      </button>
      {graph && (
        <svg width={width} height={height}>
          <g>
            {nodes.map((node) => (
              <circle
                key={node.name}
                cx={xScale(node.x)}
                cy={yScale(node.y)}
                r="5"
                fill="blue"
                stroke="black"
              />
            ))}
          </g>
          <g>
            {links.map((link) => (
              <line
                key={link.source.index + "-" + link.target.index}
                x1={xScale(link.source.x)}
                y1={yScale(link.source.y)}
                x2={xScale(link.target.x)}
                y2={yScale(link.target.y)}
                stroke="black"
              />
            ))}
          </g>
        </svg>
      )}
    </>
  );
}

export default App;
