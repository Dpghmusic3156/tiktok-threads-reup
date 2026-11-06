"""Configuration constants and default parameters for TikTok Threads Reup Pipeline."""
from __future__ import annotations

from pathlib import Path
import imageio_ffmpeg

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
SAMPLES_DIR = ASSETS_DIR / "samples"
OUTPUT_DIR = BASE_DIR / "output"

# FFmpeg binary
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# Default Video Specifications (TikTok Vertical Standard)
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FPS = 60

# Card Layout & Styling
CARD_BORDER_RADIUS = 24
CARD_SHADOW_RADIUS = 24
CARD_SHADOW_ALPHA = 140
CARD_SHADOW_OFFSET_Y = 12
CARD_VERTICAL_CENTER_RATIO = 0.42
CARD_WIDTH_RATIOS = {
    "default": 0.92,
    "image_case": 0.82
}
DEFAULT_FONT_PATH = FONTS_DIR / "Roboto-regular.ttf"

# Anti-Detection Audio Parameters
AUDIO_SAMPLE_RATE = 48000
AUDIO_BITRATE = "192k"
AUDIO_HIGHPASS_FREQ = 80       # Remove sub-bass watermarks
AUDIO_LOWPASS_FREQ = 15000     # Remove ultrasound tags
AUDIO_EQ_FREQ = 1800           # Speech presence boost
AUDIO_EQ_GAIN = 2.5            # dB
AUDIO_BGM_VOLUME = 0.12        # 12% background trend music volume

# Anti-Detection Video Parameters (For Outro / Demo Clip)
DEMO_CROP_RATIO = 0.05         # 5% crop to alter aspect & spatial hash
DEMO_SATURATION_BOOST = 1.06   # +6% saturation
DEMO_CONTRAST_BOOST = 1.05     # +5% contrast
DEMO_BACKDROP_BLUR_KERNEL = (51, 51)
DEMO_BACKDROP_DARKEN = 0.75
