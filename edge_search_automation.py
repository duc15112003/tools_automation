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
import requests
from bs4 import BeautifulSoup

# Import pytrends nếu có
try:
    from pytrends.request import TrendReq
    PTRENDS_AVAILABLE = True
except ImportError:
    PTRENDS_AVAILABLE = False
    print("Warning: pytrends chua duoc cai dat. Su dung: pip install pytrends")


class TrendingKeywords:
    """Class để lấy trending keywords từ nhiều nguồn: Google Trends, Bing, Reddit, Yahoo, DuckDuckGo"""
    
    def __init__(self):
        self.pytrends = None
        if PTRENDS_AVAILABLE:
            try:
                # Thử với retry và delay
                time.sleep(1)  # Delay ban đầu
                self.pytrends = TrendReq(hl='en-US', tz=360, retries=2, backoff_factor=0.1)
            except Exception as e:
                print(f"Warning: Khong the khoi tao pytrends: {e}")
    
    def get_google_trending(self, geo='US', num_keywords=20):
        """
        Lấy trending keywords từ Google Trends với retry logic
        
        Args:
            geo: Mã quốc gia (US, VN, v.v.)
            num_keywords: Số lượng từ khóa muốn lấy
            
        Returns:
            List các từ khóa trending
        """
        if not PTRENDS_AVAILABLE or not self.pytrends:
            return []
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = (attempt + 1) * 2  # Tăng delay mỗi lần retry
                    print(f"Thu lai lan {attempt + 1}/{max_retries} sau {delay} giay...")
                    time.sleep(delay)
                
                print("Dang lay trending keywords tu Google Trends...")
                
                # Thử lấy daily trending searches
                try:
                    trending_searches = self.pytrends.trending_searches(pn=geo)
                    
                    if trending_searches is not None and len(trending_searches) > 0:
                        keywords = trending_searches[0].head(num_keywords).tolist()
                        if keywords:
                            print(f"✓ Da lay duoc {len(keywords)} trending keywords tu Google Trends")
                            return keywords
                except:
                    pass
                
                # Fallback: Lấy related topics
                return self._get_related_keywords(num_keywords)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"✗ Loi khi lay Google Trends sau {max_retries} lan thu: {e}")
                    # Thử fallback method
                    return self._get_related_keywords(num_keywords)
                continue
        
        return []
    
    def _get_related_keywords(self, num_keywords=20):
        """Lấy related keywords từ Google Trends"""
        if not PTRENDS_AVAILABLE or not self.pytrends:
            return []
        
        try:
            # Sử dụng một số từ khóa phổ biến để lấy related
            base_keywords = ['technology', 'news', 'sports', 'entertainment', 'science']
            all_keywords = []
            
            for keyword in base_keywords[:2]:  # Chỉ lấy 2 từ khóa để tránh rate limit
                try:
                    self.pytrends.build_payload([keyword], cat=0, timeframe='today 1-m')
                    related = self.pytrends.related_queries()
                    if related and keyword in related:
                        if related[keyword]['top'] is not None:
                            top_queries = related[keyword]['top']['query'].head(5).tolist()
                            all_keywords.extend(top_queries)
                    time.sleep(2)  # Tăng delay để tránh rate limit
                except Exception as e:
                    continue
            
            return all_keywords[:num_keywords] if all_keywords else []
        except Exception as e:
            return []
    
    def get_bing_trending(self, num_keywords=20):
        """
        Lấy trending keywords từ Bing với nhiều phương pháp
        
        Args:
            num_keywords: Số lượng từ khóa muốn lấy
            
        Returns:
            List các từ khóa trending
        """
        try:
            print("Dang lay trending keywords tu Bing...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            keywords = []
            
            # Method 1: Bing News headlines
            try:
                url = "https://www.bing.com/news"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Thử nhiều selector khác nhau
                    selectors = [
                        ('h2', {'class': lambda x: x and 'title' in str(x).lower()}),
                        ('h3', {'class': lambda x: x and 'title' in str(x).lower()}),
                        ('a', {'class': lambda x: x and ('title' in str(x).lower() or 'headline' in str(x).lower())}),
                        ('div', {'class': lambda x: x and 'title' in str(x).lower()}),
                        ('span', {'class': lambda x: x and 'title' in str(x).lower()}),
                    ]
                    
                    for tag, attrs in selectors:
                        items = soup.find_all(tag, attrs)
                        for item in items[:num_keywords]:
                            text = item.get_text(strip=True)
                            if text and 5 < len(text) < 100 and text not in keywords:
                                keywords.append(text)
                                if len(keywords) >= num_keywords:
                                    break
                        if len(keywords) >= num_keywords:
                            break
            except Exception as e:
                pass
            
            # Method 2: Bing Search suggestions từ trending topics
            if len(keywords) < num_keywords:
                try:
                    # Lấy từ Bing homepage
                    url = "https://www.bing.com"
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Tìm các link trong trending section
                        trending_links = soup.find_all('a', href=lambda x: x and ('search' in x.lower() or 'trending' in x.lower()))
                        for link in trending_links[:10]:
                            text = link.get_text(strip=True)
                            if text and 3 < len(text) < 80 and text not in keywords:
                                keywords.append(text)
                except:
                    pass
            
            if keywords:
                print(f"✓ Da lay duoc {len(keywords)} trending keywords tu Bing")
                return keywords[:num_keywords]
            else:
                return []
        except Exception as e:
            print(f"✗ Loi khi lay Bing trending: {e}")
            return []
    
    def get_reddit_trending(self, num_keywords=20):
        """
        Lấy trending keywords từ Reddit
        
        Args:
            num_keywords: Số lượng từ khóa muốn lấy
            
        Returns:
            List các từ khóa trending
        """
        try:
            print("Dang lay trending keywords tu Reddit...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            keywords = []
            
            # Lấy từ r/popular và r/all
            subreddits = ['popular', 'all', 'news', 'worldnews', 'technology']
            
            for subreddit in subreddits[:3]:  # Chỉ lấy 3 subreddit
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'data' in data and 'children' in data['data']:
                            for post in data['data']['children']:
                                if 'data' in post:
                                    title = post['data'].get('title', '')
                                    if title and len(title) > 5 and len(title) < 100:
                                        # Lấy một số từ quan trọng từ title
                                        words = title.split()[:5]  # Lấy 5 từ đầu
                                        keyword = ' '.join(words)
                                        if keyword not in keywords:
                                            keywords.append(keyword)
                    time.sleep(1)  # Delay để tránh rate limit
                except:
                    continue
                
                if len(keywords) >= num_keywords:
                    break
            
            if keywords:
                print(f"✓ Da lay duoc {len(keywords)} trending keywords tu Reddit")
                return keywords[:num_keywords]
            return []
        except Exception as e:
            print(f"✗ Loi khi lay Reddit trending: {e}")
            return []
    
    def get_yahoo_trending(self, num_keywords=20):
        """
        Lấy trending keywords từ Yahoo News
        
        Args:
            num_keywords: Số lượng từ khóa muốn lấy
            
        Returns:
            List các từ khóa trending
        """
        try:
            print("Dang lay trending keywords tu Yahoo News...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = "https://news.yahoo.com"
            response = requests.get(url, headers=headers, timeout=10)
            keywords = []
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Tìm các headline
                selectors = [
                    ('h3', {}),
                    ('h2', {}),
                    ('a', {'class': lambda x: x and ('headline' in str(x).lower() or 'title' in str(x).lower())}),
                ]
                
                for tag, attrs in selectors:
                    items = soup.find_all(tag, attrs)
                    for item in items[:num_keywords]:
                        text = item.get_text(strip=True)
                        if text and 5 < len(text) < 100 and text not in keywords:
                            keywords.append(text)
                            if len(keywords) >= num_keywords:
                                break
                    if len(keywords) >= num_keywords:
                        break
            
            if keywords:
                print(f"✓ Da lay duoc {len(keywords)} trending keywords tu Yahoo News")
                return keywords[:num_keywords]
            return []
        except Exception as e:
            print(f"✗ Loi khi lay Yahoo trending: {e}")
            return []
    
    def get_duckduckgo_trending(self, num_keywords=20):
        """
        Lấy trending keywords từ DuckDuckGo (thông qua instant answers)
        
        Args:
            num_keywords: Số lượng từ khóa muốn lấy
            
        Returns:
            List các từ khóa trending
        """
        try:
            print("Dang lay trending keywords tu DuckDuckGo...")
            # DuckDuckGo không có trending API công khai, nhưng có thể lấy từ news
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Sử dụng một số từ khóa phổ biến để tạo suggestions
            base_keywords = ['news', 'technology', 'sports', 'science', 'world']
            keywords = []
            
            for base in base_keywords[:3]:
                try:
                    # Lấy instant answer từ DuckDuckGo
                    url = f"https://api.duckduckgo.com/?q={base}&format=json&no_html=1&skip_disambig=1"
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if 'RelatedTopics' in data:
                            for topic in data['RelatedTopics'][:3]:
                                if 'Text' in topic:
                                    text = topic['Text']
                                    # Lấy một số từ quan trọng
                                    words = text.split()[:4]
                                    keyword = ' '.join(words)
                                    if keyword not in keywords and len(keyword) > 5:
                                        keywords.append(keyword)
                    time.sleep(0.5)
                except:
                    continue
            
            if keywords:
                print(f"✓ Da lay duoc {len(keywords)} keywords tu DuckDuckGo")
                return keywords[:num_keywords]
            return []
        except Exception as e:
            return []
    
    def get_combined_trending(self, num_keywords=30):
        """
        Lấy trending keywords từ nhiều nguồn và kết hợp lại
        
        Args:
            num_keywords: Tổng số từ khóa muốn lấy
            
        Returns:
            List các từ khóa trending (đã loại bỏ trùng lặp)
        """
        all_keywords = []
        sources = []
        
        # Lấy từ các nguồn khác nhau
        # Google Trends (có thể fail)
        try:
            google_keywords = self.get_google_trending(num_keywords=num_keywords // 4)
            if google_keywords:
                all_keywords.extend(google_keywords)
                sources.append('Google')
        except:
            pass
        
        # Bing
        try:
            bing_keywords = self.get_bing_trending(num_keywords=num_keywords // 4)
            if bing_keywords:
                all_keywords.extend(bing_keywords)
                sources.append('Bing')
        except:
            pass
        
        # Reddit
        try:
            reddit_keywords = self.get_reddit_trending(num_keywords=num_keywords // 4)
            if reddit_keywords:
                all_keywords.extend(reddit_keywords)
                sources.append('Reddit')
        except:
            pass
        
        # Yahoo News
        try:
            yahoo_keywords = self.get_yahoo_trending(num_keywords=num_keywords // 4)
            if yahoo_keywords:
                all_keywords.extend(yahoo_keywords)
                sources.append('Yahoo')
        except:
            pass
        
        # DuckDuckGo (fallback)
        if len(all_keywords) < num_keywords // 2:
            try:
                ddg_keywords = self.get_duckduckgo_trending(num_keywords=10)
                if ddg_keywords:
                    all_keywords.extend(ddg_keywords)
                    sources.append('DuckDuckGo')
            except:
                pass
        
        # Loại bỏ trùng lặp và làm sạch
        unique_keywords = []
        seen = set()
        for kw in all_keywords:
            kw_lower = kw.lower().strip()
            # Làm sạch: loại bỏ các ký tự đặc biệt không cần thiết
            kw_clean = ''.join(c for c in kw_lower if c.isalnum() or c.isspace())
            kw_clean = ' '.join(kw_clean.split())  # Loại bỏ khoảng trắng thừa
            
            if kw_clean and kw_clean not in seen and 3 < len(kw_clean) < 100:
                seen.add(kw_clean)
                unique_keywords.append(kw.strip())
        
        if sources:
            print(f"✓ Tong hop tu {len(sources)} nguon: {', '.join(sources)}")
        
        return unique_keywords[:num_keywords]


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
        """Thiết lập Edge WebDriver với nhiều phương pháp fallback"""
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
        
        service = None
        driver_initialized = False
        
        # Method 1: Thử sử dụng webdriver-manager
        if not driver_initialized:
            try:
                print("Phuong phap 1: Dang tai EdgeDriver tu webdriver-manager...")
                driver_path = EdgeChromiumDriverManager().install()
                service = Service(driver_path)
                print("✓ Da tai EdgeDriver thanh cong")
                driver_initialized = True
            except Exception as e:
                print(f"✗ Phuong phap 1 that bai: {e}")
        
        # Method 2: Thử sử dụng Selenium Manager (tự động trong Selenium 4.6+)
        if not driver_initialized:
            try:
                print("Phuong phap 2: Thu su dung Selenium Manager...")
                service = Service()  # Selenium sẽ tự động tìm driver
                # Test thử khởi tạo
                test_driver = webdriver.Edge(service=service, options=edge_options)
                test_driver.quit()
                print("✓ Selenium Manager hoat dong")
                driver_initialized = True
            except Exception as e:
                print(f"✗ Phuong phap 2 that bai: {e}")
                service = None
        
        # Method 3: Thử tìm EdgeDriver trong các vị trí thông thường
        if not driver_initialized:
            try:
                print("Phuong phap 3: Tim EdgeDriver trong he thong...")
                possible_paths = [
                    os.path.join(os.environ.get('PROGRAMFILES', ''), 'Microsoft', 'Edge', 'Application', 'msedgedriver.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft', 'Edge', 'Application', 'msedgedriver.exe'),
                    os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'edgedriver', '*', 'msedgedriver.exe'),
                    'msedgedriver.exe',  # Trong PATH
                ]
                
                import glob
                for path_pattern in possible_paths:
                    if '*' in path_pattern:
                        matches = glob.glob(path_pattern)
                        if matches:
                            driver_path = matches[0]
                            if os.path.exists(driver_path):
                                service = Service(driver_path)
                                print(f"✓ Tim thay EdgeDriver tai: {driver_path}")
                                driver_initialized = True
                                break
                    else:
                        if os.path.exists(path_pattern):
                            service = Service(path_pattern)
                            print(f"✓ Tim thay EdgeDriver tai: {path_pattern}")
                            driver_initialized = True
                            break
                
                if not driver_initialized:
                    print("✗ Khong tim thay EdgeDriver trong he thong")
            except Exception as e:
                print(f"✗ Phuong phap 3 that bai: {e}")
        
        # Method 4: Thử không chỉ định service (Selenium sẽ tự tìm)
        if not driver_initialized:
            try:
                print("Phuong phap 4: Thu khoi tao khong chi dinh service...")
                service = None  # Để Selenium tự động tìm
                # Test thử
                test_driver = webdriver.Edge(options=edge_options)
                test_driver.quit()
                print("✓ Khoi tao thanh cong khong can service")
                driver_initialized = True
            except Exception as e:
                print(f"✗ Phuong phap 4 that bai: {e}")
        
        # Khởi tạo driver thực sự
        try:
            print("\nDang khoi tao Edge browser...")
            if service:
                self.driver = webdriver.Edge(service=service, options=edge_options)
            else:
                self.driver = webdriver.Edge(options=edge_options)
            
            self.driver.maximize_window()
            print("✓ Da khoi tao Edge WebDriver thanh cong!")
        except Exception as e:
            print(f"\n✗ Loi khi khoi tao WebDriver: {e}")
            print("\n" + "="*60)
            print("HUONG DAN KHAI PHUC:")
            print("="*60)
            print("1. Kiem tra Microsoft Edge da duoc cai dat:")
            print("   - Mo Edge va vao edge://version de xem phien ban")
            print("   - Neu chua co, cai dat tu: https://www.microsoft.com/edge")
            print()
            print("2. Tai EdgeDriver thu cong:")
            print("   - Vao: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            print("   - Tai dung phien ban EdgeDriver phu hop voi Edge cua ban")
            print("   - Giai nen va dat msedgedriver.exe vao:")
            print("     * Cung thu muc voi script nay")
            print("     * Hoac vao thu muc trong PATH (vi du: C:\\Windows\\System32)")
            print()
            print("3. Kiem tra ket noi internet:")
            print("   - Dang co the bi chan boi firewall hoac proxy")
            print("   - Thu tat firewall tam thoi hoac cau hinh proxy")
            print()
            print("4. Chay voi quyen Administrator:")
            print("   - Click chuot phai vao PowerShell/CMD")
            print("   - Chon 'Run as Administrator'")
            print("   - Chay lai script")
            print("="*60)
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
    
    def run_automation(self, num_searches=10, keywords_file='keywords.json', 
                      use_trending=False, trending_source='combined', 
                      combine_with_file=True):
        """
        Chạy automation với số lần tìm kiếm nhất định
        
        Args:
            num_searches: Số lần tìm kiếm muốn thực hiện
            keywords_file: File chứa danh sách từ khóa
            use_trending: Có sử dụng trending keywords không
            trending_source: Nguồn trending ('google', 'bing', 'reddit', 'yahoo', 'duckduckgo', 'combined', 'all')
            combine_with_file: Có kết hợp với keywords từ file không
        """
        keywords = []
        
        # Lấy keywords từ file nếu cần
        if combine_with_file or not use_trending:
            file_keywords = self.load_search_keywords(keywords_file)
            keywords.extend(file_keywords)
        
        # Lấy trending keywords nếu cần
        if use_trending:
            trending = TrendingKeywords()
            trending_keywords = []
            
            if trending_source == 'google':
                trending_keywords = trending.get_google_trending(num_keywords=30)
            elif trending_source == 'bing':
                trending_keywords = trending.get_bing_trending(num_keywords=30)
            elif trending_source == 'reddit':
                trending_keywords = trending.get_reddit_trending(num_keywords=30)
            elif trending_source == 'yahoo':
                trending_keywords = trending.get_yahoo_trending(num_keywords=30)
            elif trending_source == 'duckduckgo':
                trending_keywords = trending.get_duckduckgo_trending(num_keywords=30)
            elif trending_source == 'all':
                # Lấy từ tất cả nguồn
                all_trending = []
                try:
                    all_trending.extend(trending.get_google_trending(num_keywords=10))
                except: pass
                try:
                    all_trending.extend(trending.get_bing_trending(num_keywords=10))
                except: pass
                try:
                    all_trending.extend(trending.get_reddit_trending(num_keywords=10))
                except: pass
                try:
                    all_trending.extend(trending.get_yahoo_trending(num_keywords=10))
                except: pass
                # Loại bỏ trùng lặp
                seen = set()
                for kw in all_trending:
                    kw_lower = kw.lower().strip()
                    if kw_lower not in seen:
                        seen.add(kw_lower)
                        trending_keywords.append(kw)
            else:  # combined (mặc định - sử dụng get_combined_trending)
                trending_keywords = trending.get_combined_trending(num_keywords=30)
            
            keywords.extend(trending_keywords)
        
        # Loại bỏ trùng lặp
        unique_keywords = []
        seen = set()
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower and kw_lower not in seen and len(kw.strip()) > 2:
                seen.add(kw_lower)
                unique_keywords.append(kw.strip())
        
        keywords = unique_keywords
        
        if not keywords:
            print("✗ Khong co tu khoa de tim kiem!")
            return
        
        print(f"\n{'='*50}")
        print(f"Bat dau automation - So lan tim kiem: {num_searches}")
        print(f"Danh sach tu khoa: {len(keywords)} tu khoa")
        if use_trending:
            print(f"Nguon trending: {trending_source}")
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
    
    # Cấu hình Trending
    USE_TRENDING = True  # True để sử dụng trending keywords
    # Các nguồn: 'google', 'bing', 'reddit', 'yahoo', 'duckduckgo', 'combined', 'all'
    TRENDING_SOURCE = 'combined'  # 'combined' = tự động chọn nguồn tốt nhất, 'all' = lấy từ tất cả
    COMBINE_WITH_FILE = True  # True để kết hợp trending với keywords từ file
    
    automation = None
    
    try:
        # Khởi tạo automation
        automation = EdgeSearchAutomation(headless=HEADLESS, delay_range=DELAY_RANGE)
        
        # Chạy automation
        automation.run_automation(
            num_searches=NUM_SEARCHES, 
            keywords_file=KEYWORDS_FILE,
            use_trending=USE_TRENDING,
            trending_source=TRENDING_SOURCE,
            combine_with_file=COMBINE_WITH_FILE
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠ Người dùng đã dừng chương trình")
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
    finally:
        if automation:
            automation.close()


if __name__ == "__main__":
    main()

