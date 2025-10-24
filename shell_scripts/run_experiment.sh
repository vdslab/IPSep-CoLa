#!/bin/bash
cd "$(dirname "$0")/.." || exit

# -----------------------------------------------------------------------------
# 引数チェック
# -----------------------------------------------------------------------------
if [ "$#" -ne 5 ]; then
	echo "Usage: $0 TYPE START END STEP VIOLATION_TYPE"
	exit 1
fi

# -----------------------------------------------------------------------------
# 設定セクション
# -----------------------------------------------------------------------------
# 引数から実験の種類や対象のノード数を設定します。
TYPE="$1"
START="$2"
END="$3"
STEP="$4"
VIOLATION_TYPE="$5"

# 各種ディレクトリのパスを設定します。
GRAPH_DIR="data/graph"
DRAWING_DIR="data/drawing"
STRESS_DIR="result/stress"
VIOLATION_DIR="result/violation"
PLOT_DIR="result/plot"
TYPE_FILE=$(echo "$TYPE" | tr '/' '_')
OUTPUT_CSV="$GRAPH_DIR"/"$TYPE_FILE".csv

# 評価する手法名を定義します。
SGD="FullSGD(ours)"
WEBCOLA="WebCoLa"
UNICON="UNICON"

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
	log_info "グラフリストを ${OUTPUT_CSV} に生成中..."

	echo "name,type,n,path" >"$OUTPUT_CSV"
	for n in $(seq -f "%04g" $START $STEP $END); do
		for i in $(seq -w 0 19); do
			echo "node_n=${n}_$i.json,$TYPE,$n,$TYPE/$n/node_n=${n}_$i.json" >>"$OUTPUT_CSV"
		done
	done
}

# 指定された手法でグラフを描画し、結果をプロットします。
# $1: 手法名 (例: "FullSGD(ours)", "WebCoLa", "UNICON")
process_method() {
	local method_name="$1"
	log_info "処理中: $method_name"

	for n in $(seq -f "%04g" $START $STEP $END); do
		echo "  ノード数: $n"
		mkdir -p "$DRAWING_DIR/$method_name/$TYPE/$n"

		# 各グラフに対して10回実行（GNU Parallelで並列化）
		for i in $(seq -w 0 19); do
			echo "    サブグラフ: $i"

			# GNU Parallelで3回の実行を並列処理
			seq 0 9 | parallel --bar -j 3 "
				run={}
				case '$method_name' in
				'$SGD')
					python scripts/draw.py --space euclidean \
						'$GRAPH_DIR/$TYPE/$n/node_n=${n}_$i.json' \
						--dest '$DRAWING_DIR/$method_name/$TYPE/$n' \
						--output-suffix '_run_{}'
					;;
				'$WEBCOLA')
					node js/src/draw_webcola.js \
						--graphFile '$GRAPH_DIR/$TYPE/$n/node_n=${n}_$i.json' \
						--output '$DRAWING_DIR/$method_name/$TYPE/$n/node_n=${n}_${i}_run_{}.json'
					;;
				'$UNICON')
					python scripts/draw_unicon.py \
						'$GRAPH_DIR/$TYPE/$n/node_n=${n}_$i.json' \
						--dest '$DRAWING_DIR/$method_name/$TYPE/$n' \
						--output-suffix '_run_{}'
					;;
				*)
					echo 'エラー: 未知の手法です - $method_name' >&2
					exit 1
					;;
				esac
			"
		done

		# 描画結果をプロット (最初の実行結果 run_0 を使用、GNU Parallelで並列化)
		seq -w 0 5 19 | parallel -j 4 "
			python scripts/plot.py \
				'$GRAPH_DIR/$TYPE/$n/node_n=${n}_{}.json' \
				'$DRAWING_DIR/$method_name/$TYPE/$n/node_n=${n}_{}_run_0.json' \
				'$PLOT_DIR/$method_name/$TYPE/$n/node_n=${n}_{}.png'
		"
	done
}

# analyze_results関数のみ、VIOLATION_TYPEを引数で受け取るように変更
analyze_results() {
	log_info "結果を分析中..."
	local methods=("$@")
	local result_prefix="$TYPE-$START-$END"

	# Stress（ストレス）の計算と可視化
	python scripts/calc_stress.py \
		"$OUTPUT_CSV" \
		"$STRESS_DIR/$result_prefix.csv" \
		--methods "${methods[@]}"

	python scripts/create_boxplot.py \
		"$STRESS_DIR/$result_prefix.csv" \
		"$STRESS_DIR"/"$result_prefix"_"${methods[0]}"_"${methods[1]}".png \
		--methods "${methods[0]}" "${methods[1]}" \
		--ylabel "normalized stress" \
		--xlabel "node size"

	# Violation（制約違反）の計算と可視化
	python scripts/calc_violation.py \
		"$OUTPUT_CSV" \
		"$VIOLATION_DIR/$result_prefix.csv" \
		--methods "${methods[@]}" \
		--violations "$VIOLATION_TYPE" # ここを変更

	python scripts/create_boxplot.py \
		"$VIOLATION_DIR/$result_prefix.csv" \
		"$VIOLATION_DIR"/"$result_prefix"_"${methods[0]}"_"${methods[1]}".png \
		--methods "${methods[0]}" "${methods[1]}" \
		--ylabel "average violation" \
		--xlabel "node size"
}
# -----------------------------------------------------------------------------
# メイン処理
# -----------------------------------------------------------------------------
main() {
	local all_methods=("$WEBCOLA" "$SGD" "$UNICON")

	# generate_graph_list

	# for method in "${all_methods[@]}"; do
	# 	process_method "$method"
	# done

	analyze_results "${all_methods[@]}"

	log_info "すべての処理が完了しました。"
}

# スクリプトの実行開始
main
