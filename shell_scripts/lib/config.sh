#!/bin/bash
# =============================================================================
# config.sh - 実験の設定と定数定義
# =============================================================================

# -----------------------------------------------------------------------------
# ディレクトリパス設定
# -----------------------------------------------------------------------------

# グラフデータとレイアウト結果のディレクトリ
GRAPH_DIR="data/graph"
DRAWING_DIR="data/drawing"
PLOT_DIR="result/plot"

# 評価結果のディレクトリ（EVALUATIONサブディレクトリを含む）
get_stress_dir() {
    echo "result/stress/$EVALUATION"
}

get_violation_dir() {
    echo "result/violation/$EVALUATION"
}

get_ratio_dir() {
    echo "result/ratio/$EVALUATION"
}

# -----------------------------------------------------------------------------
# 手法名の定義
# -----------------------------------------------------------------------------

SGD="FullSGD(ours)"
WEBCOLA="WebCoLa"
UNICON="UNICON"
INLINE="Inline Projection"
POSTPROCESS="Post-processing Projection"

# 全手法のリスト
ALL_METHODS=("$WEBCOLA" "$SGD" "$UNICON" "$POSTPROCESS" "$INLINE")

# -----------------------------------------------------------------------------
# 比較ペアの定義
# -----------------------------------------------------------------------------
# 形式: "method1:method2"
COMPARISON_PAIRS=(
    "$WEBCOLA:$SGD"
    "$UNICON:$SGD"
    "$INLINE:$POSTPROCESS"
)

# -----------------------------------------------------------------------------
# ヘルパー関数
# -----------------------------------------------------------------------------

# 実験結果のファイル名プレフィックスを生成します。
# グローバル変数の使用:
#   $TYPE, $START, $END
# 戻り値:
#   結果ファイル名のプレフィックス (例: "layer_fix_rel-100-2000")
get_result_prefix() {
    echo "$TYPE-$START-$END"
}

# TYPEをファイル名として使用可能な形式に変換します。
# グローバル変数の使用:
#   $TYPE
# 戻り値:
#   変換されたTYPE (例: "layer/fix" -> "layer_fix")
get_type_file() {
    echo "$TYPE" | tr '/' '_'
}

# グラフリストのCSVファイルパスを取得します。
# グローバル変数の使用:
#   $GRAPH_DIR, $TYPE, $EVALUATION
# 戻り値:
#   CSVファイルのパス
get_output_csv() {
    local type_file=$(get_type_file)
    echo "$GRAPH_DIR/${type_file}_${EVALUATION}.csv"
}

# -----------------------------------------------------------------------------
# 初期化
# -----------------------------------------------------------------------------

# 設定の初期化を行います。
# この関数は引数を受け取り、グローバル変数を設定します。
# 引数:
#   $1: TYPE - 実験タイプ
#   $2: START - 開始ノード数
#   $3: END - 終了ノード数
#   $4: STEP - ステップ数
#   $5: VIOLATION_TYPE - 制約違反タイプ
#   $6: EVALUATION - 評価メトリクス (オプション、デフォルト: "SNS")
init_config() {
    TYPE="$1"
    START="$2"
    END="$3"
    STEP="$4"
    VIOLATION_TYPE="$5"
    EVALUATION="${6:-SNS}"  # デフォルトはSNS
    
    # 派生する設定値を計算
    TYPE_FILE=$(get_type_file)
    OUTPUT_CSV=$(get_output_csv)
    STRESS_DIR=$(get_stress_dir)
    VIOLATION_DIR=$(get_violation_dir)
    RATIO_DIR=$(get_ratio_dir)
}
