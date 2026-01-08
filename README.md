# Edge Search Automation Tool

Tool tự động hóa tìm kiếm trên Microsoft Edge để tích điểm trong chương trình Microsoft Rewards.

## ⚠️ Lưu ý quan trọng

- Tool này chỉ dành cho mục đích học tập và nghiên cứu
- Việc sử dụng automation có thể vi phạm điều khoản dịch vụ của Microsoft Rewards
- Sử dụng có trách nhiệm và tuân thủ các quy định của Microsoft
- Tác giả không chịu trách nhiệm về việc sử dụng tool này

## 📋 Yêu cầu hệ thống

- Python 3.7 trở lên
- Microsoft Edge browser đã cài đặt
- Windows 10/11 (khuyến nghị)

## 🚀 Cài đặt

### 1. Clone hoặc tải project về máy

### 2. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Hoặc cài đặt từng thư viện:

```bash
pip install selenium webdriver-manager python-dotenv pytrends requests beautifulsoup4
``` web

### 3. Kiểm tra Edge browser

Đảm bảo Microsoft Edge đã được cài đặt và cập nhật lên phiên bản mới nhất.

### 4. Kiểm tra cài đặt (Tùy chọn nhưng khuyến nghị)

Chạy script kiểm tra để đảm bảo mọi thứ đã sẵn sàng:

```bash
python check_edgedriver.py
```

Script này sẽ kiểm tra và báo cáo tình trạng:
- Microsoft Edge đã cài đặt
- EdgeDriver đã có và tương thích
- Kết nối internet
- Selenium hoạt động

## 📖 Cách sử dụng

### Chạy với cấu hình mặc định

```bash
python edge_search_automation.py
```

### Tùy chỉnh cấu hình

Mở file `edge_search_automation.py` và chỉnh sửa các tham số trong hàm `main()`:

```python
NUM_SEARCHES = 20      # Số lần tìm kiếm
HEADLESS = False       # True = chạy ẩn, False = hiển thị browser
DELAY_RANGE = (3, 6)   # Khoảng delay giữa các lần search (giây)
KEYWORDS_FILE = 'keywords.json'  # File chứa từ khóa

# Cấu hình Trending (TÍNH NĂNG MỚI!)
USE_TRENDING = True    # True để sử dụng trending keywords
TRENDING_SOURCE = 'combined'  # 'google', 'bing', hoặc 'combined'
COMBINE_WITH_FILE = True  # True để kết hợp trending với keywords từ file
```

### Tính năng Trending Keywords (MỚI!)

Tool hiện hỗ trợ tự động lấy từ khóa trending từ Google Trends và Bing:

- **USE_TRENDING**: Bật/tắt tính năng trending
- **TRENDING_SOURCE**: Chọn nguồn trending
  - `'google'`: Chỉ lấy từ Google Trends
  - `'bing'`: Chỉ lấy từ Bing Trending
  - `'combined'`: Kết hợp cả hai nguồn (khuyến nghị)
- **COMBINE_WITH_FILE**: Kết hợp trending với keywords từ file `keywords.json`

**Ví dụ cấu hình:**

1. **Chỉ dùng trending keywords:**
```python
USE_TRENDING = True
TRENDING_SOURCE = 'combined'
COMBINE_WITH_FILE = False
```

2. **Kết hợp trending và keywords từ file:**
```python
USE_TRENDING = True
TRENDING_SOURCE = 'google'
COMBINE_WITH_FILE = True
```

3. **Chỉ dùng keywords từ file (như cũ):**
```python
USE_TRENDING = False
```

### Tùy chỉnh từ khóa tìm kiếm

Chỉnh sửa file `keywords.json` để thêm/bớt từ khóa:

```json
{
  "keywords": [
    "từ khóa 1",
    "từ khóa 2",
    "từ khóa 3"
  ]
}
```

## 🎯 Tính năng

- ✅ Tự động mở Edge và thực hiện tìm kiếm
- ✅ Sử dụng từ khóa ngẫu nhiên từ danh sách
- ✅ **TÍNH NĂNG MỚI:** Tự động lấy trending keywords từ Google Trends và Bing
- ✅ Hỗ trợ nhiều nguồn trending: Google, Bing, hoặc kết hợp
- ✅ Kết hợp trending keywords với keywords từ file
- ✅ Delay ngẫu nhiên giữa các lần tìm kiếm (tránh bị phát hiện)
- ✅ Tự động tải và cài đặt EdgeDriver
- ✅ Xử lý lỗi và báo cáo kết quả
- ✅ Hỗ trợ chế độ headless (chạy ẩn)

## ⚙️ Cấu trúc project

```
tools_automation_search/
├── edge_search_automation.py  # Script chính
├── check_edgedriver.py        # Script kiểm tra EdgeDriver
├── install_edgedriver.py      # Script cài đặt EdgeDriver
├── keywords.json              # File chứa từ khóa
├── requirements.txt            # Danh sách thư viện
└── README.md                  # Hướng dẫn sử dụng
```

## 🔧 Troubleshooting

### Kiểm tra cài đặt (Khuyến nghị đầu tiên!)

Trước khi chạy script chính, hãy kiểm tra môi trường:

```bash
python check_edgedriver.py
```

Script này sẽ kiểm tra:
- ✓ Microsoft Edge đã được cài đặt chưa
- ✓ EdgeDriver đã có chưa và ở đâu
- ✓ Phiên bản Edge và EdgeDriver có tương thích không
- ✓ Kết nối internet
- ✓ Selenium có hoạt động không

### Lỗi: "EdgeDriver not found" hoặc "Unable to obtain driver"

**Cách 1: Sử dụng script helper (Khuyến nghị)**
```bash
python install_edgedriver.py
```
Script này sẽ tự động:
- Phát hiện phiên bản Edge của bạn
- Tải EdgeDriver phù hợp
- Cài đặt vào thư mục hiện tại

**Cách 2: Tải thủ công**
1. Kiểm tra phiên bản Edge: Mở Edge → `edge://version`
2. Tải EdgeDriver từ: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
3. Chọn đúng phiên bản (phải khớp với Edge)
4. Giải nén và đặt `msedgedriver.exe` vào:
   - Cùng thư mục với script, HOẶC
   - Thư mục trong PATH (ví dụ: `C:\Windows\System32`)

**Cách 3: Sử dụng Selenium Manager (Selenium 4.6+)**
- Selenium 4.6+ có thể tự động tải driver
- Đảm bảo đã cài đặt Selenium mới nhất: `pip install --upgrade selenium`
- Tool sẽ tự động thử phương pháp này nếu webdriver-manager thất bại

### Lỗi: "Edge browser not installed"
- Cài đặt Microsoft Edge từ Microsoft Store hoặc trang chính thức

### Lỗi: "Element not found"
- Kiểm tra kết nối internet
- Đảm bảo Bing.com có thể truy cập được
- Có thể cần cập nhật selector nếu Bing thay đổi giao diện

### Lỗi khi lấy trending keywords
- Đảm bảo đã cài đặt `pytrends`: `pip install pytrends`
- Kiểm tra kết nối internet (cần để truy cập Google Trends/Bing)
- Nếu Google Trends bị rate limit, hãy đợi một chút rồi thử lại
- Có thể chuyển sang `TRENDING_SOURCE = 'bing'` nếu Google Trends gặp vấn đề

## 📝 Lưu ý kỹ thuật

- Tool sử dụng Selenium WebDriver để điều khiển browser
- Delay ngẫu nhiên giúp mô phỏng hành vi người dùng thật
- User agent được thiết lập để tránh bị phát hiện là bot
- Có thể cần điều chỉnh selector nếu Bing thay đổi HTML structure

## 🤝 Đóng góp

Nếu bạn muốn cải thiện tool này, hãy:
1. Fork project
2. Tạo branch mới cho feature
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

Project này chỉ dành cho mục đích giáo dục và nghiên cứu.

---

**Tác giả:** Developer với 5 năm kinh nghiệm Python
**Ngày tạo:** 2024

