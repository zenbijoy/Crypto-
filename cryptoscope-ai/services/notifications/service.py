"""
CryptoScope AI - Notification Service
Implements Phase 32, 33, 34:
- Unified notification interface for FCM (Push), Telegram, and In-App
- Push events: prediction_signal, liquidation_alert, funding_alert, OI_alert, provider_issue, paper_result
- Graceful degradation: reports NOT_CONFIGURED when Firebase credentials or Telegram token absent
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass
from core.config import settings

logger = logging.getLogger("cryptoscope.notifications")

@dataclass
class NotificationMessage:
    event_type: str
    title: str
    body: str
    symbol: Optional[str] = None
    prediction_id: Optional[str] = None
    deep_link: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class NotificationService:
    def __init__(self):
        self.firebase_enabled = bool(settings.FIREBASE_PROJECT_ID and settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH))
        self.telegram_enabled = bool(settings.TELEGRAM_BOT_TOKEN)
        self._fcm_app = None
        
        if self.firebase_enabled:
            self._init_firebase()

    def _init_firebase(self):
        try:
            import firebase_admin
            from firebase_admin import credentials
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                self._fcm_app = firebase_admin.initialize_app(cred)
            else:
                self._fcm_app = firebase_admin.get_app()
            logger.info("Firebase Admin SDK successfully initialized.")
        except Exception as e:
            logger.warning(f"Firebase Admin SDK initialization failed: {str(e)}")
            self.firebase_enabled = False

    async def send_push_fcm(self, device_token: str, message: NotificationMessage) -> Dict[str, Any]:
        """Sends an FCM push notification with structured payload."""
        if not self.firebase_enabled:
            return {
                "status": "NOT_CONFIGURED",
                "reason": "Firebase credentials not configured or file not found",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        try:
            from firebase_admin import messaging
            payload_data = {
                "event_type": message.event_type,
                "symbol": message.symbol or "",
                "prediction_id": message.prediction_id or "",
                "deep_link": message.deep_link or f"cryptoscope://app/{message.symbol or 'markets'}"
            }
            if message.data:
                for k, v in message.data.items():
                    payload_data[k] = str(v)

            fcm_msg = messaging.Message(
                notification=messaging.Notification(
                    title=message.title,
                    body=message.body,
                ),
                data=payload_data,
                token=device_token
            )
            response = messaging.send(fcm_msg)
            return {"status": "DELIVERED", "fcm_message_id": response}
        except Exception as e:
            logger.error(f"FCM delivery error: {str(e)}")
            return {"status": "FAILED", "error": str(e)}

    async def send_telegram_alert(self, chat_id: str, message: NotificationMessage) -> Dict[str, Any]:
        """Dispatches an alert message to a linked Telegram chat."""
        if not self.telegram_enabled:
            return {
                "status": "NOT_CONFIGURED",
                "reason": "Telegram bot token not configured",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        try:
            import httpx
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            text = f"🚨 *{message.title}*\n\n{message.body}\n"
            if message.symbol:
                text += f"\nAsset: `{message.symbol}`"
            if message.deep_link:
                text += f"\nView: {message.deep_link}"

            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
                return {"status": "DELIVERED" if res.status_code == 200 else "FAILED", "code": res.status_code}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    async def send(self, channels: List[str], recipient: str, message: NotificationMessage) -> Dict[str, Any]:
        """Unified dispatch to requested channels."""
        results = {}
        for ch in channels:
            if ch == "fcm":
                results["fcm"] = await self.send_push_fcm(recipient, message)
            elif ch == "telegram":
                results["telegram"] = await self.send_telegram_alert(recipient, message)
            elif ch == "in_app":
                results["in_app"] = {"status": "RECORDED", "timestamp": datetime.now(timezone.utc).isoformat()}
        return results

notification_service = NotificationService()
