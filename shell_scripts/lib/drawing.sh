#!/bin/bash
# =============================================================================
# drawing.sh - グラフ描画とプロット処理
# =============================================================================

# -----------------------------------------------------------------------------
# 各手法のレイアウト実行
# -----------------------------------------------------------------------------

# FullSGDでグラフレイアウトを実行します。
# 引数:
#   $1: graph_file - 入力グラフファイルパス
#   $2: output_dir - 出力ディレクトリ
#   $3: run_id - 実行ID
#   $4: overlap_flag - overlap除去フラグ
run_fullsgd() {
    local graph_file="$1"
    local output_dir="$2"
    local run_id="$3"
    local overlap_flag="$4"
    
    python scripts/draw.py --space euclidean \
        "$graph_file" \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag
}

# WebCoLaでグラフレイアウトを実行します。
# 引数:
#   $1: graph_file - 入力グラフファイルパス
#   $2: output_file - 出力ファイルパス
#   $3: webcola_overlap_flag - WebCoLa用overlap除去フラグ
run_webcola() {
    local graph_file="$1"
    local output_file="$2"
    local webcola_overlap_flag="$3"
    
    node js/src/draw_webcola.js \
        --graphFile "$graph_file" \
        --output "$output_file" \
        $webcola_overlap_flag
}

# UNICONでグラフレイアウトを実行します。
# 引数:
#   $1: graph_file - 入力グラフファイルパス
#   $2: output_dir - 出力ディレクトリ
#   $3: run_id - 実行ID
#   $4: overlap_flag - overlap除去フラグ
run_unicon() {
    local graph_file="$1"
    local output_dir="$2"
    local run_id="$3"
    local overlap_flag="$4"
    
    python scripts/draw_unicon.py \
        "$graph_file" \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag
}

# Inline Projectionでグラフレイアウトを実行します。
# 引数:
#   $1: graph_file - 入力グラフファイルパス
#   $2: output_dir - 出力ディレクトリ
#   $3: run_id - 実行ID
#   $4: overlap_flag - overlap除去フラグ
run_inline() {
    local graph_file="$1"
    local output_dir="$2"
    local run_id="$3"
    local overlap_flag="$4"
    
    python scripts/draw.py \
        "$graph_file" \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag
}

# Post-processing Projectionでグラフレイアウトを実行します。
# 引数:
#   $1: graph_file - 入力グラフファイルパス
#   $2: output_dir - 出力ディレクトリ
#   $3: run_id - 実行ID
#   $4: overlap_flag - overlap除去フラグ
run_postprocess() {
    local graph_file="$1"
    local output_dir="$2"
    local run_id="$3"
    local overlap_flag="$4"
    
    python scripts/draw.py \
        --space 'after_project' \
        "$graph_file" \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag
}

# -----------------------------------------------------------------------------
# グラフ描画処理
# -----------------------------------------------------------------------------

# 指定された手法でグラフを描画します。
# 引数:
#   $1: method_name - 手法名
# グローバル変数の使用:
#   $GRAPH_DIR, $DRAWING_DIR, $TYPE, $START, $STEP, $END
#   $OVERLAP_FLAG, $WEBCOLA_OVERLAP_FLAG
#   $SGD, $WEBCOLA, $UNICON, $INLINE, $POSTPROCESS
draw_graphs() {
    local method_name="$1"
    local PAUSE_FLAG="/tmp/draw.pause"
    
    for n in $(seq -f "%04g" "$START" "$STEP" "$END"); do
        echo "  ノード数: $n"
        local output_dir="$DRAWING_DIR/$method_name/$TYPE/$n"
        ensure_directory "$output_dir"
        
        # 各グラフに対して処理
        for i in $(seq -w 0 19); do
            echo "$method_name ノード数: $n サブグラフ: $i"
            local graph_file="$GRAPH_DIR/$TYPE/$n/node_n=${n}_$i.json"
            
            # GNU Parallelで10回の実行を並列処理
            seq 0 9 | parallel --bar -j 10 "
                while [ -f '$PAUSE_FLAG' ]; do sleep 1; done
                
                case '$method_name' in
                '$SGD')
                    $(declare -f run_fullsgd)
                    run_fullsgd '$graph_file' '$output_dir' {} '$OVERLAP_FLAG'
                    ;;
                '$WEBCOLA')
                    $(declare -f run_webcola)
                    local output_file='$output_dir/node_n=${n}_${i}_run_{}.json'
                    run_webcola '$graph_file' \"\$output_file\" '$WEBCOLA_OVERLAP_FLAG'
                    ;;
                '$UNICON')
                    $(declare -f run_unicon)
                    run_unicon '$graph_file' '$output_dir' {} '$OVERLAP_FLAG'
                    ;;
                '$INLINE')
                    $(declare -f run_inline)
                    run_inline '$graph_file' '$output_dir' {} '$OVERLAP_FLAG'
                    ;;
                '$POSTPROCESS')
                    $(declare -f run_postprocess)
                    run_postprocess '$graph_file' '$output_dir' {} '$OVERLAP_FLAG'
                    ;;
                *)
                    echo 'エラー: 未知の手法です - $method_name' >&2
                    exit 1
                    ;;
                esac
            "
        done
    done
}

# -----------------------------------------------------------------------------
# 結果プロット処理
# -----------------------------------------------------------------------------

# 描画結果をプロットします（最初の実行結果 run_0 を使用）。
# 引数:
#   $1: method_name - 手法名
# グローバル変数の使用:
#   $GRAPH_DIR, $DRAWING_DIR, $PLOT_DIR, $TYPE, $START, $STEP, $END
plot_results() {
    local method_name="$1"
    
    for n in $(seq -f "%04g" "$START" "$STEP" "$END"); do
        # GNU Parallelで並列化（サンプル0, 5, 10, 15のみプロット）
        seq -w 0 5 19 | parallel -j 4 "
            python scripts/plot.py \
                '$GRAPH_DIR/$TYPE/$n/node_n=${n}_{}.json' \
                '$DRAWING_DIR/$method_name/$TYPE/$n/node_n=${n}_{}_run_0.json' \
                '$PLOT_DIR/$method_name/$TYPE/$n/node_n=${n}_{}_run_0.png'
        "
    done
}

# -----------------------------------------------------------------------------
# 統合処理
# -----------------------------------------------------------------------------

# 指定された手法でグラフを描画し、結果をプロットします。
# 引数:
#   $1: method_name - 手法名 (例: "FullSGD(ours)", "WebCoLa", "UNICON")
# グローバル変数の使用:
#   各種ディレクトリパス、実験パラメータ
# 戻り値:
#   0: 成功
process_method() {
    local method_name="$1"
    log_info "処理中: $method_name"
    
    # グラフ描画
    draw_graphs "$method_name"
    
    # 結果プロット
    plot_results "$method_name"
    
    log_info "$method_name の処理が完了しました"
    return 0
}
