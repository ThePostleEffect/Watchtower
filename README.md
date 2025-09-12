# Watchtower
Watchtower adds a privacy-first AI layer to your existing cameras to detect visible, brandished weapons and deliver human-verified alerts—no cloud dependency, no auto-911.

# Watchtower — On-Prem AI Safety (Visible Weapon Detection + Human-Verified Alerts)

**Goal:** Add a privacy-first AI layer to existing RTSP/ONVIF cameras that detects **visible, brandished firearms**, pushes **human-verified** alerts, and saves short evidence clips.

## Quick start (dev)
1) Install Docker & Docker Compose.
2) `cp .env.example .env` and fill values (RTSP pass, optional Telegram).
3) Edit `edge/frigate/config.yml` with your camera RTSP URLs.
4) From `edge/`: `docker compose up -d`
5) Open **Frigate UI** at http://localhost:5000 to confirm camera ingest.

**Services**
- **Frigate** — person detect, zones, clips (on-prem)
- **Sidecar** — YOLO weapon check on person crops → `weapon_visible` events
- **Notifier** — fan-out to Telegram/webhooks; **Verify / Dismiss / Escalate** endpoints

## Scope & Safety
- Detects **brandished** weapons only (no concealed detection).
- **Human verification required** before siren/locks/911.
- On-prem storage; retention 7–30 days (configurable).

## Dev tasks
- [ ] Person-crop pipeline (sidecar) with persistence filter
- [ ] Notifier actions API (+ Telegram/webhook adapters)
- [ ] Metrics log: FP rate, alert fan-out time
- [ ] Tests: unit for sidecar; integration with Frigate events
- [ ] Model weights management (see `MODEL.md`)
- [ ] Basic CI (lint, type-check, unit tests)

See `docs/ROADMAP.md` for milestones and acceptance criteria.

