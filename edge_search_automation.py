"""
Edge Search Automation Tool
Tự động hóa tìm kiếm trên Edge để tích điểm
"""

# -*- coding: utf-8 -*-
import sys
import io
import time
import random

# Cấu hình encoding UTF-8 cho Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json
import os


class EdgeSearchAutomation:
    def __init__(self, headless=False, delay_range=(2, 5)):
        """
        Khởi tạo automation tool
        
        Args:
            headless: Chạy ở chế độ ẩn (True) hoặc hiển thị browser (False)
            delay_range: Khoảng thời gian delay giữa các lần search (min, max) giây
        """
        self.headless = headless
        self.delay_range = delay_range
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Thiết lập Edge WebDriver"""
        edge_options = Options()
        
        if self.headless:
            edge_options.add_argument('--headless')
        
        # Các options để tối ưu hóa
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent để tránh bị phát hiện
        edge_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        
        # Tự động tải và cài đặt EdgeDriver
        try:
            print("Dang tai EdgeDriver...")
            driver_path = EdgeChromiumDriverManager().install()
            service = Service(driver_path)
            print("✓ Da tai EdgeDriver thanh cong")
        except Exception as e:
            print(f"✗ Loi khi tai EdgeDriver: {e}")
            print("Thu su dung EdgeDriver mac dinh...")
            # Thử sử dụng EdgeDriver mặc định nếu có
            service = Service()
        
        try:
            print("Dang khoi tao Edge browser...")
            self.driver = webdriver.Edge(service=service, options=edge_options)
            self.driver.maximize_window()
            print("✓ Da khoi tao Edge WebDriver thanh cong")
        except Exception as e:
            print(f"✗ Loi khi khoi tao WebDriver: {e}")
            print("\nKiem tra:")
            print("1. Microsoft Edge da duoc cai dat chua?")
            print("2. Ket noi internet co on khong?")
            print("3. Thu chay lai voi quyen Administrator")
            raise
    
    def load_search_keywords(self, keywords_file='keywords.json'):
        """
        Load danh sách từ khóa từ file JSON
        
        Args:
            keywords_file: Đường dẫn đến file chứa từ khóa
            
        Returns:
            List các từ khóa
        """
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('keywords', [])
        else:
            # Từ khóa mặc định nếu không có file
            return [
                "python programming",
                "web development",
                "machine learning",
                "artificial intelligence",
                "data science",
                "cloud computing",
                "cybersecurity",
                "blockchain technology",
                "internet of things",
                "software engineering"
            ]
    
    def perform_search(self, keyword):
        """
        Thực hiện một lần tìm kiếm
        
        Args:
            keyword: Từ khóa cần tìm kiếm
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Mở Bing (Edge thường dùng Bing làm search engine mặc định)
            self.driver.get("https://www.bing.com")
            time.sleep(random.uniform(1, 2))
            
            # Tìm ô tìm kiếm
            wait = WebDriverWait(self.driver, 10)
            search_box = wait.until(
                EC.presence_of_element_located((By.ID, "sb_form_q"))
            )
            
            # Xóa nội dung cũ và nhập từ khóa mới
            search_box.clear()
            time.sleep(random.uniform(0.5, 1))
            
            # Nhập từ khóa với tốc độ tự nhiên
            for char in keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1))
            
            # Nhấn Enter để tìm kiếm
            search_box.send_keys(Keys.RETURN)
            
            # Đợi trang kết quả load
            wait.until(EC.presence_of_element_located((By.ID, "b_results")))
            time.sleep(random.uniform(2, 4))
            
            print(f"✓ Đã tìm kiếm: '{keyword}'")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi khi tìm kiếm '{keyword}': {e}")
            return False
    
    def run_automation(self, num_searches=10, keywords_file='keywords.json'):
        """
        Chạy automation với số lần tìm kiếm nhất định
        
        Args:
            num_searches: Số lần tìm kiếm muốn thực hiện
            keywords_file: File chứa danh sách từ khóa
        """
        keywords = self.load_search_keywords(keywords_file)
        
        if not keywords:
            print("✗ Không có từ khóa để tìm kiếm!")
            return
        
        print(f"\n{'='*50}")
        print(f"Bắt đầu automation - Số lần tìm kiếm: {num_searches}")
        print(f"Danh sách từ khóa: {len(keywords)} từ khóa")
        print(f"{'='*50}\n")
        
        successful_searches = 0
        failed_searches = 0
        
        for i in range(num_searches):
            # Chọn từ khóa ngẫu nhiên
            keyword = random.choice(keywords)
            
            print(f"[{i+1}/{num_searches}] Đang tìm kiếm...")
            
            if self.perform_search(keyword):
                successful_searches += 1
            else:
                failed_searches += 1
            
            # Delay giữa các lần tìm kiếm
            if i < num_searches - 1:
                delay = random.uniform(self.delay_range[0], self.delay_range[1])
                print(f"⏳ Đợi {delay:.1f} giây trước lần tìm kiếm tiếp theo...\n")
                time.sleep(delay)
        
        print(f"\n{'='*50}")
        print(f"Hoàn thành!")
        print(f"Thành công: {successful_searches}/{num_searches}")
        print(f"Thất bại: {failed_searches}/{num_searches}")
        print(f"{'='*50}\n")
    
    def close(self):
        """Đóng browser và cleanup"""
        if self.driver:
            self.driver.quit()
            print("✓ Đã đóng browser")


def main():
    """Hàm main để chạy chương trình"""
    print("=" * 60)
    print("  Edge Search Automation Tool - Tu dong tich diem")
    print("=" * 60)
    
    # Cấu hình
    NUM_SEARCHES = 20  # Số lần tìm kiếm
    HEADLESS = False   # True để chạy ẩn, False để hiển thị browser
    DELAY_RANGE = (3, 6)  # Khoảng delay giữa các lần search (giây)
    KEYWORDS_FILE = 'keywords.json'
    
    automation = None
    
    try:
        # Khởi tạo automation
        automation = EdgeSearchAutomation(headless=HEADLESS, delay_range=DELAY_RANGE)
        
        # Chạy automation
        automation.run_automation(num_searches=NUM_SEARCHES, keywords_file=KEYWORDS_FILE)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Người dùng đã dừng chương trình")
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
    finally:
        if automation:
            automation.close()


if __name__ == "__main__":
    main()

