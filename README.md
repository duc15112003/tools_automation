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
pip install selenium webdriver-manager python-dotenv
```

### 3. Kiểm tra Edge browser

Đảm bảo Microsoft Edge đã được cài đặt và cập nhật lên phiên bản mới nhất.

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
- ✅ Delay ngẫu nhiên giữa các lần tìm kiếm (tránh bị phát hiện)
- ✅ Tự động tải và cài đặt EdgeDriver
- ✅ Xử lý lỗi và báo cáo kết quả
- ✅ Hỗ trợ chế độ headless (chạy ẩn)

## ⚙️ Cấu trúc project

```
tools_automation_search/
├── edge_search_automation.py  # Script chính
├── keywords.json              # File chứa từ khóa
├── requirements.txt           # Danh sách thư viện
└── README.md                  # Hướng dẫn sử dụng
```

## 🔧 Troubleshooting

### Lỗi: "EdgeDriver not found"
- Tool sẽ tự động tải EdgeDriver, nhưng nếu lỗi, hãy đảm bảo có kết nối internet
- Hoặc tải thủ công từ: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

### Lỗi: "Edge browser not installed"
- Cài đặt Microsoft Edge từ Microsoft Store hoặc trang chính thức

### Lỗi: "Element not found"
- Kiểm tra kết nối internet
- Đảm bảo Bing.com có thể truy cập được
- Có thể cần cập nhật selector nếu Bing thay đổi giao diện

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

