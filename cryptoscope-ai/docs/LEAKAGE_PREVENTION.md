# CryptoScope AI — Data Leakage Prevention Guidelines

---

## 🛑 Strict Rules for Time-Series Integrity

1. **Point-In-Time Availability**:
   - For every feature: `available_time <= prediction_time (T)`.
   - Never train or backtest using revised macroeconomic releases or restated on-chain metrics as though they were known at event time.
2. **Scaler & Preprocessor Isolation**:
   - Normalizers, standardizers, and scalers (`StandardScaler`, `MinMaxScaler`) must be fitted **only on historical training windows**.
   - Global fitting over combined train + validation or train + test sets is strictly prohibited.
3. **Chronological Splitting & Embargo**:
   - Random K-Fold cross validation is forbidden.
   - Use Purged Walk-Forward Cross Validation with embargo intervals exceeding the longest forecast horizon.
4. **Automated CI Leakage Test Suite**:
   - Continuous automated unit tests in `tests/leakage/` enforce zero temporal lookahead violations.
