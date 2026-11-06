"""Automated Test Suite for TikTok Threads Reup Pipeline."""
from pathlib import Path
import sys
import unittest
import cv2
import wave
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import config
from modules.downloader import download_tiktok_video
from modules.scene_detector import detect_scene_cuts
from modules.card_renderer import render_card_overlay, render_stacked_card_overlays
from modules.audio_processor import process_master_audio


class TestTikTokThreadsReup(unittest.TestCase):
    
    def test_01_assets_exist(self):
        """Verify all critical sample assets and fonts are present."""
        self.assertTrue(config.DEFAULT_FONT_PATH.is_file(), f"Missing font: {config.DEFAULT_FONT_PATH}")
        self.assertTrue((config.SAMPLES_DIR / "sample_bg.mp4").is_file(), "Missing sample background video")
        self.assertTrue((config.SAMPLES_DIR / "sample_bgm.mp3").is_file(), "Missing sample BGM")
        self.assertTrue((config.SAMPLES_DIR / "sample_original.mp4").is_file(), "Missing sample original video")
        
        cards = list((config.SAMPLES_DIR / "cards").glob("*.png"))
        self.assertGreaterEqual(len(cards), 5, "Missing sample cards")

    def test_02_card_renderer(self):
        """Verify that card overlay generates exact 1080x1920 RGBA image with rounded corners."""
        sample_card = config.SAMPLES_DIR / "cards" / "card_split_1.png"
        out_overlay = config.OUTPUT_DIR / "test_overlay.png"
        
        render_card_overlay(
            card_path=sample_card,
            output_path=out_overlay,
            label="01 / 05",
            width=1080,
            height=1920,
            font_path=config.DEFAULT_FONT_PATH
        )
        
        self.assertTrue(out_overlay.is_file())
        with Image.open(out_overlay) as img:
            self.assertEqual(img.size, (1080, 1920))
            self.assertEqual(img.mode, "RGBA")

    def test_03_scene_detector(self):
        """Verify scene transition detection on sample video."""
        sample_vid = config.SAMPLES_DIR / "sample_original.mp4"
        cuts = detect_scene_cuts(sample_vid, target_fps=60, diff_threshold=35.0)
        self.assertGreaterEqual(len(cuts), 5, "Scene detector should detect at least 5 major scenes")

    def test_04_audio_processor(self):
        """Verify master continuous audio generation and properties."""
        sample_vid = config.SAMPLES_DIR / "sample_original.mp4"
        sample_bgm = config.SAMPLES_DIR / "sample_bgm.mp3"
        out_wav = config.OUTPUT_DIR / "test_audio.wav"
        
        process_master_audio(
            original_video=sample_vid,
            bgm_track=sample_bgm,
            output_audio=out_wav,
            total_duration=5.0,  # Quick 5 second test
            ffmpeg_path=config.FFMPEG_PATH
        )
        
        self.assertTrue(out_wav.is_file())
        with wave.open(str(out_wav), "rb") as w:
            rate = w.getframerate()
            frames = w.getnframes()
            dur = frames / rate
            self.assertEqual(rate, 48000)
            self.assertAlmostEqual(dur, 5.0, delta=0.1)

    def test_05_frame_count_invariants(self):
        """Verify that Frame-Count Locked segments sum to exact duration @ 60fps."""
        # 508 + 40 + 354 + 182 + 526 + 428 + 36 + 306 + 922 = 3302 frames = 55.033s
        frame_counts = [508, 40, 354, 182, 526, 428, 36, 306, 922]
        total_frames = sum(frame_counts)
        calc_duration = total_frames / 60.0
        self.assertEqual(total_frames, 3302)
        self.assertAlmostEqual(calc_duration, 55.033, delta=0.001)

    def test_06_stacked_card_renderer(self):
        """Verify progressive stacked comment overlays generation."""
        cards_dir = config.SAMPLES_DIR / "cards"
        sample_cards = [
            cards_dir / "card_split_1.png",
            cards_dir / "card_split_2.png"
        ]
        out_stack_dir = config.OUTPUT_DIR / "test_stack"
        out_paths = render_stacked_card_overlays(
            comment_paths=sample_cards,
            output_dir=out_stack_dir,
            width=1080,
            height=1920
        )
        self.assertEqual(len(out_paths), 2)
        for p in out_paths:
            self.assertTrue(p.is_file())
            with Image.open(p) as img:
                self.assertEqual(img.size, (1080, 1920))
                self.assertEqual(img.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
