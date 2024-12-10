# ipsep-cola

## 環境

use rye

- https://rye-up.com/guide/installation/

```bash
rye sync
```

## stress、violationの比較方法

実行するファイル

- `js/src/cola/calc_position_random_tree.js`
- `src/data/calc_stress.py`
- `src/compare_stress.py`
- `src/sgd/check_constraints.py`
- `src/compare_violation.py`


データは`src/data/random_tree`の中

## 1. webcola

### 1-1. 座標計算、保存

- `js/src/cola/calc_position_random_tree.js`
- 9行目がノード数の範囲
- 38行目が保存先ディレクトリ、最後のbasenameは必須
- ファイル`{node_n}/{i}.json`が生成される

### 1-2. ストレス計算、保存

- `src/data/calc_stress.py`
- 55行目は「1. webcolaの座標計算」で指定した保存先ディレクトリ+`{node_n}`
- 73行目で保存先を指定。ファイル名はそのままにしておく

## 2. ipsepcolaの座標+ストレス保存

- `strss_position_{node_n}.json`という名前で保存
- 中身は`{positions: [[[x11,y11], ...], [[x21, y21], ...]], stresses:[s1, s2, ...]}`

## 3. ストレス比較

- `src/compare_stress.py`
- 21行目：保存先ディレクトリの指定
- 22行目：「1-1. 座標計算」で指定した保存先ディレクトリ。ノード数はいらない
- 23行目：`strss_position_{node_n}.json`があるディレクトリを指定
- 27行目：ノード数の範囲


## 4. violationの計算

- `src/sgd/check_constraints.py`
- sgd、webcolaという関数で、それぞれのviolationを計算している

- 21行目：グラフのデータがあるディレクトリ
- 22行目：保存先のディレクトリ

### 4-1. sgd

- 29行目：「2. ipsepcolaの座標計算+ストレス計算」で保存したファイルが存在するディレクトリを指定
- 33行目：ノード数の範囲指定

### 4-2. webcola

- 66行目：「1-1. 座標計算」で指定したディレクトリ。配下に`{node_n}`というディレクトリがあるもの
- 68行目：ノード数の範囲

## 5. violationの比較

- `src/compare_violation.py`
- 22行目：保存先のディレクトリ
- 23行目：「4. violationの計算」で保存先に指定したディレクトリ
- 28行目：ノード数の範囲
