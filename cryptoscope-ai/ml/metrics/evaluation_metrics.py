"""
CryptoScope AI - Comprehensive Quantitative & ML Metrics Suite
Implements:
- Direction: Balanced Accuracy, MCC, Macro F1, Precision, Recall, Confusion Matrix
- Probability: Brier Score, Log Loss, ECE (Expected Calibration Error)
- Return: MAE, RMSE, Huber, Direction Correlation, Spearman Correlation
- Quantiles: Pinball Loss, Empirical Coverage Probability, Interval Width
- Selective Signals: Precision & Coverage at [100%, 75%, 50%, 25%, 10%, 5%, 1%]
- Quantile Consistency Check: P10 <= P25 <= P50 <= P75 <= P90
"""
import numpy as np
import scipy.stats as stats
from typing import Dict, Any, List, Tuple, Optional
from sklearn.metrics import (
    balanced_accuracy_score,
    matthews_corrcoef,
    f1_score,
    precision_score,
    recall_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    confusion_matrix
)


def compute_expected_calibration_error(
    y_true_binary: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> float:
    """Calculates Expected Calibration Error (ECE) for probabilities."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(y_prob)
    if total_samples == 0:
        return 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        mask = (y_prob > bin_lower) & (y_prob <= bin_upper) if i > 0 else (y_prob >= bin_lower) & (y_prob <= bin_upper)
        bin_size = np.sum(mask)
        if bin_size > 0:
            bin_acc = np.mean(y_true_binary[mask])
            bin_conf = np.mean(y_prob[mask])
            ece += (bin_size / total_samples) * np.abs(bin_acc - bin_conf)

    return float(ece)


def compute_direction_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_probs: np.ndarray) -> Dict[str, Any]:
    """Calculates all Head A classification metrics."""
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist()

    # Brier score (multi-class one-vs-rest average)
    num_classes = 3
    one_hot = np.eye(num_classes)[y_true]
    brier = float(np.mean(np.sum((y_probs - one_hot) ** 2, axis=1)))

    # ECE for max confidence class
    max_probs = np.max(y_probs, axis=1)
    correct_preds = (y_pred == y_true).astype(int)
    ece = compute_expected_calibration_error(correct_preds, max_probs, n_bins=10)

    return {
        "balanced_accuracy": float(bal_acc),
        "mcc": float(mcc),
        "macro_f1": float(macro_f1),
        "brier_score": brier,
        "ece": ece,
        "confusion_matrix": cm
    }


def compute_return_metrics(y_true_ret: np.ndarray, y_pred_ret: np.ndarray) -> Dict[str, Any]:
    """Calculates Head B regression metrics."""
    mae = mean_absolute_error(y_true_ret, y_pred_ret)
    rmse = np.sqrt(mean_squared_error(y_true_ret, y_pred_ret))
    spearman, _ = stats.spearmanr(y_true_ret, y_pred_ret)
    dir_acc = np.mean((np.sign(y_true_ret) == np.sign(y_pred_ret)).astype(float))

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "spearman_corr": float(spearman) if not np.isnan(spearman) else 0.0,
        "sign_accuracy": float(dir_acc)
    }


def compute_quantile_metrics(
    y_true_ret: np.ndarray,
    quantiles_pred: np.ndarray,
    target_quantiles: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Computes quantile loss, interval widths, empirical coverage, and monotonicity compliance.
    quantiles_pred shape: [N, 5] representing P10, P25, P50, P75, P90
    """
    qs = target_quantiles or [0.10, 0.25, 0.50, 0.75, 0.90]
    pinball_losses = []
    coverages = {}

    for i, q in enumerate(qs):
        pred_q = quantiles_pred[:, i]
        err = y_true_ret - pred_q
        loss_q = np.mean(np.maximum((q - 1) * err, q * err))
        pinball_losses.append(float(loss_q))
        coverages[f"P{int(q*100)}_coverage"] = float(np.mean(y_true_ret <= pred_q))

    # Interval width P90 - P10
    interval_80 = quantiles_pred[:, 4] - quantiles_pred[:, 0]
    coverage_80 = np.mean((y_true_ret >= quantiles_pred[:, 0]) & (y_true_ret <= quantiles_pred[:, 4]))

    # Check monotonicity: P10 <= P25 <= P50 <= P75 <= P90
    monotonic_violations = np.sum((quantiles_pred[:, 1:] < quantiles_pred[:, :-1]))

    return {
        "mean_pinball_loss": float(np.mean(pinball_losses)),
        "coverages": coverages,
        "interquantile_width_80": float(np.mean(interval_80)),
        "empirical_coverage_80": float(coverage_80),
        "monotonic_violations": int(monotonic_violations),
        "is_monotonic": bool(monotonic_violations == 0)
    }


def compute_selective_precision(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    confidences: np.ndarray,
    percentiles: List[int] = [100, 75, 50, 25, 10, 5, 1]
) -> List[Dict[str, Any]]:
    """Evaluates precision across top confidence coverage percentiles."""
    results = []
    n = len(y_true)
    sorted_indices = np.argsort(-confidences)

    for p in percentiles:
        k = max(1, int(n * (p / 100.0)))
        top_idx = sorted_indices[:k]
        sub_true = y_true[top_idx]
        sub_pred = y_pred[top_idx]

        long_mask = sub_pred == 2
        short_mask = sub_pred == 0

        long_prec = float(np.mean(sub_true[long_mask] == 2)) if np.any(long_mask) else 0.0
        short_prec = float(np.mean(sub_true[short_mask] == 0)) if np.any(short_mask) else 0.0
        overall_prec = float(np.mean(sub_true == sub_pred))

        results.append({
            "target_coverage_pct": p,
            "actual_coverage_count": k,
            "overall_precision": round(overall_prec * 100.0, 2),
            "long_precision": round(long_prec * 100.0, 2),
            "short_precision": round(short_prec * 100.0, 2),
            "min_confidence": float(confidences[sorted_indices[k - 1]])
        })

    return results
