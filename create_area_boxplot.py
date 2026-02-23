import re

import matplotlib.pyplot as plt
import pandas as pd

from src.boxplot_2item import boxplot_seaborn


# 2. filepathから情報抽出
def extract_info(filepath):
    """
    例: 'data/.../node_n=1000_14_run_8.json'
    → node_count=1000, id=14, runid=8
    """
    pattern = r"node_n=(\d+)_(\d+)_run_(\d+)\.json"
    match = re.search(pattern, filepath)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return None, None, None


def extract_median(filepath):
    # 1. データ読み込み
    df = pd.read_csv(
        filepath,
        usecols=["method", "node_count", "area", "filepath"],
    )

    df[["node_count", "id", "runid"]] = df["filepath"].apply(
        lambda x: pd.Series(extract_info(x))
    )

    # 3. (method, node_count, id)ごとにareaの中央値を計算
    median_df = (
        df.groupby(["method", "node_count", "id"])["area"].median().reset_index()
    )
    median_df.rename(columns={"area": "median_area"}, inplace=True)
    return median_df


constrains = ["gap", "layered", "overlap"]
for constraint in constrains:
    sgd_median_df = extract_median(f"FullSGD(ours)_{constraint}_convexhull.csv")
    webcola_median_df = extract_median(f"WebCoLa_{constraint}_convexhull.csv")
    median_df = pd.concat([sgd_median_df, webcola_median_df])
    # 4. boxplot_seaborn用のデータ形式に変換
    methods = median_df["method"].unique()
    toj = {"FullSGD(ours)": "本フレームワーク", "WebCoLa": "WebCoLa"}
    node_counts = sorted(median_df["node_count"].unique())

    data_dict = {}
    for method in methods:
        method_data = []
        for nc in node_counts:
            values = median_df[
                (median_df["method"] == method) & (median_df["node_count"] == nc)
            ]["median_area"].tolist()
            method_data.append(values)

        data_dict[toj[method]] = {"data": method_data, "baseline": []}

    # 5. 描画
    x_labels = [str(nc) for nc in node_counts]
    boxplot_seaborn(data_dict, x_labels, show_legend=True)

    # 6. 軸ラベル設定（日本語）
    plt.xlabel("ノード数")
    plt.ylabel("凸包の面積")
    # タイトルは不要

    # 7. 保存
    plt.savefig(f"area_boxplot_{constraint}.pdf", bbox_inches="tight")
    print(f"保存完了: area_boxplot_{constraint}.pdf")
