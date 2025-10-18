# Watchtower — Status & Bringup (Oct 18, 2025)

This repo implements a **privacy-first, on-device weapon detection layer** that watches existing camera feeds and emits human-verified alerts. No cloud dependency. No auto-911.

## Repo status
- Default branch: `main` (tracking commit 81b59d1)
- Key files present: `app.py`, `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `.env.example`, `config.yml`
- Container entrypoint uses `uvicorn app:app --host 0.0.0.0 --port 8002`

## Bringup (local)
1. Python 3.11 recommended.
2. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set values.
5. `python app.py` (or `uvicorn app:app --reload --port 8002`).

## Bringup (Docker)
```bash
# Build and run the API on port 8002
docker build -t watchtower-edge .
docker run --env-file .env -p 8002:8002 watchtower-edge
```

If you prefer compose:
```bash
docker compose up --build
```

## Open tasks
- [ ] **Stream ingest**: Harden RTSP/USB ingest with auto-retry, backoff, and health pings.
- [ ] **Detector wrapper**: Plug a lightweight model (e.g., YOLOv8n/YOLOv10n) with on-device inference via CPU first; leave hooks for CUDA/TensorRT.
- [ ] **Zones & masking**: Support ROI polygons and dynamic masks to respect privacy (block doors, faces, bathrooms, etc.).
- [ ] **Event pipeline**: Frame buffer → detection → NMS → redact snapshot → temporary disk cache.
- [ ] **Human verify loop**: Minimal review UI (LAN-only by default) that shows redacted clip/frame before alerting.
- [ ] **Notifiers**: Pluggable sinks (SMS/Email/Webhook) with rate limiting and escalation rules.
- [ ] **Config**: YAML-driven profiles per camera (fps, resolution, model, sensitivity, postproc thresholds).
- [ ] **Logging & metrics**: Structured logs + /health and /metrics endpoints.
- [ ] **Docs**: Usage, config examples, and a small sample clip for offline tests.

## Quick test (dummy camera)
- Use a local webcam: `rtsp://test:8554/stream` or OpenCV index `0`.
- Run `/health` to confirm the service, then POST `/cameras/register` with a feed URL.

---
*Status file generated to coordinate next steps. Update freely.*
