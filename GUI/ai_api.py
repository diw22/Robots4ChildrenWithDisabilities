#!/usr/bin/env python3
import sys
import logging
import json
import requests
from requests.exceptions import ReadTimeout, RequestException
from pathlib import Path
import cv2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Base URL (ajustez si besoin)
API_BASE = "http://192.0.0.2:80"

# Model selection mapping
MODEL_MAPPING = {
#    "A1": "phospho-app/gc1724-ACT-ttt-a1-square-xxxxx",
    "A2": "phospho-app/gc1724-ACT-ttt-a2-square-rwa45",
    "A3": "phospho-app/gc1724-ACT-ttt-a3-square-dj55j",
    "B1": "phospho-app/gc1724-ACT-ttt-b1-square-c5vk8",
    "B2": "phospho-app/gc1724-ACT-ttt-b2-square-ausu9",
    "B3": "phospho-app/gc1724-ACT-ttt-b3-square-qlhk3",
#    "C1": "phospho-app/gc1724-ACT-ttt-c1-square-xxxxx",
#    "C2": "phospho-app/gc1724-ACT-ttt-c2-square-nu1bs",
    "C3": "phospho-app/gc1724-ACT-ttt-c3-square-dhwtl",
}

SPAWN_TIMEOUT = 300
START_TIMEOUT = 30


def check_cameras() -> bool:
    """
    Vérifie via /frames qu'au moins un flux est actif.
    """
    try:
        resp = requests.get(f"{API_BASE}/frames", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        active = [cam_id for cam_id, frame in data.items() if frame is not None]
        if not active:
            logger.error("No camera streams detected by /frames endpoint.")
            return False
        logger.info("Detected camera streams via /frames: %s", active)
        return True
    except RequestException as exc:
        logger.error("Camera check failed: %s", exc)
        return False


def spawn_model(model_id: str) -> bool:
    logger.info("Requesting model spawn: %s", model_id)
    try:
        resp = requests.post(
            f"{API_BASE}/ai-control/spawn",
            json={"model_id": model_id, "model_type": "ACT", "robot_serials_to_ignore": []},
            timeout=SPAWN_TIMEOUT,
        )
        resp.raise_for_status()
        logger.info("Spawn response: %s", resp.json())
        return True
    except ReadTimeout:
        logger.warning("Spawn timeout (model still loading).")
        return True
    except RequestException as exc:
        logger.error("Spawn failed: %s", exc)
        return False


def get_model_video_keys(model_id: str, model_type: str):
    """
    Appelle /model/video-keys pour récupérer la liste des clés vidéo du modèle.
    """
    payload = {"model_id": model_id, "model_type": model_type}
    resp = requests.post(f"{API_BASE}/model/video-keys", json=payload, timeout=5)
    resp.raise_for_status()
    keys = resp.json().get("video_keys", [])
    logger.info("Model vidéo keys: %s", keys)
    return keys


def detect_cameras(max_idx: int = 4):
    """
    Tente d'ouvrir les indices 0..max_idx-1 via OpenCV pour lister
    les flux existants: ['camera_0', ...].
    """
    cams = []
    for i in range(max_idx):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cams.append(f"camera_{i}")
            cap.release()
    logger.info("Streams détectés (OpenCV): %s", cams)
    return cams


def start_control(model_id: str, prompt: str) -> bool:
    if not check_cameras():
        logger.error("Start aborted: No camera streams detected.")
        return False

    video_keys = get_model_video_keys(model_id, "ACT")
    streams = detect_cameras()
    mapping = {key: idx for idx, key in enumerate(video_keys)}
    logger.info("Cameras mapping → %s", mapping)

    payload = {
        "prompt": prompt,
        "model_id": model_id,
        "model_type": "ACT",
        "speed": 1,
        "robot_serials_to_ignore": [],
        "cameras_keys_mapping": mapping,
        "selected_camera_id": 0,
    }
    logger.info("→ POST %s/ai-control/start\n%s", API_BASE, json.dumps(payload, indent=2))

    try:
        resp = requests.post(
            f"{API_BASE}/ai-control/start", json=payload, timeout=START_TIMEOUT
        )
        data = resp.json()
        if resp.status_code == 200 and data.get("status") == "ok":
            logger.info("AI control started with prompt %r.", prompt)
            return True
        logger.error("Start error: %s", data)
        return False
    except RequestException as exc:
        logger.error("Start failed: %s", exc)
        return False


def pause_control():
    """
    Met en pause le contrôle AI en cours.
    """
    try:
        resp = requests.post(f"{API_BASE}/ai-control/pause", timeout=5)
        logger.info("Paused: %s", resp.json())
    except RequestException as exc:
        logger.error("Pause failed: %s", exc)


def resume_control():
    """
    Reprend le contrôle AI en pause.
    """
    try:
        resp = requests.post(f"{API_BASE}/ai-control/resume", timeout=5)
        logger.info("Resumed: %s", resp.json())
    except RequestException as exc:
        logger.error("Resume failed: %s", exc)


def stop_control():
    """
    Arrête le contrôle AI en cours.
    """
    try:
        resp = requests.post(f"{API_BASE}/ai-control/stop", timeout=5)
        logger.info("Stopped: %s", resp.json())
    except RequestException as exc:
        logger.error("Stop failed: %s", exc)


def main():
    current_running = False
    current_paused = False
    current_model = None

    while True:
        choice = input("Enter model key (A1…C3), 'P' to pause, 'R' to resume, or 'Q' to quit: ").strip().upper()
        if choice == 'Q':
            if current_running or current_paused:
                logger.info("Stopping current AI control before exit.")
                stop_control()
            logger.info("Exiting CLI.")
            break
        elif choice == 'P':
            if current_running:
                pause_control()
                current_running = False
                current_paused = True
            else:
                logger.warning("No running model to pause.")
            continue
        elif choice == 'R':
            if current_paused:
                resume_control()
                current_paused = False
                current_running = True
            else:
                logger.warning("No paused model to resume.")
            continue

        model_id = MODEL_MAPPING.get(choice)
        if not model_id:
            message = f"Model {choice} does not exist. Available keys: {', '.join(MODEL_MAPPING.keys())}"
            logger.error(message)
            print(message)
            continue
        logger.info("Selected model ID: %s", model_id)

        if current_running or current_paused:
            logger.info("Stopping previous model: %s", current_model)
            stop_control()
            current_running = False
            current_paused = False

        if not spawn_model(model_id):
            continue

        # Toujours utiliser la lettre 'f' comme prompt
        prompt = 'f'
        if start_control(model_id, prompt):
            current_running = True
            current_model = model_id
        else:
            current_running = False

if __name__ == "__main__":
    main()
