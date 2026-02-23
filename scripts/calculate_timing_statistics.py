#!/usr/bin/env python3
"""
タイミング統計計算スクリプト

各メソッド（FullSGD, Inline Projection, etc.）と制約タイプ（gap, layered）について、
run_*.jsonファイルからSGD_step、X_projection、Y_projection、Iterationの統計を計算し、
中央値を求めてCSV形式で出力します。
"""

import csv
import json
import statistics
from pathlib import Path
from typing import Dict


def extract_stats_from_unicon(json_path: Path) -> Dict[str, float]:
    """
    標準的なJSONファイルから統計情報を抽出（FullSGD, Inline, UNICON用）

    Returns:
        dict: {
            'sgd_total': float,
            'sgd_mean': float,
            'x_total': float,
            'x_mean': float,
            'y_total': float,
            'y_mean': float,
            'iter_total': float,
            'iter_mean': float
        }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    stats = data.get("statistics", {})

    # SGD_step統計
    sgd_stats = stats.get("SGD_step", {})
    sgd_total = sgd_stats.get("total", 0.0)
    sgd_mean = sgd_stats.get("mean", 0.0)

    # X_projection統計
    x_stats = stats.get("X_constraints", {})
    x_total = x_stats.get("total", 0.0)
    x_mean = x_stats.get("mean", 0.0)

    # Y_projection統計
    y_stats = stats.get("Y_constraints", {})
    y_total = y_stats.get("total", 0.0)
    y_mean = y_stats.get("mean", 0.0)

    iter_total = sgd_total + x_total + y_total

    return {
        "sgd_total": sgd_total,
        # "sgd_mean": sgd_mean,
        "x_total": x_total,
        # "x_mean": x_mean,
        "y_total": y_total,
        # "y_mean": y_mean,
        "iter_total": iter_total,
        # "iter_mean": iter_mean,
    }


def extract_stats_from_json(json_path: Path) -> Dict[str, float]:
    """
    標準的なJSONファイルから統計情報を抽出（FullSGD, Inline, UNICON用）

    Returns:
        dict: {
            'sgd_total': float,
            'sgd_mean': float,
            'x_total': float,
            'x_mean': float,
            'y_total': float,
            'y_mean': float,
            'iter_total': float,
            'iter_mean': float
        }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    stats = data.get("statistics", {})

    # SGD_step統計
    sgd_stats = stats.get("SGD_step", {})
    sgd_total = sgd_stats.get("total", 0.0)
    sgd_mean = sgd_stats.get("mean", 0.0)

    # X_projection統計
    x_stats = stats.get("X_projection", {})
    x_total = x_stats.get("total", 0.0)
    x_mean = x_stats.get("mean", 0.0)

    # Y_projection統計
    y_stats = stats.get("Y_projection", {})
    y_total = y_stats.get("total", 0.0)
    y_mean = y_stats.get("mean", 0.0)

    # Iteration全体の統計を計算
    iter_total = sgd_total + x_total + y_total

    return {
        "sgd_total": sgd_total,
        # "sgd_mean": sgd_mean,
        "x_total": x_total,
        # "x_mean": x_mean,
        "y_total": y_total,
        # "y_mean": y_mean,
        "iter_total": iter_total,
        # "iter_mean": iter_mean,
    }


def extract_webcola_stats_from_json(json_path: Path) -> Dict[str, float]:
    """
    WebCoLa用JSONファイルから統計情報を抽出

    Returns:
        dict: {
            'initialLayout_total': float,
            'initialLayout_mean': float,
            'initialUserConstraint_total': float,
            'initialUserConstraint_mean': float,
            'initialAllConstraints_total': float,
            'initialAllConstraints_mean': float,
            'updateNodePositions_total': float,
            'updateNodePositions_mean': float,
            'all_metrics_total': float
        }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    stats = data.get("statistics", {})

    # initialLayout統計
    initial_layout = stats.get("initialLayout", {})
    initialLayout_total = initial_layout.get("total", 0.0)
    initialLayout_mean = initial_layout.get("mean", 0.0)

    # initialUserConstraintIterations統計
    initial_user = stats.get("initialUserConstraintIterations", {})
    initialUserConstraint_total = initial_user.get("total", 0.0)
    initialUserConstraint_mean = initial_user.get("mean", 0.0)

    # initialAllConstraintsIterations統計
    initial_all = stats.get("initialAllConstraintsIterations", {})
    initialAllConstraints_total = initial_all.get("total", 0.0)
    initialAllConstraints_mean = initial_all.get("mean", 0.0)

    # updateNodePositions統計
    update_node = stats.get("updateNodePositions", {})
    updateNodePositions_total = update_node.get("total", 0.0)
    updateNodePositions_mean = update_node.get("mean", 0.0)

    # 4つのメトリクスの合計
    iter_total = (
        initialLayout_total
        + initialUserConstraint_total
        + initialAllConstraints_total
        + updateNodePositions_total
    )

    return {
        "initialLayout_total": initialLayout_total,
        # "initialLayout_mean": initialLayout_mean,
        "initialUserConstraint_total": initialUserConstraint_total,
        # "initialUserConstraint_mean": initialUserConstraint_mean,
        "initialAllConstraints_total": initialAllConstraints_total,
        # "initialAllConstraints_mean": initialAllConstraints_mean,
        "updateNodePositions_total": updateNodePositions_total,
        # "updateNodePositions_mean": updateNodePositions_mean,
        "iter_total": iter_total,
    }


def extract_postprocessing_stats_from_json(json_path: Path) -> Dict[str, float]:
    """
    Post-processing Projection用JSONファイルから統計情報を抽出

    Returns:
        dict: {
            'sgd_total': float,
            'sgd_mean': float,
            'x_total': float,
            'x_mean': float,
            'y_total': float,
            'y_mean': float,
            'iter_total': float,
            'iter_mean': float
        }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    stats = data.get("statistics", {})

    # SGD_step統計
    sgd_stats = stats.get("SGD_step", {})
    sgd_total = sgd_stats.get("total", 0.0)
    sgd_mean = sgd_stats.get("mean", 0.0)

    # After_X_projection統計（値が1つだけなのでtotal=mean）
    x_stats = stats.get("After_X_projection", {})
    x_total = x_stats.get("total", 0.0)
    x_mean = x_stats.get("mean", 0.0)

    # After_Y_projection統計（値が1つだけなのでtotal=mean）
    y_stats = stats.get("After_Y_projection", {})
    y_total = y_stats.get("total", 0.0)
    y_mean = y_stats.get("mean", 0.0)

    # SGD_iterations統計（全体の反復時間）
    iter_stats = stats.get("SGD_iterations", {})
    iter_total = iter_stats.get("total", 0.0)
    iter_mean = iter_stats.get("mean", 0.0)

    return {
        "sgd_total": sgd_total,
        # "sgd_mean": sgd_mean,
        "x_total": x_total,
        # "x_mean": x_mean,
        "y_total": y_total,
        # "y_mean": y_mean,
        "iter_total": sgd_total + x_total + y_total,
        # "iter_mean": iter_mean,
    }


def calculate_medians_for_node_size(
    node_size_dir: Path, method_type: str = "default"
) -> Dict[str, float]:
    """
    指定されたノードサイズディレクトリ内のrun_*.jsonから中央値を計算

    Args:
        node_size_dir: ノードサイズディレクトリ（例: 0100/）
        method_type: メソッドタイプ ("default", "webcola", "postprocessing")

    Returns:
        dict: 各メトリクスの中央値
    """
    run_files = sorted(node_size_dir.glob("run_*.json"))
    if not run_files:
        return None

    # 各run_*.jsonから統計を抽出
    all_stats = []
    for run_file in run_files:
        try:
            if method_type == "webcola":
                stats = extract_webcola_stats_from_json(run_file)
            elif method_type == "postprocessing":
                stats = extract_postprocessing_stats_from_json(run_file)
            elif method_type == "unicon":
                stats = extract_stats_from_unicon(run_file)
            else:
                stats = extract_stats_from_json(run_file)
            all_stats.append(stats)
        except Exception as e:
            print(f"Warning: Failed to process {run_file}: {e}")
            continue

    if not all_stats:
        return None

    # 各メトリクスの中央値を計算
    medians = {}
    for key in all_stats[0].keys():
        values = [s[key] for s in all_stats]
        medians[key] = statistics.median(values)

    return medians


def process_constraint_type(
    base_dir: Path, method: str, constraint_type: str, output_path: Path
):
    """
    特定のメソッドと制約タイプについて統計を計算しCSV出力

    Args:
        base_dir: ベースディレクトリ
        method: メソッド名（例: "FullSGD(ours)"）
        constraint_type: 制約タイプ（"gap" or "layered"）
        output_path: 出力CSVパス
    """
    constraint_dir = (
        base_dir
        / method
        / "watts_strogatz"
        / "neighbor_2"
        / "rewire_030"
        / constraint_type
    )

    if not constraint_dir.exists():
        print(f"Skipping {method}/{constraint_type} - directory not found")
        return

    # ノードサイズディレクトリを探索（0100, 0200, ...）
    node_size_dirs = sorted(
        [d for d in constraint_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    )

    if not node_size_dirs:
        print(f"No node size directories found in {constraint_dir}")
        return

    # メソッドタイプを判定
    if method == "WebCoLa":
        method_type = "webcola"
    elif method == "Post-processing Projection":
        method_type = "postprocessing"
    elif method == "UNICON":
        method_type = "unicon"
    else:
        method_type = "default"

    results = []

    for node_dir in node_size_dirs:
        node_size = node_dir.name
        medians = calculate_medians_for_node_size(node_dir, method_type=method_type)

        if medians:
            if method_type == "webcola":
                row = {
                    "NodeSize": node_size,
                    "initialLayout_total_median": medians["initialLayout_total"],
                    # "initialLayout_mean_median": medians["initialLayout_mean"],
                    "initialUserConstraint_total_median": medians[
                        "initialUserConstraint_total"
                    ],
                    # "initialUserConstraint_mean_median": medians[
                    #     "initialUserConstraint_mean"
                    # ],
                    "initialAllConstraints_total_median": medians[
                        "initialAllConstraints_total"
                    ],
                    # "initialAllConstraints_mean_median": medians[
                    #     "initialAllConstraints_mean"
                    # ],
                    "updateNodePositions_total_median": medians[
                        "updateNodePositions_total"
                    ],
                    # "updateNodePositions_mean_median": medians[
                    #     "updateNodePositions_mean"
                    # ],
                    "Iter_total_median": medians["iter_total"],
                }
            else:
                row = {
                    "NodeSize": node_size,
                    "SGD_total_median": medians["sgd_total"],
                    # "SGD_mean_median": medians["sgd_mean"],
                    "X_total_median": medians["x_total"],
                    # "X_mean_median": medians["x_mean"],
                    "Y_total_median": medians["y_total"],
                    # "Y_mean_median": medians["y_mean"],
                    "Iter_total_median": medians["iter_total"],
                    # "Iter_mean_median": medians["iter_mean"],
                }
            results.append(row)
            print(f"  Processed {method}/{constraint_type}/{node_size}")

    # CSV出力
    if results:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="") as csvfile:
            if method_type == "webcola":
                fieldnames = [
                    "NodeSize",
                    "initialLayout_total_median",
                    # "initialLayout_mean_median",
                    "initialUserConstraint_total_median",
                    # "initialUserConstraint_mean_median",
                    "initialAllConstraints_total_median",
                    # "initialAllConstraints_mean_median",
                    "updateNodePositions_total_median",
                    # "updateNodePositions_mean_median",
                    "Iter_total_median",
                ]
            else:
                fieldnames = [
                    "NodeSize",
                    "SGD_total_median",
                    # "SGD_mean_median",
                    "X_total_median",
                    # "X_mean_median",
                    "Y_total_median",
                    # "Y_mean_median",
                    "Iter_total_median",
                    # "Iter_mean_median",
                ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"✓ Saved: {output_path}")
    else:
        print(f"No results for {method}/{constraint_type}")


def main():
    """メイン処理"""
    base_dir = Path("result/profiles/data/drawing/SNS")

    # 対象メソッド
    methods = [
        "FullSGD(ours)",
        "Inline Projection",
        "Post-processing Projection",
        "UNICON",
        "WebCoLa",
    ]

    # 対象制約タイプ
    constraint_types = ["gap", "layered"]

    print("=" * 60)
    print("タイミング統計計算を開始します")
    print("=" * 60)

    for method in methods:
        print(f"\n[{method}]")
        for constraint_type in constraint_types:
            output_path = (
                base_dir
                / method
                / "watts_strogatz"
                / "neighbor_2"
                / "rewire_030"
                / constraint_type
                / "timing_statistics_re.csv"
            )
            process_constraint_type(base_dir, method, constraint_type, output_path)

    print("\n" + "=" * 60)
    print("すべての統計計算が完了しました")
    print("=" * 60)


if __name__ == "__main__":
    main()
