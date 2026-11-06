"""TikTok / Video Downloader Module."""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import urllib.request


def _download_via_ssstik_fallback(url: str, output_file: Path) -> Path:
    """Fallback downloader for TikTok videos via SSSTik API when yt-dlp is blocked."""
    print(f"[*] Thử tải dự phòng qua SSSTik API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Origin": "https://ssstik.io",
        "Referer": "https://ssstik.io/en",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "HX-Request": "true",
        "HX-Trigger": "_gcaptcha_pt",
        "HX-Target": "target",
        "HX-Current-URL": "https://ssstik.io/en"
    }
    
    req_home = urllib.request.Request("https://ssstik.io/en", headers={"User-Agent": headers["User-Agent"]})
    with urllib.request.urlopen(req_home, timeout=10) as r0:
        home_html = r0.read().decode("utf-8")
        m = re.search(r"tt:\s*'([a-f0-9]+)'", home_html)
        tt_val = m.group(1) if m else "a243d6b0da67280f55cfbf7cb2db3db7"
        
    post_data = urllib.parse.urlencode({
        "id": url,
        "locale": "en",
        "tt": tt_val
    }).encode("utf-8")
    
    req_post = urllib.request.Request("https://ssstik.io/abc?url=dl", data=post_data, headers=headers)
    with urllib.request.urlopen(req_post, timeout=12) as r1:
        res_html = r1.read().decode("utf-8", errors="ignore")
        
    links = re.findall(r'href="([^"]+)"', res_html)
    dls = [l for l in links if "tikcdn" in l or "ssstik" in l or "download" in l]
    if not dls:
        raise RuntimeError("Không tìm thấy link download trong phản hồi SSSTik.")
        
    dl_url = dls[0]
    dl_req = urllib.request.Request(dl_url, headers={
        "User-Agent": headers["User-Agent"],
        "Referer": "https://ssstik.io/"
    })
    with urllib.request.urlopen(dl_req, timeout=30) as r2:
        content = r2.read()
        with open(output_file, "wb") as f:
            f.write(content)
            
    print(f"[OK] Đã tải về dự phòng thành công: {output_file.name} ({len(content):,} bytes)")
    return output_file.resolve()


def download_tiktok_video(url_or_path: str | Path, output_dir: Path) -> Path:
    """Download a video from TikTok URL using yt-dlp (with fallback to SSSTik), or resolve existing file path."""
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
        print(f"[!] yt-dlp gặp sự cố ({e}), đang kích hoạt fallback...")
        fallback_file = output_dir / "downloaded_source.mp4"
        try:
            return _download_via_ssstik_fallback(source_str, fallback_file)
        except Exception as fb_err:
            raise RuntimeError(f"Tải video thất bại từ {source_str}. yt-dlp: {e}, fallback: {fb_err}")
        
    # Find generated file
    candidates = list(output_dir.glob("downloaded_source.*"))
    if not candidates:
        raise FileNotFoundError("Không tìm thấy file sau khi tải về.")
        
    final_file = candidates[0]
    print(f"[OK] Đã tải về thành công: {final_file.name} ({final_file.stat().st_size:,} bytes)")
    return final_file.resolve()
