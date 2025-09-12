from fastapi import FastAPI
from pydantic import BaseModel
import os, requests
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT  = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_URL    = os.getenv("WEBHOOK_URL", "")

bot = Bot(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None
app = FastAPI(title="Watchtower Notifier")

class Alert(BaseModel):
    event_id: str
    camera: str
    type: str
    confidence: float
    snapshot: str
    ts: float | None = None

@app.post("/notify")
def notify(a: Alert):
    # Human-facing text
    text = f"⚠️ {a.type.replace('_',' ').title()} on {a.camera}\nConf: {a.confidence} • Event: {a.event_id}"
    # Telegram (optional)
    if bot and TELEGRAM_CHAT:
        try:
            bot.send_message(chat_id=TELEGRAM_CHAT, text=text)
            bot.send_photo(chat_id=TELEGRAM_CHAT, photo=a.snapshot)
        except Exception:
            pass
    # Generic webhook (optional)
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json=a.dict(), timeout=2)
        except Exception:
            pass
    return {"ok": True}

@app.get("/health")
def health():
    return {"ok": True}
