"""TikTok / Video Downloader Module."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def download_tiktok_video(url_or_path: str | Path, output_dir: Path) -> Path:
    """Download a video from TikTok URL using yt-dlp, or resolve existing file path."""
    source_str = str(url_or_path).strip()
    
    # Check if input is an existing local file
    local_path = Path(source_str)
    if local_path.is_file():
        return local_path.resolve()
        
    output_dir.mkdir(parents=True, exist_ok=True)
    out_template = output_dir / "downloaded_source.%(ext)s"
    
    print(f"[*] Đang tải video từ URL: {source_str}...")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", str(out_template),
        source_str
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Tải video thất bại từ {source_str}: {e}")
        
    # Find generated file
    candidates = list(output_dir.glob("downloaded_source.*"))
    if not candidates:
        raise FileNotFoundError("Không tìm thấy file sau khi tải về.")
        
    final_file = candidates[0]
    print(f"[OK] Đã tải về thành công: {final_file.name} ({final_file.stat().st_size:,} bytes)")
    return final_file.resolve()
