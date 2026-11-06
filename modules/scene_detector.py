"""Scene Cut & Transition Detection Module."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np


@dataclass
class SceneSegment:
    index: int
    name: str
    seg_type: str        # 'card', 'orig_clip', 'demo'
    start_sec: float
    end_sec: float
    duration: float
    orig_start_frame: int
    orig_end_frame: int
    target_frames: int   # Number of frames at target FPS (e.g. 60fps)


def detect_scene_cuts(
    video_path: Path,
    target_fps: int = 60,
    diff_threshold: float = 35.0
) -> list[dict]:
    """Scan video frame-by-frame to identify major transition points (scene jumps)."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Không thể mở video: {video_path}")
        
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    prev_gray = None
    transitions = [0]
    
    for f in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
            
        h, w, _ = frame.shape
        # Center region where cards appear
        crop = frame[int(h * 0.25):int(h * 0.70), int(w * 0.15):int(w * 0.85)]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        if prev_gray is not None:
            diff = float(np.mean(cv2.absdiff(gray, prev_gray)))
            if diff > diff_threshold:
                # Avoid registering two jumps within 10 frames
                if f - transitions[-1] > int(src_fps * 0.4):
                    transitions.append(f)
                    
        prev_gray = gray
        
    cap.release()
    transitions.append(total_frames)
    
    results = []
    for i in range(len(transitions) - 1):
        s_f = transitions[i]
        e_f = transitions[i + 1]
        s_t = s_f / src_fps
        e_t = e_f / src_fps
        dur = e_t - s_t
        t_frames = round(dur * target_fps)
        results.append({
            "segment_idx": i + 1,
            "start_frame": s_f,
            "end_frame": e_f,
            "start_sec": s_t,
            "end_sec": e_t,
            "duration": dur,
            "target_frames": t_frames
        })
        
    return results
