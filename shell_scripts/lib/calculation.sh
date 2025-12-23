#!/bin/bash
# =============================================================================
# calculation.sh - ストレスと制約違反の計算処理
# =============================================================================

# -----------------------------------------------------------------------------
# 計算処理
# -----------------------------------------------------------------------------

# ストレスと制約違反を計算します。
# 引数:
#   $@: methods - 評価する手法のリスト
# グローバル変数の使用:
#   $OUTPUT_CSV, $STRESS_DIR, $VIOLATION_DIR, $VIOLATION_TYPE
calculation() {
    log_info "結果を計算中..."
    local methods=("$@")
    local result_prefix=$(get_result_prefix)
    
    # ストレス（Stress）の計算
    python scripts/calc_stress.py \
        "$OUTPUT_CSV" \
        "$STRESS_DIR/$result_prefix.csv" \
        --methods "${methods[@]}"
    
    # 制約違反（Violation）の計算
    python scripts/calc_violation.py \
        "$OUTPUT_CSV" \
        "$VIOLATION_DIR/$result_prefix.csv" \
        --methods "${methods[@]}" \
        --violations "$VIOLATION_TYPE"
    
    log_info "計算が完了しました"
}

# -----------------------------------------------------------------------------
# 比率計算
# -----------------------------------------------------------------------------

# ストレス削減率を計算します。
# 引数:
#   $1: baseline_method - ベースライン手法
#   $2: proposed_method - 提案手法
# グローバル変数の使用:
#   $STRESS_DIR, $RATIO_DIR
calc_ratio() {
    local baseline_method="$1"
    local proposed_method="$2"
    local result_prefix=$(get_result_prefix)
    
    python scripts/compare_stress_ratio.py \
        "$STRESS_DIR/$result_prefix.csv" \
        "$RATIO_DIR/${result_prefix}_${baseline_method}_${proposed_method}_ratio.csv" \
        --methods "$baseline_method" "$proposed_method"
}
