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
  var pageBounds = { x: 100, y: 50, width: 700, height: 400 },
    page = svg.append("rect").attr("id", "page").attr(pageBounds),
    nodeRadius = 10,
    realGraphNodes = graph.nodes.slice(0);
  let fixedNode = { fixed: true, fixedWeight: 100 },
    topLeft = { ...fixedNode, x: pageBounds.x, y: pageBounds.y },
    tlIndex = graph.nodes.push(topLeft) - 1,
    bottomRight = {
      ...fixedNode,
      x: pageBounds.x + pageBounds.width,
      y: pageBounds.y + pageBounds.height,
    },
    brIndex = graph.nodes.push(bottomRight) - 1,
    constraints = [];
  for (var i = 0; i < realGraphNodes.length; i++) {
    constraints.push({
      axis: "x",
      type: "separation",
      left: tlIndex,
      right: i,
      gap: nodeRadius,
    });
    constraints.push({
      axis: "y",
      type: "separation",
      left: tlIndex,
      right: i,
      gap: nodeRadius,
    });
    constraints.push({
      axis: "x",
      type: "separation",
      left: i,
      right: brIndex,
      gap: nodeRadius,
    });
    constraints.push({
      axis: "y",
      type: "separation",
      left: i,
      right: brIndex,
      gap: nodeRadius,
    });
  }
  if (graph) {
    d3cola
      .nodes(graph?.nodes)
      .links(graph?.links)
      .constraints(graph?.constraints)
      .defaultNodeSize(1)
      // .flowLayout("y", 30)
      // .size([width, height])
      // .symmetricDiffLinkLengths(20)
      // .avoidOverlaps(true)
      .start(10, 10, 10, 0, false, false);
    // d3cola.start(10, 15, 20, 15, false, true);
  }

  const xmn = d3.min(graph?.nodes.map((node) => node?.x ?? 0) ?? []);
  const ymn = d3.min(graph?.nodes.map((node) => node?.y ?? 0) ?? []);

  // const xScale = d3
  //   .scaleLinear()
  //   .domain(
  //     d3.extent(!graph ? [0, width] : graph.nodes.map((node) => node.x - xmn))
  //   )
  //   .range([0, width])
  //   .nice();

  // const yScale = d3
  //   .scaleLinear()
  //   .domain(d3.extent(!graph ? [0, height] : graph.nodes.map(({ y }) => y)))
  //   .range([0, height])
  //   .nice();
  const xScale = (x) => x - xmn + 50;
  const yScale = (y) => y - ymn + 50;

  const nodes = graph?.nodes.map((node) => ({
    ...node,
    width: 100,
    height: 25,
  }));
  const links = graph?.links;

  return (
    <>
      <select onChange={handleSelectChange} defaultValue={"no_cycle_tree"}>
        <option value="no_cycle_tree">no_cycle_tree</option>
        <option value="node_n=100_0 copy">100 0</option>
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
          <g opacity={0.5}>
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
          <g>
            {nodes.map((node) => (
              <circle
                key={node.name}
                cx={xScale(node.x)}
                cy={yScale(node.y)}
                r="5"
                fill="blue"
                // opacity={0.5}
                stroke="black"
                // width={100}
                // height={25}
              >
                <title>{node.id}</title>
              </circle>
            ))}
          </g>
        </svg>
      )}
    </>
  );
}

export default App;
