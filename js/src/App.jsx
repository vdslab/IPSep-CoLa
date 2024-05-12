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
  const width = 960;
  const height = 600;
  if (graph) {
    d3cola
      .nodes(graph?.nodes)
      .links(graph?.links)
      .constraints(graph?.constraints)
      .size([width, height])
      .start(10, 15, 20);
  }

  const nodes = graph?.nodes;
  const links = graph?.links;

  return (
    <>
      <select onChange={handleSelectChange} defaultValue={"no_cycle_tree"}>
        <option value="no_cycle_tree">tree</option>
        <option value="w">w</option>
      </select>
      {graph && (
        <svg width="960" height="600">
          <g>
            {nodes.map((node) => (
              <circle
                key={node.name}
                cx={node.x}
                cy={node.y}
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
                x1={link.source.x}
                y1={link.source.y}
                x2={link.target.x}
                y2={link.target.y}
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
