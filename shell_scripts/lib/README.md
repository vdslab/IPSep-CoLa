# Shell Scripts Library

このディレクトリには、`run_experiment.sh`で使用される共通ライブラリが含まれています。

## ファイル構成

```bash
lib/
├── README.md          # このファイル
├── config.sh          # 設定と定数定義
├── utils.sh           # ユーティリティ関数
├── drawing.sh         # グラフ描画とプロット処理
├── calculation.sh     # ストレスと制約違反の計算
└── visualization.sh   # 可視化処理（Box plot等）
```

## 各ファイルの責任

### config.sh - 設定と定数定義

**主な機能:**

- ディレクトリパスの定義
- 手法名の定義
- 比較ペアの定義
- 設定のヘルパー関数

**主要な関数:**

- `init_config()` - 設定の初期化
- `get_result_prefix()` - 結果ファイル名プレフィックスの生成
- `get_stress_dir()` - ストレスディレクトリパスの取得
- `get_violation_dir()` - 違反ディレクトリパスの取得
- `get_ratio_dir()` - 比率ディレクトリパスの取得

**グローバル変数:**

- `ALL_METHODS` - 全手法のリスト
- `COMPARISON_PAIRS` - 比較ペアのリスト

### utils.sh - ユーティリティ関数

**主な機能:**

- ログ出力
- グラフリスト生成
- 制約フラグ設定
- ディレクトリ作成

**主要な関数:**

- `log_info()` - 情報ログの出力
- `log_error()` - エラーログの出力と終了
- `generate_graph_list()` - グラフリストCSVの生成
- `setup_constraint_flags()` - 制約フラグの設定
- `ensure_directory()` - ディレクトリの作成

### drawing.sh - グラフ描画とプロット処理

**主な機能:**

- 各手法でのレイアウト実行
- グラフ描画処理
- 結果のプロット

**主要な関数:**

- `run_fullsgd()` - FullSGDの実行
- `run_webcola()` - WebCoLaの実行
- `run_unicon()` - UNICONの実行
- `run_inline()` - Inline Projectionの実行
- `run_postprocess()` - Post-processing Projectionの実行
- `draw_graphs()` - グラフ描画処理
- `plot_results()` - 結果のプロット
- `process_method()` - 統合処理（描画+プロット）

**責任分離:**

- 各手法の実行ロジックを独立した関数に分離
- 描画とプロットを別々の関数に分離
- 並列処理の詳細をカプセル化

### calculation.sh - ストレスと制約違反の計算

**主な機能:**

- ストレスの計算
- 制約違反の計算
- ストレス削減率の計算

**主要な関数:**

- `calculation()` - ストレスと制約違反の計算
- `calc_ratio()` - ストレス削減率の計算

### visualization.sh - 可視化処理

**主な機能:**

- Box plotの生成
- 比率のBox plot生成
- 比較処理の統合

**主要な関数:**

- `create_single_boxplot()` - 単一のBox plot生成（共通処理）
- `box_plot()` - ストレスと制約違反のBox plot生成
- `ratio_box_plot()` - 比率のBox plot生成
- `process_comparison()` - 比較処理の統合

**重複削減:**

- Box plot生成の共通処理を`create_single_boxplot()`に集約
- ストレスと制約違反で同じロジックを再利用

## 使用方法

これらのライブラリは`run_experiment.sh`から自動的に読み込まれます：

```bash
source "$LIB_DIR/config.sh"
source "$LIB_DIR/utils.sh"
source "$LIB_DIR/drawing.sh"
source "$LIB_DIR/calculation.sh"
source "$LIB_DIR/visualization.sh"
```

他のスクリプトからも同様に読み込んで使用できます。

## 設計原則

### 1. 責任の分離

各ファイルは明確な責任を持ち、関連する機能のみを含みます。

### 2. DRY（Don't Repeat Yourself）

重複するコードを共通関数に集約し、保守性を向上させます。

### 3. 明確なインターフェース

各関数は明確な引数と戻り値を持ち、ドキュメント化されています。

### 4. グローバル変数の適切な管理

設定値は`config.sh`で一元管理し、ヘルパー関数でアクセスします。

## カスタマイズ

### 新しい手法の追加

1. `config.sh`の手法名定義に追加
2. `drawing.sh`に実行関数を追加（`run_<method>()`）
3. `draw_graphs()`のcase文に追加
4. `ALL_METHODS`配列に追加

### 新しい比較ペアの追加

`config.sh`の`COMPARISON_PAIRS`配列に追加：

```bash
COMPARISON_PAIRS=(
    "$WEBCOLA:$SGD"
    "$UNICON:$SGD"
    "$INLINE:$POSTPROCESS"
    "$NEW_METHOD1:$NEW_METHOD2"  # 追加
)
```

### 評価メトリクスの変更

実行時に引数で指定：

```bash
./run_experiment.sh layer_fix_rel 100 2000 100 gap CustomMetric
```

## リファクタリングの効果

### 保守性の向上

- 機能ごとにファイルが分離され、変更箇所が明確
- 関連するコードがまとまっている

### 再利用性の向上

- 各ライブラリは他のスクリプトからも使用可能
- 共通処理が関数化されている

### 可読性の向上

- メインスクリプトが簡潔（元: 230行 → 新: 100行）
- 各関数がドキュメント化されている

### テスト性の向上

- 各関数を独立してテスト可能
- モックやスタブを使いやすい
