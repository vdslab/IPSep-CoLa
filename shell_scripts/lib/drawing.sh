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
    
    uv run --project "$REPO_ROOT/cli" draw --space euclidean \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag \
        "$graph_file"
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
    
    node "$REPO_ROOT/js/src/draw_webcola.js" \
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
    
    uv run --project "$REPO_ROOT/cli" draw-unicon \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag \
        "$graph_file"
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
    
    uv run --project "$REPO_ROOT/cli" draw \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag \
        "$graph_file"
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
    
    uv run --project "$REPO_ROOT/cli" draw \
        --space 'after_project' \
        --dest "$output_dir" \
        --output-suffix "_run_${run_id}" \
        $overlap_flag \
        "$graph_file"
}

# -----------------------------------------------------------------------------
# グラフ描画処理
# -----------------------------------------------------------------------------

# 1つのグラフ描画実行を処理する関数
# 引数:
#   $1: n - ノード数
#   $2: i - グラフ番号
#   $3: run_id - 実行ID
# 環境変数から取得:
#   METHOD_NAME, GRAPH_DIR_EXPORT, DRAWING_DIR_EXPORT, TYPE_EXPORT
#   OVERLAP_FLAG_EXPORT, WEBCOLA_OVERLAP_FLAG_EXPORT
#   SGD_EXPORT, WEBCOLA_EXPORT, UNICON_EXPORT, INLINE_EXPORT, POSTPROCESS_EXPORT
process_single_run() {
    local n=$1
    local i=$2
    local run_id=$3
    
    # 環境変数から値を取得
    local method_name="$METHOD_NAME"
    local graph_dir="$GRAPH_DIR_EXPORT"
    local drawing_dir="$DRAWING_DIR_EXPORT"
    local type="$TYPE_EXPORT"
    local overlap_flag="$OVERLAP_FLAG_EXPORT"
    local webcola_overlap_flag="$WEBCOLA_OVERLAP_FLAG_EXPORT"
    local sgd="$SGD_EXPORT"
    local webcola="$WEBCOLA_EXPORT"
    local unicon="$UNICON_EXPORT"
    local inline="$INLINE_EXPORT"
    local postprocess="$POSTPROCESS_EXPORT"
    
    local PAUSE_FLAG="/tmp/draw.pause"
    
    # PAUSE_FLAGのチェック
    while [ -f "$PAUSE_FLAG" ]; do sleep 1; done
    
    local graph_file="$graph_dir/$type/$n/node_n=${n}_$i.json"
    local output_dir="$drawing_dir/$method_name/$type/$n"
    
    # ディレクトリ作成
    mkdir -p "$output_dir"
    
    # 手法に応じた処理
    case "$method_name" in
        "$sgd")
            run_fullsgd "$graph_file" "$output_dir" "$run_id" "$overlap_flag"
            ;;
        "$webcola")
            local output_file="$output_dir/node_n=${n}_${i}_run_${run_id}.json"
            run_webcola "$graph_file" "$output_file" "$webcola_overlap_flag"
            ;;
        "$unicon")
            run_unicon "$graph_file" "$output_dir" "$run_id" "$overlap_flag"
            ;;
        "$inline")
            run_inline "$graph_file" "$output_dir" "$run_id" "$overlap_flag"
            ;;
        "$postprocess")
            run_postprocess "$graph_file" "$output_dir" "$run_id" "$overlap_flag"
            ;;
        *)
            echo "エラー: 未知の手法です - $method_name" >&2
            exit 1
            ;;
    esac
}

# 指定された手法でグラフを描画します。
# 引数:
#   $1: method_name - 手法名
# グローバル変数の使用:
#   $GRAPH_DIR, $DRAWING_DIR, $TYPE, $START, $STEP, $END
#   $OVERLAP_FLAG, $WEBCOLA_OVERLAP_FLAG
#   $SGD, $WEBCOLA, $UNICON, $INLINE, $POSTPROCESS
#   $PARALLEL_JOBS - 並列ジョブ数
draw_graphs() {
    local method_name="$1"
    
    # 関数をエクスポート（parallelで使用するため）
    export -f process_single_run
    export -f run_fullsgd run_webcola run_unicon run_inline run_postprocess
    
    # 複雑な変数（スペースや括弧を含む）を環境変数としてエクスポート
    export METHOD_NAME="$method_name"
    export GRAPH_DIR_EXPORT="$GRAPH_DIR"
    export DRAWING_DIR_EXPORT="$DRAWING_DIR"
    export TYPE_EXPORT="$TYPE"
    export OVERLAP_FLAG_EXPORT="$OVERLAP_FLAG"
    export WEBCOLA_OVERLAP_FLAG_EXPORT="$WEBCOLA_OVERLAP_FLAG"
    export SGD_EXPORT="$SGD"
    export WEBCOLA_EXPORT="$WEBCOLA"
    export UNICON_EXPORT="$UNICON"
    export INLINE_EXPORT="$INLINE"
    export POSTPROCESS_EXPORT="$POSTPROCESS"
    
    echo "  並列処理中: $method_name (並列度: $PARALLEL_JOBS)"
    
    # 全組み合わせを1回のparallelで処理（環境変数を使用）
    parallel --bar --line-buffer -j "$PARALLEL_JOBS" \
        process_single_run {1} {2} {3} \
        ::: $(seq -f "%04g" "$START" "$STEP" "$END") \
        ::: $(seq -w 0 19) \
        ::: $(seq 0 9)
}

# -----------------------------------------------------------------------------
# 結果プロット処理
# -----------------------------------------------------------------------------

# 描画結果をプロットします（最初の実行結果 run_0 を使用）。
# 引数:
#   $1: method_name - 手法名
# グローバル変数の使用:
#   $GRAPH_DIR, $DRAWING_DIR, $PLOT_DIR, $TYPE, $START, $STEP, $END, $PARALLEL_PLOTS
plot_results() {
    local method_name="$1"
    
    # ノード数とグラフ番号の組み合わせを並列化
    seq -f "%04g" "$START" "$STEP" "$END" | parallel --line-buffer -j "$PARALLEL_PLOTS" "
        n={}
        # サンプル0, 5, 10, 15のみプロット
        for i in 00 05 10 15; do
            uv run --project \"$REPO_ROOT/cli\" plot \
                \"$GRAPH_DIR/$TYPE/\$n/node_n=\${n}_\${i}.json\" \
                \"$DRAWING_DIR/$method_name/$TYPE/\$n/node_n=\${n}_\${i}_run_0.json\" \
                \"$PLOT_DIR/$method_name/$TYPE/\$n/node_n=\${n}_\${i}_run_0.png\"
        done
    "
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
