from fastapi import FastAPI
import os, json, requests, cv2, numpy as np
import paho.mqtt.client as mqtt
from ultralytics import YOLO

# --- Env / config ---
BROKER = os.getenv("MQTT_HOST", "mosquitto")
TOPIC  = os.getenv("MQTT_TOPIC", "frigate/events")
CONF_TH = float(os.getenv("GUN_CONF", "0.6"))
PERSIST_FRAMES = int(os.getenv("PERSIST_FRAMES", "6"))  # ~0.5s @12fps
MODEL_PATH = os.getenv("MODEL_PATH", "/app/weights/gun.pt")

app = FastAPI(title="Watchtower Sidecar")

# Load model (place your weights at edge/sidecar/weights/gun.pt)
model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
pending = {}  # event_id -> consecutive frames above threshold

def run_gun_check(img_bgr) -> float:
    """Return max confidence that a visible weapon is present."""
    if model is None:
        return 0.0
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    res = model.predict(img_rgb, verbose=False)
    conf = 0.0
    for r in res:
        if getattr(r, "boxes", None) and len(r.boxes):
            conf = max(conf, float(r.boxes.conf.max().cpu()))
    return conf

def handle_person_event(ev):
    snap = ev.get("after", {}).get("snapshot", {})
    url  = snap.get("url")
    event_id = ev.get("id")
    if not url or not event_id:
        return

    try:
        img_bytes = requests.get(url, timeout=2).content
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        return

    conf = run_gun_check(img)
    if conf >= CONF_TH:
        pending[event_id] = pending.get(event_id, 0) + 1
        if pending[event_id] >= PERSIST_FRAMES:
            payload = {
                "event_id": event_id,
                "camera": ev.get("after", {}).get("camera"),
                "type": "weapon_visible",
                "confidence": round(conf, 2),
                "snapshot": url,
                "ts": ev.get("after", {}).get("start_time")
            }
            # Send to notifier
            try:
                requests.post("http://notifier:8002/notify", json=payload, timeout=2)
            except Exception:
                pass
    else:
        pending[event_id] = 0

def on_mqtt(client, userdata, msg):
    try:
        ev = json.loads(msg.payload.decode())
        if ev.get("type") == "new" and ev.get("after", {}).get("label") == "person":
            handle_person_event(ev)
    except Exception:
        pass

@app.on_event("startup")
def _start():
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_message = on_mqtt
    c.connect(BROKER, 1883, 60)
    c.subscribe(TOPIC, qos=0)
    c.loop_start()

@app.get("/health")
def health():
    return {"ok": True, "model_loaded": bool(model)}
