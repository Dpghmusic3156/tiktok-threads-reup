"""One-click example script to test and verify the TikTok Threads Reup Pipeline."""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from reup_pipeline import build_sample_pipeline

if __name__ == "__main__":
    out_file = BASE_DIR / "output" / "example_reup_result.mp4"
    build_sample_pipeline(output_path=out_file)
