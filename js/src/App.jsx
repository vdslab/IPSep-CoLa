import * as cola from "webcola";
import * as d3 from "d3";
import graph from "../../src/data/no_cycle_tree.json";

function App() {
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
