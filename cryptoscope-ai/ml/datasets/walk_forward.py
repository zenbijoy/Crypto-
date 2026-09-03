"""
CryptoScope AI - Walk-Forward & Purged Cross-Validation
Implements Sections 27 & 29 specifications:
- Strict prevention of data leakage
- Walk-forward validation with embargo periods
- Purged time-series splitting
"""
from typing import List, Tuple, Generator

class WalkForwardValidator:
    def __init__(self, train_window_size: int = 1000, val_window_size: int = 200, embargo_size: int = 20):
        self.train_window_size = train_window_size
        self.val_window_size = val_window_size
        self.embargo_size = embargo_size

    def split(self, n_samples: int) -> Generator[Tuple[List[int], List[int], List[int]], None, None]:
        """
        Yields chronological (train_indices, embargo_indices, val_indices) splits with embargo periods.
        Guarantees that train indices strictly precede val indices.
        """
        start = 0
        while start + self.train_window_size + self.embargo_size + self.val_window_size <= n_samples:
            train_start = start
            train_end = start + self.train_window_size
            
            embargo_start = train_end
            embargo_end = embargo_start + self.embargo_size
            
            val_start = embargo_end  # Embargo prevents overlap autocorrelation leakage
            val_end = val_start + self.val_window_size
            
            train_idx = list(range(train_start, train_end))
            embargo_idx = list(range(embargo_start, embargo_end))
            val_idx = list(range(val_start, val_end))
            
            yield train_idx, embargo_idx, val_idx
            start += self.val_window_size
