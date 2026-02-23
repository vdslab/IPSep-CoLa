#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib_fontja
import networkx as nx


def compute_union_bounds(pos_list, pad_ratio=0.03):
    xmin, xmax = float("inf"), -float("inf")
    ymin, ymax = float("inf"), -float("inf")
    for pos in pos_list:
        for _, (x, y) in pos.items():
            xmin = min(xmin, x)
            xmax = max(xmax, x)
            ymin = min(ymin, y)
            ymax = max(ymax, y)
    xr = (xmax - xmin) if xmax > xmin else 1.0
    yr = (ymax - ymin) if ymax > ymin else 1.0
    padx = xr * pad_ratio
    pady = yr * pad_ratio
    return (xmin - padx, xmax + padx), (ymin - pady, ymax + pady)


def choose_figsize_from_bounds(xlim, ylim, height_in=10.0, min_w=8.0, max_w=20.0):
    # データの縦横比に合わせてキャンバス比率を決める（無駄な余白を減らす）
    xr = max(1e-9, xlim[1] - xlim[0])
    yr = max(1e-9, ylim[1] - ylim[0])
    width = height_in * (xr / yr)
    width = max(min_w, min(max_w, width))
    return (width, height_in)


def plot_graph_fixed(
    G: nx.Graph,
    pos: dict,
    out_path: Path,
    xlim,
    ylim,
    show_violation=False,
    show_size=False,
    node_size=30,
    labeled=False,
    figsize=(6, 5),
    dpi=300,
):
    matplotlib_fontja.japanize()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # エッジの主張を弱める設定
    edge_color = ["gray"] * len(G.edges)
    edge_width = [1.5] * len(G.edges)
    edge_alpha = 1

    if show_violation:
        constraints = G.graph.get("constraints", [])
        y_violations = {
            tuple(sorted([str(c["right"]), str(c["left"])])): (
                max(0, c["gap"] - (pos[str(c["right"])][1] - pos[str(c["left"])][1]))
                > 1e-1
            )
            for c in constraints
            if c.get("axis", "") == "y"
        }
        edge_color = [
            "red" if y_violations.get(tuple(sorted(e)), False) else "gray"
            for e in G.edges
        ]
        edge_width = [
            2 if y_violations.get(tuple(sorted(e)), False) else 1.5 for e in G.edges
        ]
        edge_alpha = 0.8

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # 少しだけ余白を追加
    pd = 0.01
    fig.subplots_adjust(left=pd, right=1 - pd, bottom=pd, top=1 - pd)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    # エッジとノードを別々に描画（エッジだけ透明度を下げる）
    nx.draw_networkx_edges(
        G,
        pos=pos,
        edge_color=edge_color,
        width=edge_width,
        alpha=edge_alpha,
        ax=ax,
    )

    nx.draw_networkx_nodes(
        G,
        pos=pos,
        node_shape="s",
        node_size=node_size,
        alpha=0.8,
        ax=ax,
    )

    if labeled:
        nx.draw_networkx_labels(G, pos=pos, ax=ax)

    # 既存の見た目に合わせる（元コードと同じ）
    ax.invert_yaxis()

    # 描画範囲に枠線を追加（点線）
    rect_x = [xlim[0], xlim[1], xlim[1], xlim[0], xlim[0]]
    rect_y = [ylim[0], ylim[0], ylim[1], ylim[1], ylim[0]]
    ax.plot(rect_x, rect_y, "k--", linewidth=2, zorder=1000)

    # 領域のサイズを表示
    if show_size:
        x_length = xlim[1] - xlim[0]
        y_length = ylim[1] - ylim[0]
        text_str = f"横: {x_length:.2f}\n縦: {y_length:.2f}"
        ax.text(
            0.02,
            0.98,
            text_str,
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            fontsize=24,
            zorder=1001,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, pad_inches=0)  # bbox_inches は使わない
    plt.close(fig)


def load_pos(path: Path) -> dict:
    pos = json.load(open(path, "r"))
    # pos のキーが数字だったり混ざってても plot.py 互換のため str に寄せる
    return {str(k): v for k, v in pos.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph_file", required=True)
    ap.add_argument(
        "--drawing_file", required=True, nargs="*", help="この手法のpos(json)"
    )
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--output_suffix", required=True, nargs="*")
    ap.add_argument("--node_size", type=int, default=30)
    ap.add_argument("--labeled", action="store_true")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--pad_ratio", type=float, default=0.03)
    ap.add_argument("--height_in", type=float, default=10.0)
    args = ap.parse_args()

    # グラフ読み込み（既存関数）

    pos_list = [load_pos(Path(p)) for p in args.drawing_file]

    xlim, ylim = compute_union_bounds(pos_list, pad_ratio=args.pad_ratio)
    figsize = choose_figsize_from_bounds(xlim, ylim, height_in=args.height_in)

    graph = nx.node_link_graph(json.load(open(args.graph_file)), edges="links")
    for drawing_file, output_suffix in zip(args.drawing_file, args.output_suffix):
        pos_main = load_pos(Path(drawing_file))

        def plot(show_violation, show_size):
            suffix = ""
            if show_violation:
                suffix += "show_violation"
            if not show_violation and show_size:
                suffix += "show_size"
            elif show_size:
                suffix += "size"
            plot_graph_fixed(
                G=graph,
                pos=pos_main,
                out_path=Path(args.output_dir)
                / f"{Path(args.graph_file).stem}_{output_suffix}_{suffix}.pdf",
                xlim=xlim,
                ylim=ylim,
                show_violation=show_violation,
                show_size=show_size,
                node_size=args.node_size,
                labeled=args.labeled,
                figsize=figsize,
                dpi=args.dpi,
            )

        plot(False, False)
        plot(False, True)
        plot(True, False)
        plot(True, True)


if __name__ == "__main__":
    main()
