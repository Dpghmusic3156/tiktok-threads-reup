# TikTok Threads Reup Automation Pipeline 

Bộ công cụ tự động hóa chuyên nghiệp dành cho việc **"xào nấu" & Reup video TikTok dạng Threads đọc bình luận** (kèm đoạn video review/test sản phẩm ở Outro).

Được thiết kế để giải quyết dứt điểm các lỗi kinh điển khi reup video: **Lệch tiếng / trôi giọng theo thời gian**, **lặp card thoại**, **tua nhanh video nền giật lag**, và **bị thuật toán TikTok quét bản quyền trùng lặp**.

---

##  Tính năng vượt trội

1. **Kiến trúc Frame-Count Locked (Khớp tiếng 100% tuyệt đối)**:
   - Thay vì dùng các phép tính thời gian float dễ bị sai số làm tròn khi render `ffmpeg`, hệ thống **khóa cứng số lượng frame chính xác** cho từng phân cảnh dựa trên tốc độ khung hình (60 FPS).
   - Âm thanh thoại gốc được giữ nguyên vẹn liên tục (Continuous Master Audio) — **không cắt vụn, không lệch PTS**.

2. **Bộ lọc Né quét Bản quyền AI của TikTok**:
   - **Âm thanh**: Tự động lọc cắt tần số siêu âm/hạ âm watermark ngầm (`highpass=80Hz`, `lowpass=15000Hz`), tăng cường dải hiện diện giọng nói (`EQ Boost 1.8kHz +2.5dB`), và lồng nhạc nền hot trend ở mức 12% âm lượng.
   - **Hình ảnh**: Thay thế toàn bộ nền parkour/gameplay cũ bằng video nền mới ở tốc độ 100% chuẩn; đoạn Outro giới thiệu sản phẩm được crop 5%, tinh chỉnh màu sắc (Saturation +6%, Contrast +5%) và tạo khung viền mờ nghệ thuật.

3. **Card Threads Chuẩn Giao diện Full HD 1080×1920 & Hỗ trợ Comment Xếp Chồng (Nested Stacking)**:
   - Tự động bo góc mềm mại (Radius 24px), tạo bóng đổ chiều sâu đa lớp (Soft Drop-Shadow).
   - Tự động thêm số trang tiến trình trực quan (`01 / 05`, `02 / 05`...).
   - **Hỗ trợ comment xếp chồng liên hoàn (`render_stacked_card_overlays`)**: Giải quyết triệt để dạng video Threads có bình luận trả lời liên tiếp (Comment 1 -> Comment 2 -> Comment 3) với khoảng trống giữa các card trong suốt 100%, neo vị trí cố định chống rung giật và không lem nền cũ.

4. **Tải Video Đa Kênh Thông Minh (Dual-Engine Downloader)**:
   - Tự động tải qua `yt-dlp` tốc độ cao.
   - Tự động kích hoạt cơ chế dự phòng **SSSTik API** khi gặp bot-challenge hoặc link rút gọn (`vt.tiktok.com`) mà không cần nạp cookie trình duyệt.

5. **Kích hoạt cờ FastStart**:
   - Tự động chèn atom `moov` lên đầu file video (`-movflags +faststart`), giúp video tải tức thì khi xem và tua mượt mà không bị delay trên app TikTok.

---

## 📂 Cấu trúc Repository

```text
tiktok-threads-reup/
├── README.md                      # Hướng dẫn chi tiết sử dụng
├── requirements.txt               # Thư viện phụ thuộc Python
├── config.py                      # File cấu hình thông số kỹ thuật mặc định
├── reup_pipeline.py               # Master CLI script điều phối toàn bộ
├── run_example.py                 # Script chạy mẫu 1 lệnh ra ngay video
├── modules/
│   ├── __init__.py
│   ├── downloader.py              # Tải video TikTok tự động qua link
│   ├── scene_detector.py          # Dò tìm tự động các điểm chuyển cảnh
│   ├── card_renderer.py           # Render card Threads 1080x1920 sắc nét
│   ├── audio_processor.py         # Rửa âm thanh và lồng BGM né quét
│   └── video_composer.py          # Động cơ ghép Frame-Count Locked
├── assets/
│   ├── fonts/                     # Font chữ Roboto tiếng Việt
│   └── samples/                   # File mẫu đi kèm (Background, BGM, Video gốc, Cards)
├── tests/
│   └── test_pipeline.py           # Bộ kiểm thử tự động (Unit Test Suite)
└── output/                        # Thư mục chứa video thành phẩm
```

---

## 🚀 Cài đặt & Bắt đầu Nhanh

### 1. Cài đặt môi trường
Yêu cầu Python 3.9+ và FFmpeg. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 2. Chạy thử nghiệm video mẫu có sẵn
Chỉ cần chạy lệnh sau để kiểm tra toàn bộ pipeline:
```bash
python run_example.py
```
Video thành phẩm sẽ xuất hiện tại `output/example_reup_result.mp4`.

### 3. Kiểm tra tự động (Run Test Suite)
```bash
python -m unittest tests/test_pipeline.py
```

---

## 🛠️ Hướng dẫn Sử dụng CLI

### Cú pháp tổng quát:
```bash
python reup_pipeline.py --source <url_hoặc_file_gốc> --bg <video_nền> --bgm <nhạc_nền> --output <đường_dẫn_ra>
```

### Ví dụ cụ thể:
```bash
python reup_pipeline.py ^
    --source "https://www.tiktok.com/@example/video/123456789" ^
    --bg assets/samples/sample_bg.mp4 ^
    --bgm assets/samples/sample_bgm.mp3 ^
    --output output/my_tiktok_reup.mp4
```

---

## 📐 Nguyên lý Frame-Count Locked (Tại sao không bao giờ lệch tiếng?)

Trong video chuẩn 60 FPS:
- $1 \text{ giây} = 60 \text{ frames}$
- Phân đoạn $D$ giây sẽ có chính xác $N = \text{round}(D \times 60)$ frames.

Bảng phân bổ khung hình trong video mẫu 55.033 giây:
| Phân cảnh | Nội dung | Số frame (60 FPS) | Thời gian tương ứng |
|:---|:---|:---:|:---:|
| **Thẻ 1** | Post gốc dẫn dắt | 508 frames | 0.000s ➔ 8.467s |
| **Meme 1** | Mèo Tom suy nghĩ | 40 frames | 8.467s ➔ 9.133s |
| **Thẻ 2** | Comment thích màu mè | 354 frames | 9.133s ➔ 15.033s |
| **Thẻ 3** | Comment kèm ảnh ốp | 182 frames | 15.033s ➔ 18.067s |
| **Thẻ 4** | Comment nhanh chán | 526 frames | 18.067s ➔ 26.833s |
| **Thẻ 5** | Comment mua để ra vẻ | 428 frames | 26.833s ➔ 33.967s |
| **Meme 2** | Người que tát Stickman | 36 frames | 33.967s ➔ 34.567s |
| **Thẻ 6** | Comment chốt mua ốp | 306 frames | 34.567s ➔ 39.667s |
| **Outro** | Video review test ốp | 922 frames | 39.667s ➔ 55.033s |
| **TỔNG CỘNG** | **Toàn bộ video** | **3302 frames** | **55.033 giây** |

Vì tổng số frame video $(3302 / 60 \approx 55.033\text{s})$ khớp chuẩn xác với thời lượng dòng thoại âm thanh, **không một mili-giây nào có thể bị xê dịch hay trôi lệch**.

---

## 🛡️ Tùy chỉnh Bộ lọc Né Quét TikTok trong `config.py`

Bạn có thể chỉnh sửa các tham số trong file `config.py`:
- `AUDIO_BGM_VOLUME = 0.12`: Âm lượng nhạc nền (12%).
- `AUDIO_EQ_GAIN = 2.5`: Tăng âm sắc dải trung cao cho giọng đọc ấm và rõ.
- `DEMO_CROP_RATIO = 0.05`: Tỷ lệ cắt viền video review (5%).
- `DEMO_SATURATION_BOOST = 1.06`: Độ rực màu video review (+6%).
- `DEMO_CONTRAST_BOOST = 1.05`: Độ tương phản (+5%).

---
*Chúc bạn tạo ra những video triệu view an toàn và hiệu quả!*
