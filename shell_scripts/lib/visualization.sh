#!/bin/bash
# =============================================================================
# visualization.sh - 可視化処理（Box plot等）
# =============================================================================

# -----------------------------------------------------------------------------
# Box plot生成（共通処理）
# -----------------------------------------------------------------------------

# 単一のBox plotを生成します。
# 引数:
#   $1: input_csv - 入力CSVファイル
#   $2: output_pdf - 出力PDFファイル
#   $3: method1 - 比較手法1
#   $4: method2 - 比較手法2
#   $5: ylabel - Y軸ラベル
create_single_boxplot() {
    local input_csv="$1"
    local output_pdf="$2"
    local method1="$3"
    local method2="$4"
    local ylabel="$5"
    
    uv run python scripts/create_boxplot.py \
        "$input_csv" \
        "$output_pdf" \
        --methods "$method1" "$method2" \
        --ylabel "$ylabel" \
        --xlabel "Number of Nodes"
}

# -----------------------------------------------------------------------------
# ストレスと制約違反のBox plot
# -----------------------------------------------------------------------------

# ストレスと制約違反のBox plotを生成します。
# 引数:
#   $1: method1 - 比較手法1
#   $2: method2 - 比較手法2
# グローバル変数の使用:
#   $STRESS_DIR, $VIOLATION_DIR, $EVALUATION
box_plot() {
    log_info "結果を描画中..."
    local method1="$1"
    local method2="$2"
    local result_prefix=$(get_result_prefix)
    
    # ストレスのBox plot
    create_single_boxplot \
        "$STRESS_DIR/$result_prefix.csv" \
        "$STRESS_DIR/${result_prefix}_${method1}_${method2}.pdf" \
        "$method1" \
        "$method2" \
        "$EVALUATION"
    
    # 制約違反のBox plot
    create_single_boxplot \
        "$VIOLATION_DIR/$result_prefix.csv" \
        "$VIOLATION_DIR/${result_prefix}_${method1}_${method2}.pdf" \
        "$method1" \
        "$method2" \
        "average violation"
}

# -----------------------------------------------------------------------------
# 比率のBox plot
# -----------------------------------------------------------------------------

# ストレス削減率のBox plotを生成します。
# 引数:
#   $1: method1 - 比較手法1（ベースライン）
#   $2: method2 - 比較手法2（提案手法）
# グローバル変数の使用:
#   $RATIO_DIR
ratio_box_plot() {
    local method1="$1"
    local method2="$2"
    local result_prefix=$(get_result_prefix)
    
    uv run python scripts/ratio_boxplot.py \
        "$RATIO_DIR/${result_prefix}_${method1}_${method2}_ratio.csv" \
        "$RATIO_DIR/${result_prefix}_${method1}_${method2}_ratio.pdf" \
        --xlabel "Number of Nodes"
}

# -----------------------------------------------------------------------------
# 統合処理
# -----------------------------------------------------------------------------

# 2つの手法を比較する処理（Box plotと比率計算）。
# 引数:
#   $1: method1 - 比較手法1
#   $2: method2 - 比較手法2
# グローバル変数の使用:
#   各種ディレクトリパス
process_comparison() {
    local method1="$1"
    local method2="$2"
    
    # Box plotの生成
    box_plot "$method1" "$method2"
    
    # 比率の計算
    calc_ratio "$method1" "$method2"
    
    # 比率のBox plot生成
    ratio_box_plot "$method1" "$method2"
}
