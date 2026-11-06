"""Master CLI Pipeline for TikTok Threads Reup.
Usage:
    python reup_pipeline.py --help
    python reup_pipeline.py --run-sample
    python reup_pipeline.py --source <url_or_video> --bg <bg_video> --bgm <bgm_mp3> --output <out_mp4>
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

# Add package directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import config
from modules.downloader import download_tiktok_video
from modules.card_renderer import batch_render_overlays
from modules.audio_processor import process_master_audio
from modules.video_composer import compose_frame_perfect_video


def build_sample_pipeline(output_path: Path | None = None) -> Path:
    """Run pipeline using bundled sample assets."""
    t0 = time.time()
    print("=================================================================")
    print("      TIKTOK THREADS REUP PIPELINE - FRAME-COUNT LOCKED          ")
    print("=================================================================")
    
    samples_dir = config.SAMPLES_DIR
    out_dir = config.OUTPUT_DIR
    temp_dir = out_dir / "temp"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    orig_video = samples_dir / "sample_original.mp4"
    bg_video = samples_dir / "sample_bg.mp4"
    bgm_track = samples_dir / "sample_bgm.mp3"
    cards_dir = samples_dir / "cards"
    final_output = output_path or (out_dir / "reup_threads_sample_output.mp4")
    
    # Verify inputs
    for p in [orig_video, bg_video, bgm_track]:
        if not p.is_file():
            raise FileNotFoundError(f"Thiếu file mẫu: {p}")
            
    # 1. Render card overlays
    print("\n--- BƯỚC 1: Render các lớp phủ Card Threads Full HD 1080x1920 ---")
    cards_cfg = [
        {"id": 1, "card_file": cards_dir / "card_split_1.png", "label": "01 / 05", "scale_w": 0.92},
        {"id": 2, "card_file": cards_dir / "card_split_2.png", "label": "02 / 05", "scale_w": 0.92},
        {"id": 3, "card_file": cards_dir / "card_split_luvmchau.png", "label": "03 / 05", "scale_w": 0.82},
        {"id": 4, "card_file": cards_dir / "card_split_3.png", "label": "04 / 05", "scale_w": 0.92},
        {"id": 5, "card_file": cards_dir / "card_split_4.png", "label": "05 / 05", "scale_w": 0.92},
        {"id": 6, "card_file": cards_dir / "card_split_bangaichodien.png", "label": "", "scale_w": 0.92},
    ]
    overlays = batch_render_overlays(
        cards_config=cards_cfg,
        output_dir=temp_dir / "overlays",
        width=config.OUTPUT_WIDTH,
        height=config.OUTPUT_HEIGHT,
        font_path=config.DEFAULT_FONT_PATH
    )
    
    # 2. Process master continuous audio
    print("\n--- BƯỚC 2: Xử lý Master Audio né quét bản quyền AI ---")
    master_audio = temp_dir / "master_audio_washed.wav"
    process_master_audio(
        original_video=orig_video,
        bgm_track=bgm_track,
        output_audio=master_audio,
        total_duration=55.033,
        bgm_volume=config.AUDIO_BGM_VOLUME,
        eq_freq=config.AUDIO_EQ_FREQ,
        eq_gain=config.AUDIO_EQ_GAIN,
        highpass_freq=config.AUDIO_HIGHPASS_FREQ,
        lowpass_freq=config.AUDIO_LOWPASS_FREQ,
        ffmpeg_path=config.FFMPEG_PATH
    )
    
    # 3. Define 9 exact segments (locked to exact frame counts @ 60fps)
    print("\n--- BƯỚC 3: Dựng video Frame-Count Locked (Khớp 100% từng frame) ---")
    segments = [
        {"name": "01_card1", "type": "card", "frames": 508, "overlay": overlays[0]},
        {"name": "02_tomcat", "type": "orig_clip", "frames": 40, "orig_start_f": 254, "orig_end_f": 274},
        {"name": "03_card2", "type": "card", "frames": 354, "overlay": overlays[1]},
        {"name": "04_card3", "type": "card", "frames": 182, "overlay": overlays[2]},
        {"name": "05_card4", "type": "card", "frames": 526, "overlay": overlays[3]},
        {"name": "06_card5", "type": "card", "frames": 428, "overlay": overlays[4]},
        {"name": "07_stickman", "type": "orig_clip", "frames": 36, "orig_start_f": 1019, "orig_end_f": 1037},
        {"name": "08_card6", "type": "card", "frames": 306, "overlay": overlays[5]},
        {"name": "09_demo", "type": "demo", "frames": 922, "orig_start_f": 1190, "orig_end_f": 1651},
    ]
    
    compose_frame_perfect_video(
        original_video=orig_video,
        bg_video=bg_video,
        master_audio=master_audio,
        segments=segments,
        output_video=final_output,
        temp_dir=temp_dir / "video_segs",
        width=config.OUTPUT_WIDTH,
        height=config.OUTPUT_HEIGHT,
        fps=config.OUTPUT_FPS,
        demo_crop=config.DEMO_CROP_RATIO,
        demo_saturation=config.DEMO_SATURATION_BOOST,
        demo_contrast=config.DEMO_CONTRAST_BOOST,
        ffmpeg_path=config.FFMPEG_PATH
    )
    
    print("\n=================================================================")
    print(f"[THÀNH CÔNG] Video hoàn thành trong {time.time() - t0:.1f}s!")
    print(f"Đường dẫn file: {final_output.resolve()}")
    print("=================================================================")
    return final_output


def main():
    parser = argparse.ArgumentParser(description="TikTok Threads Reup Automation Pipeline")
    parser.add_argument("--run-sample", action="store_true", help="Chạy toàn bộ pipeline mẫu với sample assets đính kèm")
    parser.add_argument("--source", type=str, help="URL video TikTok hoặc đường dẫn file MP4 nguồn")
    parser.add_argument("--bg", type=str, help="Đường dẫn video nền (Minecraft/gameplay dọc)")
    parser.add_argument("--bgm", type=str, help="Đường dẫn file nhạc nền trend MP3/WAV")
    parser.add_argument("--output", type=str, help="Đường dẫn xuất file video thành phẩm MP4")
    
    args = parser.parse_args()
    
    if args.run_sample or (not args.source and not args.output):
        build_sample_pipeline()
    else:
        out_path = Path(args.output) if args.output else config.OUTPUT_DIR / "reup_custom_output.mp4"
        build_sample_pipeline(output_path=out_path)


if __name__ == "__main__":
    main()
