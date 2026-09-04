# CryptoScope AI — Test Truth & Verification Audit

**Purpose**: Forensic verification of all unit, integration, and Android Robolectric test suites.  
**Classification System**:
- **REAL BEHAVIOR TEST**: Tests true calculations, state transitions, API contracts, or mathematical properties.
- **SHAPE-ONLY TEST**: Tests only output schema dictionary keys without asserting numerical/logical validity.
- **MOCK-ONLY TEST**: Relies on synthetic stubs that mock out the core behavior being verified.
- **MISNAMED TEST**: Test names claiming to test deep learning or neural models while actually verifying heuristic baselines.
- **OBSOLETE TEST**: Legacy test testing removed endpoints or obsolete data structures.

---

## 1. Test Suite Forensic Ledger

| Test Suite / File | Test Method / Scope | Classification | Findings & Truthfulness Assessment | Remediation & Action Taken |
|---|---|---|---|---|
| `test_deep_learning_architecture.py` | `test_triple_barrier_labeling` | **REAL BEHAVIOR TEST** | Validates true triple-barrier label computation with upper/lower volatility boundaries | Preserved as quantitative ground-truth test |
| `test_deep_learning_architecture.py` | `test_specialist_models_and_meta_ensemble` | **MISNAMED TEST** | File and test names implied deep neural weights; actually tests `Heuristic*Baseline` specialists | Renamed scope to verify calibrated multi-expert baselines and probability simplex ($\sum p_i = 1.0$) |
| `test_deep_learning_architecture.py` | `test_probability_calibration` | **REAL BEHAVIOR TEST** | Verifies isotonic regression and Platt scaling calibration reduction of Brier score | Preserved |
| `test_deep_learning_architecture.py` | `test_abstention_engine` | **REAL BEHAVIOR TEST** | Validates that high uncertainty or conflicting expert signals trigger `NO_SIGNAL` / `NO_TRADE` | Enforces `actionable = False` invariant |
| `test_prediction_and_risk.py` | `test_probability_simplex` | **REAL BEHAVIOR TEST** | Asserts that $p_{\text{up}} + p_{\text{neutral}} + p_{\text{down}} = 1.0 \pm 10^{-4}$ | Passed across all assets and horizons |
| `test_prediction_and_risk.py` | `test_no_trade_not_actionable`| **REAL BEHAVIOR TEST** | Asserts that whenever signal is `NO_TRADE`, `actionable` is strictly `False` | Critical safety invariant verified |
| `test_providers_and_normalization.py` | `test_binance_provider_real_http`| **REAL BEHAVIOR TEST** | Validates Binance USD-M endpoint paths, parameters, and candle structure | Asserts zero fake data fallback |
| `test_providers_and_normalization.py` | `test_bybit_okx_real_semantics` | **REAL BEHAVIOR TEST** | Verifies Bybit Linear and OKX Swap responses return distinct real exchange fields | Prevents deriving Bybit/OKX from Binance formulas |
| `test_feature_engineering.py` | `test_point_in_time_invariants`| **REAL BEHAVIOR TEST** | Verifies that all feature timestamps satisfy `feature_time <= prediction_time` | Strict anti-leakage verification |
| `test_asset_registry.py` | `test_tier_assignment` | **REAL BEHAVIOR TEST** | Validates Tier-1 assignment for BTC, ETH, SOL, DOGE and readiness scoring | Verified dynamic discovery |
| `test_api_endpoints.py` | `test_canonical_v1_routes` | **REAL BEHAVIOR TEST** | Calls FastAPI `/api/v1` routes and verifies canonical JSON envelope structure | Ensures `sources` list only real providers |
| `CryptoFuturesNetworkTest.kt` | `testFuturesTickerSerialization` | **REAL BEHAVIOR TEST** | Tests Moshi deserialization of live Binance USD-M 24hr ticker JSON payloads | Validates float parsing and null safety |
| `CryptoFuturesNetworkTest.kt` | `testKlineArrayParsing` | **REAL BEHAVIOR TEST** | Tests raw multi-element kline arrays deserializing into structured domain models | Validates timestamp and volume conversions |
| `ExampleRobolectricTest.kt` | `verify app_name matches metadata`| **REAL BEHAVIOR TEST** | Asserts platform `metadata.json` matches Android string resource `CryptoScope AI` | Enforces AI Studio Platform Sync Rule |
| `ExampleRobolectricTest.kt` | `verify screen routes include auth`| **REAL BEHAVIOR TEST** | Asserts `ScreenRoute.SIGN_IN` and `SIGN_UP` are first-class destinations in navigation | Verifies full auth flow availability |

---

## 2. Invariant Gate Verification

1. **No False Deep Learning Claims**: All tests testing heuristic baselines are clearly documented as testing analytical/heuristic experts, preserving trust and technical transparency.
2. **Anti-Fabrication Guard**: No test mocks out the prediction engine to simulate artificially high win rates or fake profit factors.
3. **Android JVM Compatibility**: All Android unit and Robolectric tests execute cleanly in local JVM test runner without requiring an emulator.
