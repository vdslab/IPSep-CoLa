import time
import json
import csv
from contextlib import contextmanager
from functools import wraps
from typing import Dict, List, Optional, Callable


_global_timer_stats = None


class TimerStats:
    """時間計測の統計情報を管理するクラス"""
    
    def __init__(self, timing_level: int = 3, quiet: bool = False):
        """
        Args:
            timing_level: 詳細度レベル
                0 - 計測なし
                1 - 全体の合計時間のみ
                2 - イテレーションごとの合計時間
                3 - 各処理の詳細な時間（デフォルト）
            quiet: Trueの場合、計測は行うがprint出力を抑制
        """
        self.timing_level = timing_level
        self.quiet = quiet
        self.times: Dict[str, List[float]] = {}
        self.total_start = None
        self.total_elapsed = 0
    
    def start_total(self):
        """全体の計測を開始"""
        self.total_start = time.perf_counter()
    
    def end_total(self):
        """全体の計測を終了"""
        if self.total_start is not None:
            self.total_elapsed = time.perf_counter() - self.total_start
    
    def record(self, name: str, elapsed: float):
        """時間を記録"""
        if name not in self.times:
            self.times[name] = []
        self.times[name].append(elapsed)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """指定された処理の統計情報を取得"""
        if name not in self.times or not self.times[name]:
            return {}
        
        times = self.times[name]
        return {
            "count": len(times),
            "total": sum(times),
            "mean": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "std": (sum((t - sum(times) / len(times)) ** 2 for t in times) / len(times)) ** 0.5
        }
    
    def print_summary(self):
        """統計情報を出力"""
        if self.timing_level == 0 or self.quiet:
            return  # quietモードではprint出力を抑制
        
        print("\n" + "="*60)
        print("時間計測結果")
        print("="*60)
        
        if self.timing_level == 1:
            print(f"総実行時間: {self.total_elapsed:.4f}秒")
            print("="*60 + "\n")
            return
        
        # イテレーション単位の集計
        iteration_times = {k: v for k, v in self.times.items() if k.startswith("Iteration_")}
        other_times = {k: v for k, v in self.times.items() if not k.startswith("Iteration_")}
        
        if self.timing_level == 2 and iteration_times:
            print("\nイテレーションごとの実行時間:")
            for name in sorted(iteration_times.keys(), key=lambda x: int(x.split("_")[1])):
                times = iteration_times[name]
                if times:
                    print(f"  {name}: {times[0]:.4f}秒")
            print(f"\n総実行時間: {self.total_elapsed:.4f}秒")
            print("="*60 + "\n")
            return
        
        # Level 3: 詳細な統計情報
        if iteration_times and self.timing_level >= 2:
            print("\nイテレーション統計:")
            stats = self.get_stats_for_group(iteration_times)
            if stats:
                self._print_stats_table(stats)
        
        if other_times and self.timing_level == 3:
            print("\n処理別統計:")
            stats = self.get_stats_for_group(other_times)
            if stats:
                self._print_stats_table(stats)
        
        print(f"\n総実行時間: {self.total_elapsed:.4f}秒")
        print("="*60 + "\n")
    
    def get_stats_for_group(self, time_dict: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """グループの統計情報を取得"""
        return {name: self.get_stats(name) for name in time_dict.keys()}
    
    def _print_stats_table(self, stats: Dict[str, Dict[str, float]]):
        """統計情報をテーブル形式で出力"""
        print(f"{'処理名':<30} {'回数':>6} {'合計(秒)':>10} {'平均(秒)':>10} {'最小(秒)':>10} {'最大(秒)':>10}")
        print("-" * 80)
        for name, stat in stats.items():
            if stat:
                print(f"{name:<30} {stat['count']:>6} {stat['total']:>10.4f} {stat['mean']:>10.4f} "
                      f"{stat['min']:>10.4f} {stat['max']:>10.4f}")
    
    def save(self, filepath: str):
        """結果をファイルに保存（JSON と CSV の両方）"""
        self._save_json(f"{filepath}.json")
        self._save_csv(f"{filepath}.csv")
        if not self.quiet:
            print(f"計測結果を保存しました: {filepath}.json, {filepath}.csv")
    
    def _save_json(self, filepath: str):
        """JSON形式で保存"""
        data = {
            "total_elapsed": self.total_elapsed,
            "timing_level": self.timing_level,
            "raw_times": self.times,
            "statistics": {}
        }
        
        for name in self.times.keys():
            data["statistics"][name] = self.get_stats(name)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_csv(self, filepath: str):
        """CSV形式で保存（イテレーションごと）"""
        # イテレーション単位のデータを抽出
        iteration_times = {k: v for k, v in self.times.items() if k.startswith("Iteration_")}
        other_times = {k: v for k, v in self.times.items() if not k.startswith("Iteration_")}
        
        if not iteration_times and not other_times:
            return
        
        # ヘッダーを準備
        headers = ["Iteration"]
        other_keys = sorted(other_times.keys())
        headers.extend(other_keys)
        
        # イテレーション数を取得
        max_iterations = max(len(v) for v in other_times.values()) if other_times else 0
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for i in range(max_iterations):
                row = [i]
                for key in other_keys:
                    if i < len(other_times[key]):
                        row.append(f"{other_times[key][i]:.6f}")
                    else:
                        row.append("")
                writer.writerow(row)


def enable_profiling(timing_level: int = 3, timing_output_file: Optional[str] = None, quiet: bool = False) -> TimerStats:
    """
    計測を有効化（グローバル設定）
    
    Args:
        timing_level: 詳細度レベル (0-3)
        timing_output_file: 出力ファイルパス（拡張子なし）
        quiet: Trueの場合、計測は行うがprint出力を抑制
    
    Returns:
        TimerStats インスタンス
    """
    global _global_timer_stats
    _global_timer_stats = TimerStats(timing_level, quiet)
    _global_timer_stats.start_total()
    return _global_timer_stats


def disable_profiling() -> Optional[TimerStats]:
    """計測を無効化し、結果を返す"""
    global _global_timer_stats
    if _global_timer_stats is not None:
        _global_timer_stats.end_total()
    stats = _global_timer_stats
    _global_timer_stats = None
    return stats


def timed(name: str):
    """
    関数の実行時間を計測するデコレータ
    
    Args:
        name: 計測時の識別名
    
    Example:
        @timed("my_function")
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _global_timer_stats is None or _global_timer_stats.timing_level == 0:
                return func(*args, **kwargs)  # 計測無効時
            
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            _global_timer_stats.record(name, elapsed)
            return result
        return wrapper
    return decorator


@contextmanager
def timer(name: str):
    """
    コンテキストマネージャー版の時間計測
    
    Args:
        name: 計測時の識別名
    
    Example:
        with timer("loop_iteration"):
            # 処理
            pass
    """
    if _global_timer_stats is None or _global_timer_stats.timing_level == 0:
        yield  # 計測無効時は何もしない
        return
    
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    _global_timer_stats.record(name, elapsed)


def profiler(func: Optional[Callable] = None, timing_level: int = 3, timing_output_file: Optional[str] = None, quiet: bool = False):
    """
    関数全体をプロファイリングするデコレータ/ラッパー
    
    Args:
        func: 計測対象の関数
        timing_level: 詳細度レベル (0-3)
        timing_output_file: 出力ファイルパス（拡張子なし）
        quiet: Trueの場合、計測は行うがprint出力を抑制
    
    Example:
        # ラッパーとして使用
        sgd_profile = profiler(sgd, timing_level=3, timing_output_file="results/timing", quiet=False)
        pos = sgd_profile(nx_graph, ...)
        
        # デコレータとして使用
        @profiler(timing_level=3, timing_output_file="results/timing", quiet=True)
        def my_function():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            stats = enable_profiling(timing_level, timing_output_file, quiet)
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                stats.end_total()
                stats.print_summary()
                if timing_output_file:
                    stats.save(timing_output_file)
                disable_profiling()
        return wrapper
    
    # 関数が渡された場合（ラッパーとして使用）
    if func is not None:
        return decorator(func)
    
    # デコレータとして使用
    return decorator
