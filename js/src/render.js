import { createCanvas } from "@napi-rs/canvas";
import { readFile, writeFile } from "node:fs/promises";
import { parseArgs } from "node:util";
import * as d3 from "d3";

function render(graph, drawing) {
  const width = 2000;
  const height = 2000;
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");

  ctx.beginPath();
  ctx.rect(0, 0, width, height);
  ctx.fillStyle = "#fff";
  ctx.fill();

  const left = Math.min(
    ...graph.nodes.map((node) => drawing[node.id][0] - node.shape.width / 2),
  );
  const right = Math.max(
    ...graph.nodes.map((node) => drawing[node.id][0] + node.shape.width / 2),
  );
  const top = Math.max(
    ...graph.nodes.map((node) => drawing[node.id][1] + node.shape.height / 2),
  );
  const bottom = Math.min(
    ...graph.nodes.map((node) => drawing[node.id][1] - node.shape.height / 2),
  );
  const contentWidth = right - left;
  const contentHeight = top - bottom;
  ctx.translate(
    -left - contentWidth / 2 + width / 2,
    -bottom - contentHeight / 2 + height / 2,
  );

  const nodeColor = d3.scaleOrdinal(d3.schemeCategory10);
  const groups = {};
  for (const node of graph.nodes) {
    if ("group" in node) {
      nodeColor(node.group);
      if (!(node.group in groups)) {
        groups[node.group] = { id: node.group, nodes: [] };
      }
      groups[node.group].nodes.push(node.id);
    }
  }

  for (const group of Object.values(groups)) {
    let left = Infinity;
    let right = -Infinity;
    let bottom = Infinity;
    let top = -Infinity;
    for (const u of group.nodes) {
      const [x, y] = drawing[u];
      const { width: w, height: h } = graph.nodes[u].shape;
      left = Math.min(left, x - w / 2);
      right = Math.max(right, x + w / 2);
      bottom = Math.min(bottom, y - h / 2);
      top = Math.max(top, y + h / 2);
    }
    ctx.beginPath();
    ctx.rect(left, bottom, right - left, top - bottom);
    const c = d3.color(nodeColor(group.id));
    c.opacity = 0.2;
    ctx.fillStyle = c.toString();
    ctx.fill();
  }

  for (const link of graph.links) {
    const [x1, y1] = drawing[link.source];
    const [x2, y2] = drawing[link.target];
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = "#888";
    ctx.stroke();
  }

  for (const node of graph.nodes) {
    const [x, y] = drawing[node.id];
    const { width: w, height: h } = node.shape;
    ctx.beginPath();
    ctx.rect(x - w / 2, y - h / 2, w, h);
    ctx.strokeStyle = "#000";
    ctx.stroke();
    if ("group" in node) {
      ctx.fillStyle = nodeColor(node.group);
    } else {
      ctx.fillStyle = "#fff";
    }
    ctx.fill();
  }

  for (const node of graph.nodes) {
    const [x, y] = drawing[node.id];
    ctx.fillStyle = "#000";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(node.id, x, y);
  }
  return canvas.encode("png");
}

(async () => {
  const { values } = parseArgs({
    options: {
      graphFile: {
        type: "string",
      },
      drawingFile: {
        type: "string",
      },
      output: {
        type: "string",
      },
    },
  });
  const graph = JSON.parse(await readFile(values.graphFile));
  for (const node of graph.nodes) {
    if (!node.shape) {
      node.shape = {
        width: 30,
        height: 30,
      };
    }
  }
  const drawing = JSON.parse(await readFile(values.drawingFile));
  const pngData = await render(graph, drawing);
  writeFile(values.output, pngData);
})();
