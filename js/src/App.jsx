import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import * as cola from "webcola";
import * as d3 from "d3";
import graph from "../../src/data/no_cycle_tree.json";

function App() {
  const [count, setCount] = useState(0);

  const d3cola = cola.d3adaptor(d3);
  const width = 960;
  const height = 600;
  d3cola
    .nodes(graph.nodes)
    .links(graph.links)
    .constraints(graph.constraints)
    .size([width, height])
    .start(10, 15, 20);

  const nodes = graph.nodes;
  const links = graph.links;

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <svg width="960" height="600">
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
      </svg>
    </>
  );
}

export default App;
