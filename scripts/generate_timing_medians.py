#!/usr/bin/env python3
"""
タイミングデータの中央値を計算してCSVファイルを生成するスクリプト

各アルゴリズムのJSONファイルから適切なタイミングデータを抽出し、
run_0.json～run_9.jsonの中央値を計算して、CSVファイルに出力します。
"""

import csv
import json
import os
from pathlib import Path
from statistics import median


def get_webcola_timing(data):
    """WebCoLaのcola_start値を取得"""
    return data["statistics"]["cola_start"]["mean"]


def get_iteration_sum_timing(data):
    """Iteration_0～Iteration_29の合計時間を取得"""
    total = 0.0
    for i in range(30):
        key = f"Iteration_{i}"
        if key in data["statistics"]:
            total += data["statistics"][key]["mean"]
    return total


def get_postprocessing_timing(data):
    """Post-processing ProjectionのSGD_iterations + After_projectionsを取得"""
    sgd_time = data["statistics"]["SGD_step"]["total"]
    after_time = data["statistics"]["After_projections"]["total"]
    return sgd_time + after_time


# アルゴリズムごとのタイミング取得関数
ALGORITHM_TIMING_FUNCTIONS = {
    "WebCoLa": get_webcola_timing,
    "FullSGD(ours)": get_iteration_sum_timing,
    "UNICON": get_iteration_sum_timing,
    "Inline Projection": get_iteration_sum_timing,
    "Post-processing Projection": get_postprocessing_timing,
}


def collect_timings_for_size(size_dir, algorithm):
    """指定されたサイズディレクトリからrun_0.json～run_9.jsonの値を収集"""
    timings = []
    timing_func = ALGORITHM_TIMING_FUNCTIONS[algorithm]

    for run_idx in range(10):
        json_path = size_dir / f"run_{run_idx}.json"
        if json_path.exists():
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                timing = timing_func(data)
                timings.append(timing)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Error reading {json_path}: {e}")
        else:
            print(f"Warning: {json_path} not found")

    return timings


def process_algorithm_constraint(base_path, algorithm, constraint_path):
    """
    特定のアルゴリズムと制約条件の組み合わせを処理

    Args:
        base_path: ベースディレクトリ（result/profiles/data/drawing/SNS）
        algorithm: アルゴリズム名
        constraint_path: 制約条件のパス（例: watts_strogatz/neighbor_2/rewire_030/overlap/rect100）
    """
    algorithm_dir = base_path / algorithm / constraint_path

    if not algorithm_dir.exists():
        print(f"Skipping {algorithm_dir} (not found)")
        return

    results = []

    # 0100～2000まで100刻みのディレクトリを処理
    for size in range(100, 2100, 100):
        size_str = f"{size:04d}"
        size_dir = algorithm_dir / size_str

        if size_dir.exists():
            timings = collect_timings_for_size(size_dir, algorithm)

            if timings:
                median_time = median(timings)
                results.append(
                    {"Size": size, "Median_Time": median_time, "Count": len(timings)}
                )
                print(
                    f"  {algorithm} - Size {size}: {median_time:.6f}s (n={len(timings)})"
                )
            else:
                print(f"  {algorithm} - Size {size}: No data")
        else:
            print(f"  {algorithm} - Size {size}: Directory not found")

    # CSVファイルを出力
    if results:
        output_dir = algorithm_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "medians.csv"

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Size", "Median_Time", "Count"])
            writer.writeheader()
            writer.writerows(results)

        print(f"✓ Created: {output_path}")
    else:
        print(f"✗ No results for {algorithm} / {constraint_path}")


def main():
    """メイン処理"""
    base_path = Path("result/profiles/data/drawing/SNS")

    if not base_path.exists():
        print(f"Error: {base_path} not found")
        return

    # アルゴリズムと制約条件の組み合わせを処理
    # 現在確認されている制約条件
    constraint_paths = [
        "watts_strogatz/neighbor_2/rewire_030/overlap/rect100",
        "watts_strogatz/neighbor_2/rewire_030/layered",
        "watts_strogatz/neighbor_2/rewire_030/gap",
    ]

    print("=" * 80)
    print("タイミングデータの中央値計算を開始します")
    print("=" * 80)

    for algorithm in ALGORITHM_TIMING_FUNCTIONS.keys():
        print(f"\n処理中: {algorithm}")
        print("-" * 80)

        for constraint_path in constraint_paths:
            process_algorithm_constraint(base_path, algorithm, constraint_path)

    print("\n" + "=" * 80)
    print("処理完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
