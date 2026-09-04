# CryptoScope AI — Firebase Cloud Messaging (FCM) Architecture

**Push Notifications, Payload Schemas & Device Lifecycle**  

---

## 1. Firebase Service Role Boundary

In accordance with strict architectural requirements:
- **Firebase is used solely for FCM Push Notifications** (and optional client-side Crashlytics).
- **Firebase Firestore is NOT used as a quantitative database.**
- **No private service keys are bundled in the Android client.** Firebase Admin SDK credentials reside strictly on the backend server (`/secrets/firebase-service-account.json`).

---

## 2. Device Registration Flow

```
[ Android Client ]
        │
        │ 1. Generates FCM Device Token on launch
        ▼
[ Android Client ]
        │
        │ 2. Calls POST /api/v1/devices
        │    Header: Authorization: Bearer <Supabase_JWT>
        │    Body: { "device_token": "fcm_token_xyz", "platform": "android" }
        ▼
[ FastAPI Backend ]
        │
        │ 3. Stores in product.device_tokens linked to Supabase User UUID
        ▼
[ PostgreSQL: product.device_tokens ]
```

---

## 3. Push Event Types & Payload Schema

All push notification payloads sent via `services/notifications/service.py` adhere to the canonical schema:

| Event Type | Title Format | Body Content | Deep Link URI |
|---|---|---|---|
| `prediction_signal` | 🤖 AI Signal: {symbol} | Probable {direction} ({horizon}) with {confidence}% confidence | `cryptoscope://prediction/{symbol}` |
| `liquidation_alert` | 💥 Liquidation Surge | ${volume_usd}M liquidated on {symbol} across venues | `cryptoscope://liquidations/{symbol}` |
| `funding_alert` | ⚠️ Extreme Funding Rate | {symbol} funding rate reached {rate_bps} bps | `cryptoscope://derivatives/{symbol}` |
| `oi_alert` | 📈 Open Interest Outlier | {symbol} OI surged by {change_pct}% in 1 hour | `cryptoscope://radar` |
| `provider_issue` | 🚨 Market Feed Alert | Feed {provider} status: {status} | `cryptoscope://health` |
| `paper_result` | 💼 Paper Trade Closed | {symbol} {side} closed with PnL: ${pnl_usd} | `cryptoscope://paper` |

Payloads include structured data keys (`event_type`, `symbol`, `prediction_id`, `deep_link`) enabling background routing on Android.
