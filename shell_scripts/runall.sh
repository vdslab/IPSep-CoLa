#!/bin/bash
# =============================================================================
# runall.sh - 複数の実験を順次実行するスクリプト
# =============================================================================
#
# このスクリプトは、Watts-Strogatzグラフ (k=2, p=0.3) に対して
# 異なる制約条件での実験を順次実行します。
#
# 実験タイプ:
#   1. Gap制約 - ランダムなy軸方向のギャップ制約
#   2. Layered制約 - DAGベースの階層的双方向制約
#   3. Overlap除去 - ノードのオーバーラップ除去制約
#
# =============================================================================

cd "$(dirname "$0")/.." || exit

# -----------------------------------------------------------------------------
# 実験パラメータ設定
# -----------------------------------------------------------------------------

# グラフサイズの範囲
START=100
END=2000
STEP=100

# 評価メトリクス（Scale-normalized Stress）
EVALUATION="SNS"

# -----------------------------------------------------------------------------
# 実験の実行
# -----------------------------------------------------------------------------

echo "========================================"
echo "実験を開始します"
echo "グラフサイズ: $START - $END (step: $STEP)"
echo "評価メトリクス: $EVALUATION"
echo "========================================"

# Gap制約の実験
echo ""
echo ">>> Gap制約の実験を実行中..."
./shell_scripts/run_experiment.sh \
    'watts_strogatz/neighbor_2/rewire_030/gap' \
    $START $END $STEP \
    'constraint' \
    "$EVALUATION"

# Layered制約の実験
echo ""
echo ">>> Layered制約の実験を実行中..."
./shell_scripts/run_experiment.sh \
    'watts_strogatz/neighbor_2/rewire_030/layered' \
    $START $END $STEP \
    'constraint' \
    "$EVALUATION"

# Overlap除去の実験
echo ""
echo ">>> Overlap除去の実験を実行中..."
./shell_scripts/run_experiment.sh \
    'watts_strogatz/neighbor_2/rewire_030/overlap/rect100' \
    $START $END $STEP \
    'overlap' \
    "$EVALUATION"

echo ""
echo "========================================"
echo "すべての実験が完了しました"
echo "========================================"

# -----------------------------------------------------------------------------
# 参考: 古いコマンドの履歴（アーカイブ）
# -----------------------------------------------------------------------------

# 以下は古いインターフェースを使用したコマンドのアーカイブです。
# 参考のために残していますが、現在は使用されていません。

# for n in `seq -f '%04.0f' 100 100 2000`
# do
#   python scripts/draw.py --space euclidean --dest data/drawing/sgd/overlap/$n --overlap-removal data/graph/overlap/$n/*
# done

# for n in $(seq -f '%04.0f' 100 100 2000); do
# 	python scripts/draw_webcola.py --dest data/drawing/webcola/overlap/$n --overlap-removal data/graph/overlap/$n/*
# done

# for method in sgd webcola
# do
#   for type in random_tree overlap
#   do
#     for n in `seq -f '%04.0f' 100 100 2000`
#     do
#       mkdir -p result/plot/${method}/${type}/${n}
#       for i in `seq -f '%02.0f' 0 19`
#       do
#         node js/src/render.js --graphFile=data/graph/${type}/${n}/node_n\=${n}_${i}.json --drawingFile=data/drawing/${method}/${type}/${n}/node_n\=${n}_${i}.json --output=result/plot/${method}/${type}/${n}/node_n=${n}_${i}.png
#       done
#     done
#   done
# done

# for type in overlap; do
# 	python scripts/calc_stress.py data/graph/$type.csv result/stress/$type-0100-2000.csv
# 	python scripts/create_boxplot.py result/stress/$type-0100-2000.csv result/stress/$type-0100-2000.png
# done
