import re

import pandas as pd


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


# CSVファイルを読み込む
median_df = extract_median("test.csv")

methods = ["FullSGD(ours)", "WebCoLa"]
method_data = []
for method in methods:
    values = median_df[
        (median_df["method"] == method) & (median_df["node_count"] == 1000)
    ]["median_area"].mean()
    method_data.append(values)

result = median_df.groupby("method")["median_area"].median()
print(result)

# print("Method別の平均値:")
print(method_data)
print("削減率", (method_data[1] - method_data[0]) / method_data[1])
