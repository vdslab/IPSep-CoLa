#!/bin/bash
# =============================================================================
# run_experiment.sh - グラフレイアウト実験のメインスクリプト
# =============================================================================
#
# 使用方法:
#   ./run_experiment.sh TYPE START END STEP VIOLATION_TYPE [EVALUATION]
#
# 引数:
#   TYPE            - 実験タイプ (例: "layer_fix_rel", "overlap")
#   START           - 開始ノード数 (例: 100)
#   END             - 終了ノード数 (例: 2000)
#   STEP            - ステップ数 (例: 100)
#   VIOLATION_TYPE  - 制約違反タイプ (例: "gap", "overlap")
#   EVALUATION      - 評価メトリクス (オプション、デフォルト: "SNS")
#
# 例:
#   ./run_experiment.sh layer_fix_rel 100 2000 100 gap
#   ./run_experiment.sh overlap 100 500 100 overlap SNS
#
# =============================================================================

cd "$(dirname "$0")/.." || exit

# -----------------------------------------------------------------------------
# ライブラリの読み込み
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(dirname "$0")"
LIB_DIR="$SCRIPT_DIR/lib"

# 各ライブラリファイルを読み込む
source "$LIB_DIR/config.sh"
source "$LIB_DIR/utils.sh"
source "$LIB_DIR/drawing.sh"
source "$LIB_DIR/calculation.sh"
source "$LIB_DIR/visualization.sh"

# -----------------------------------------------------------------------------
# 引数チェック
# -----------------------------------------------------------------------------

if [ "$#" -lt 5 ] || [ "$#" -gt 6 ]; then
    echo "Usage: $0 TYPE START END STEP VIOLATION_TYPE [EVALUATION]"
    echo ""
    echo "Arguments:"
    echo "  TYPE            実験タイプ (例: layer_fix_rel, overlap)"
    echo "  START           開始ノード数 (例: 100)"
    echo "  END             終了ノード数 (例: 2000)"
    echo "  STEP            ステップ数 (例: 100)"
    echo "  VIOLATION_TYPE  制約違反タイプ (例: gap, overlap)"
    echo "  EVALUATION      評価メトリクス (オプション、デフォルト: SNS)"
    echo ""
    echo "Example:"
    echo "  $0 layer_fix_rel 100 2000 100 gap"
    echo "  $0 overlap 100 500 100 overlap SNS"
    exit 1
fi

# -----------------------------------------------------------------------------
# 設定の初期化
# -----------------------------------------------------------------------------

# 引数から設定を初期化
init_config "$1" "$2" "$3" "$4" "$5" "${6:-SNS}"

# 制約フラグの設定
setup_constraint_flags "$VIOLATION_TYPE"

log_info "実験設定:"
echo "  TYPE:           $TYPE"
echo "  ノード数範囲:    $START - $END (step: $STEP)"
echo "  VIOLATION_TYPE: $VIOLATION_TYPE"
echo "  EVALUATION:     $EVALUATION"
echo "  OUTPUT_CSV:     $OUTPUT_CSV"

# -----------------------------------------------------------------------------
# メイン処理
# -----------------------------------------------------------------------------

main() {
    # グラフリストの生成
    generate_graph_list
    
    # 各手法でグラフを描画
    for method in "${ALL_METHODS[@]}"; do
        process_method "$method"
    done
    
    # ストレスと制約違反の計算
    calculation "${ALL_METHODS[@]}"
    
    # 比較ペアの処理
    log_info "手法比較を実行中..."
    for pair in "${COMPARISON_PAIRS[@]}"; do
        IFS=':' read -r method1 method2 <<< "$pair"
        process_comparison "$method1" "$method2"
    done
    
    log_info "すべての処理が完了しました。"
}

# メイン処理の実行
main
