"""Audio Processing & Anti-Detection Washing Module."""
from __future__ import annotations

from pathlib import Path
import subprocess
import imageio_ffmpeg


def process_master_audio(
    original_video: Path,
    bgm_track: Path | None,
    output_audio: Path,
    total_duration: float,
    bgm_volume: float = 0.12,
    eq_freq: int = 1800,
    eq_gain: float = 2.5,
    highpass_freq: int = 80,
    lowpass_freq: int = 15000,
    ffmpeg_path: str | None = None
) -> Path:
    """Process master continuous audio with anti-detection EQ and subtle BGM mixing.
    
    Guarantees:
    - 100% continuous timeline (zero slicing, zero PTS drift)
    - Anti-detection filtering to alter MD5 and acoustic fingerprint
    - Vocal enhancement for crisp, punchy voice delivery
    """
    ffmpeg_exe = ffmpeg_path or imageio_ffmpeg.get_ffmpeg_exe()
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        ffmpeg_exe, "-hide_banner", "-loglevel", "error", "-y", "-nostdin",
        "-i", str(original_video)
    ]
    
    if bgm_track and bgm_track.is_file():
        cmd += ["-stream_loop", "-1", "-i", str(bgm_track)]
        filters = [
            f"[0:a]highpass=f={highpass_freq},lowpass=f={lowpass_freq},equalizer=f={eq_freq}:width_type=q:width=1.5:g={eq_gain},volume=1.0[voice]",
            f"[1:a]volume={bgm_volume}[bgm]",
            f"[voice][bgm]amix=inputs=2:duration=longest:dropout_transition=2,aformat=sample_rates=48000:channel_layouts=stereo[a_out]"
        ]
        cmd += ["-filter_complex", ";".join(filters), "-map", "[a_out]"]
    else:
        filters = [
            f"[0:a]highpass=f={highpass_freq},lowpass=f={lowpass_freq},equalizer=f={eq_freq}:width_type=q:width=1.5:g={eq_gain},aformat=sample_rates=48000:channel_layouts=stereo[a_out]"
        ]
        cmd += ["-filter_complex", ";".join(filters), "-map", "[a_out]"]
        
    cmd += ["-t", f"{total_duration:.4f}", str(output_audio)]
    
    print(f"[*] Đang xử lý Master Audio ({total_duration:.3f}s)...")
    subprocess.run(cmd, check=True)
    print(f"[OK] Master Audio đã tạo: {output_audio.name} ({output_audio.stat().st_size:,} bytes)")
    return output_audio
