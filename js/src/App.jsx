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
      .constraints(graph?.constraints)
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
        <option value="no_cycle_tree">tree</option>
        <option value="w">w</option>
        <option value="gnp_random_10">gnp_random_10</option>
        <option value="gnp_random_50">gnp_random_50</option>
        <option value="gnp_random_100">gnp_random_100</option>
        <option value="gnp_random_150">gnp_random_150</option>
        <option value="gnp_random_200">gnp_random_200</option>
        <option value="gnp_random_all_constraints_10">
          gnp_random_all_constraints_10
        </option>
        <option value="gnp_random_all_constraints_50">
          gnp_random_all_constraints_50
        </option>
        <option value="gnp_random_all_constraints_100">
          gnp_random_all_constraints_100
        </option>
        <option value="gnp_random_all_constraints_150">
          gnp_random_all_constraints_150
        </option>
        <option value="gnp_random_all_constraints_200">
          gnp_random_all_constraints_200
        </option>
        <option value="gnp_random_all_constraints_250">
          gnp_random_all_constraints_250
        </option>
        <option value="gnp_random_all_constraints_300">
          gnp_random_all_constraints_300
        </option>
        <option value="gnp_random_all_constraints_350">
          gnp_random_all_constraints_350
        </option>
        <option value="gnp_random_all_constraints_400">
          gnp_random_all_constraints_400
        </option>
        <option value="gnp_random_all_constraints_450">
          gnp_random_all_constraints_450
        </option>
        <option value="gnp_random_all_constraints_500">
          gnp_random_all_constraints_500
        </option>
        <option value="random_tree_10">random_tree_10</option>
        <option value="random_tree_50">random_tree_50</option>
        <option value="random_tree_100">random_tree_100</option>
        <option value="random_tree_150">random_tree_150</option>
        <option value="random_tree_200">random_tree_200</option>
        <option value="random_tree_250">random_tree_250</option>
        <option value="random_tree_300">random_tree_300</option>
        <option value="random_tree_350">random_tree_350</option>
        <option value="random_tree_400">random_tree_400</option>
        <option value="random_tree_450">random_tree_450</option>
        <option value="random_tree_500">random_tree_500</option>
      </select>
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
