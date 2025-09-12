# Model Weights & Datasets
- Use a YOLO-family checkpoint for **visible firearm** class(es).
- Store weights at `edge/sidecar/weights/` (git-ignored).
- Do not commit datasets. Track sources & licenses in this file.
- Evaluate on curated clips; log FP/FN and conf thresholds.
