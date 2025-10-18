from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Dict, Optional
import yaml
import os
import time
import psutil

app = FastAPI(title="Watchtower Edge API", version="0.1.0")

class Settings(BaseSettings):
    ENV: str = "dev"
    SERVICE_PORT: int = 8002
    CONFIG_PATH: str = "config.yml"

    class Config:
        env_file = ".env"

settings = Settings()

# Load YAML config (optional)
config: Dict = {}
if os.path.exists(settings.CONFIG_PATH):
    with open(settings.CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f) or {}

start_time = time.time()

class CameraIn(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    url: str
    type: Optional[str] = "rtsp"  # rtsp | usb | file

# naive in-memory registry
cameras: Dict[str, Dict] = {}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_s": round(time.time() - start_time, 2),
        "env": settings.ENV,
    }

@app.get("/metrics")
def metrics():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss
    cpu = psutil.cpu_percent(interval=0.0)
    return {
        "cpu_percent": cpu,
        "rss_bytes": mem,
        "camera_count": len(cameras),
    }

@app.get("/version")
def version():
    return {
        "version": app.version,
        "config_keys": list(config.keys()),
    }

@app.post("/cameras")
def register_camera(cam: CameraIn):
    cam_id = cam.id or f"cam_{len(cameras)+1}"
    cameras[cam_id] = {
        "name": cam.name or cam_id,
        "url": cam.url,
        "type": cam.type,
        "status": "registered",
    }
    return {
        "id": cam_id,
        "message": "registered",
    }

@app.get("/cameras")
def list_cameras():
    return cameras

@app.delete("/cameras/{cam_id}")
def delete_camera(cam_id: str):
    if cam_id not in cameras:
        raise HTTPException(status_code=404, detail="camera not found")
    del cameras[cam_id]
    return {
        "id": cam_id,
        "message": "deleted",
    }

# placeholder for background ingest workers and detector hooks
# TODO: wire OpenCV/GStreamer and YOLO wrapper
