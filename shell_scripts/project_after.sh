#!/bin/bash
cd "$(dirname "$0")/.." || exit

# -----------------------------------------------------------------------------
# 設定セクション
# -----------------------------------------------------------------------------
# 引数から実験の種類や対象のノード数を設定します。
TYPE="project_after_gap"
# TYPE="project_after_fix"
START="100"
END="2000"
STEP="100"
VIOLATION_TYPE="constraint"

# 各種ディレクトリのパスを設定します。
GRAPH_DIR="data/graph"
DRAWING_DIR="data/drawing"
STRESS_DIR="result/stress"
VIOLATION_DIR="result/violation"
PLOT_DIR="result/plot"

# 評価する手法名を定義します。
DURING="Project during layout"
AFTER="Project after layout"

# -----------------------------------------------------------------------------
# 関数定義
# -----------------------------------------------------------------------------

# 処理の開始時にメッセージを表示します。
# $1: メッセージ
log_info() {
	echo "----------------------------------------"
	echo "$1"
	echo "----------------------------------------"
}

# 実験対象となるグラフのリストをCSVファイルとして生成します。
generate_graph_list() {
	log_info "グラフリストを生成中..."
	local output_csv="$GRAPH_DIR/$TYPE.csv"
	echo "name,type,n,path" >"$output_csv"
	for n in $(seq -f "%04g" $START $STEP $END); do
		for i in $(seq -w 0 19); do
			echo "node_n=${n}_$i.json,$TYPE,$n,$TYPE/$n/node_n=${n}_$i.json" >>"$output_csv"
		done
	done
}

# 指定された手法でグラフを描画し、結果をプロットします。
# $1: 手法名 (例: "FullSGD(ours)", "WebCoLa", "UNICON")
process_method() {
	local method_name="$1"
	log_info "処理中: $method_name"

	for n in $(seq -f "%04g" $START $STEP $END); do
		echo "$n"
		# 手法ごとに描画コマンドを実行
		case "$method_name" in
		"$DURING")
			python scripts/draw.py \
				"$GRAPH_DIR/$TYPE/$n"/*.json \
				--dest "$DRAWING_DIR/$method_name/$TYPE/$n"
			;;
		"$AFTER")
			python scripts/draw.py \
				--space "after_project" \
				--dest "$DRAWING_DIR/$method_name/$TYPE/$n" \
				"$GRAPH_DIR/$TYPE/$n"/*.json
			;;
		*)
			echo "エラー: 未知の手法です - $method_name" >&2
			return 1
			;;
		esac

		# 描画結果をプロット
		for i in $(seq -w 0 5 19); do
			python scripts/plot.py \
				"$GRAPH_DIR/$TYPE/$n/node_n=${n}_$i.json" \
				"$DRAWING_DIR/$method_name/$TYPE/$n/node_n=${n}_$i.json" \
				"$PLOT_DIR/$method_name/$TYPE/$n/node_n=${n}_$i.png"
		done
	done
}

# analyze_results関数のみ、VIOLATION_TYPEを引数で受け取るように変更
analyze_results() {
	log_info "結果を分析中..."
	local methods=("$@")
	local result_prefix="$TYPE-$START-$END"

	# Stress（ストレス）の計算と可視化
	# python scripts/calc_stress.py \
	# 	"$GRAPH_DIR/$TYPE.csv" \
	# 	"$STRESS_DIR/$result_prefix.csv" \
	# 	--methods "$AFTER" "$DURING"

	python scripts/create_boxplot.py \
		"$STRESS_DIR/$result_prefix.csv" \
		"$STRESS_DIR/$result_prefix.png" \
		--methods "$AFTER" "$DURING" \
		--title "$AFTER stress vs $DURING stress" \
		--ylabel "normalized stress" \
		--xlabel "node size"

	# Violation（制約違反）の計算と可視化
	# python scripts/calc_violation.py \
	# 	"$GRAPH_DIR/$TYPE.csv" \
	# 	"$VIOLATION_DIR/$result_prefix.csv" \
	# 	--methods "$AFTER" "$DURING" \
	# 	--violations "$VIOLATION_TYPE" # ここを変更

	python scripts/create_boxplot.py \
		"$VIOLATION_DIR/$result_prefix.csv" \
		"$VIOLATION_DIR/$result_prefix.png" \
		--methods "$AFTER" "$DURING" \
		--title "$AFTER violation vs $DURING violation" \
		--ylabel "average violation" \
		--xlabel "node size"
}

# -----------------------------------------------------------------------------
# メイン処理
# -----------------------------------------------------------------------------
main() {
	local all_methods=("$DURING, $AFTER")

	# generate_graph_list

	# for method in "${all_methods[@]}"; do
	# 	process_method "$method"
	# done

	analyze_results "${all_methods[@]}"

	log_info "すべての処理が完了しました。"
}

# スクリプトの実行開始
main
