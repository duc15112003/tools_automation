"""
Script kiểm tra EdgeDriver và Edge browser
Kiểm tra xem EdgeDriver đã được cài đặt đúng chưa
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def print_header(text):
    """In header với format đẹp"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_edge_installed():
    """Kiểm tra Edge đã được cài đặt chưa"""
    print_header("KIEM TRA MICROSOFT EDGE")
    
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    ]
    
    edge_found = False
    edge_version = None
    edge_path = None
    
    # Kiểm tra trong PATH
    try:
        result = subprocess.run(['where', 'msedge'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            edge_path = result.stdout.strip().split('\n')[0]
            edge_found = True
    except:
        pass
    
    # Kiểm tra các đường dẫn thông thường
    if not edge_found:
        for path in edge_paths:
            if os.path.exists(path):
                edge_path = path
                edge_found = True
                break
    
    if edge_found:
        print(f"✓ Microsoft Edge da duoc cai dat")
        print(f"  Duong dan: {edge_path}")
        
        # Lấy phiên bản Edge
        try:
            if sys.platform == 'win32':
                import winreg
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Edge\BLBeacon"
                    )
                    edge_version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                except:
                    try:
                        key = winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Edge\BLBeacon"
                        )
                        edge_version, _ = winreg.QueryValueEx(key, "version")
                        winreg.CloseKey(key)
                    except:
                        pass
        except:
            pass
        
        # Thử lấy từ command line
        if not edge_version:
            try:
                result = subprocess.run([edge_path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    edge_version = result.stdout.strip().split()[-1]
            except:
                pass
        
        if edge_version:
            print(f"  Phien ban: {edge_version}")
            major_version = edge_version.split('.')[0] if edge_version else None
            if major_version:
                print(f"  Major version: {major_version}")
                return True, edge_version, major_version, edge_path
        else:
            print("  ⚠ Khong the xac dinh phien ban Edge")
            return True, None, None, edge_path
    else:
        print("✗ Microsoft Edge CHUA duoc cai dat")
        print("\nHuong dan:")
        print("1. Cai dat tu: https://www.microsoft.com/edge")
        print("2. Hoac tu Microsoft Store")
        return False, None, None, None

def check_edgedriver_installed():
    """Kiểm tra EdgeDriver đã được cài đặt chưa"""
    print_header("KIEM TRA EDGEDRIVER")
    
    # Kiểm tra trong thư mục hiện tại
    current_dir_driver = os.path.join(os.getcwd(), 'msedgedriver.exe')
    if os.path.exists(current_dir_driver):
        print(f"✓ Tim thay EdgeDriver trong thu muc hien tai")
        print(f"  Duong dan: {os.path.abspath(current_dir_driver)}")
        return True, current_dir_driver
    
    # Kiểm tra trong PATH
    try:
        result = subprocess.run(['where', 'msedgedriver'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            driver_path = result.stdout.strip().split('\n')[0]
            if os.path.exists(driver_path):
                print(f"✓ Tim thay EdgeDriver trong PATH")
                print(f"  Duong dan: {driver_path}")
                return True, driver_path
    except:
        pass
    
    # Kiểm tra các vị trí khác
    possible_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Microsoft', 'Edge', 'Application', 'msedgedriver.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft', 'Edge', 'Application', 'msedgedriver.exe'),
        os.path.join(os.path.expanduser('~'), '.wdm', 'drivers', 'edgedriver'),
    ]
    
    import glob
    for path_pattern in possible_paths:
        if '*' not in path_pattern:
            if os.path.exists(path_pattern):
                print(f"✓ Tim thay EdgeDriver")
                print(f"  Duong dan: {path_pattern}")
                return True, path_pattern
        else:
            matches = glob.glob(os.path.join(path_pattern, '*', 'msedgedriver.exe'))
            if matches:
                driver_path = matches[0]
                print(f"✓ Tim thay EdgeDriver")
                print(f"  Duong dan: {driver_path}")
                return True, driver_path
    
    print("✗ KHONG tim thay EdgeDriver")
    return False, None

def get_edgedriver_version(driver_path):
    """Lấy phiên bản EdgeDriver"""
    if not driver_path or not os.path.exists(driver_path):
        return None
    
    try:
        result = subprocess.run([driver_path, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_output = result.stdout.strip()
            # EdgeDriver thường trả về: "MSEdgeDriver 120.0.0.0 (abc123...)"
            parts = version_output.split()
            if len(parts) >= 2:
                version = parts[1]
                return version
    except Exception as e:
        print(f"  ⚠ Khong the lay phien ban EdgeDriver: {e}")
    
    return None

def check_version_compatibility(edge_version, driver_version):
    """Kiểm tra phiên bản có tương thích không"""
    print_header("KIEM TRA TUONG THICH PHIEN BAN")
    
    if not edge_version:
        print("⚠ Khong the xac dinh phien ban Edge")
        return False
    
    if not driver_version:
        print("⚠ Khong the xac dinh phien ban EdgeDriver")
        return False
    
    edge_major = edge_version.split('.')[0]
    driver_major = driver_version.split('.')[0]
    
    print(f"Edge version:      {edge_version} (Major: {edge_major})")
    print(f"EdgeDriver version: {driver_version} (Major: {driver_major})")
    
    if edge_major == driver_major:
        print(f"\n✓ TUONG THICH! Ca hai cung major version {edge_major}")
        return True
    else:
        print(f"\n✗ KHONG TUONG THICH!")
        print(f"  Edge major version: {edge_major}")
        print(f"  EdgeDriver major version: {driver_major}")
        print(f"\n  Can tai EdgeDriver version {edge_major}.x.x.x")
        return False

def test_selenium_connection():
    """Kiểm tra xem Selenium có thể kết nối được không"""
    print_header("KIEM TRA KET NOI SELENIUM")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
        
        print("Dang thu khoi tao Edge WebDriver...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        # Thử khởi tạo
        try:
            driver = webdriver.Edge(options=options)
            driver.get("https://www.bing.com")
            title = driver.title
            driver.quit()
            print("✓ Selenium ket noi thanh cong!")
            print(f"  Test page title: {title}")
            return True
        except Exception as e:
            print(f"✗ Selenium ket noi that bai: {e}")
            return False
            
    except ImportError:
        print("✗ Selenium chua duoc cai dat")
        print("  Cai dat: pip install selenium")
        return False
    except Exception as e:
        print(f"✗ Loi: {e}")
        return False

def check_internet_connection():
    """Kiểm tra kết nối internet"""
    print_header("KIEM TRA KET NOI INTERNET")
    
    test_urls = [
        "https://www.google.com",
        "https://www.microsoft.com",
        "https://msedgedriver.azureedge.net",
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ Ket noi den {url} thanh cong")
                return True
        except Exception as e:
            print(f"✗ Khong ket noi duoc den {url}")
            continue
    
    print("\n⚠ Khong co ket noi internet hoac bi chan")
    print("  Ban can ket noi internet de tai EdgeDriver")
    return False

def main():
    """Hàm main"""
    print("="*60)
    print("  EDGEDRIVER CHECKER - Kiem tra cai dat EdgeDriver")
    print("="*60)
    
    # Kiểm tra Edge
    edge_ok, edge_version, edge_major, edge_path = check_edge_installed()
    
    if not edge_ok:
        print("\n⚠ CAN CAI DAT EDGE TRUOC!")
        return
    
    # Kiểm tra EdgeDriver
    driver_ok, driver_path = check_edgedriver_installed()
    
    if driver_ok:
        driver_version = get_edgedriver_version(driver_path)
        if driver_version:
            print(f"  Phien ban: {driver_version}")
        
        # Kiểm tra tương thích
        if edge_version and driver_version:
            compatible = check_version_compatibility(edge_version, driver_version)
            if not compatible:
                print("\n⚠ CAN TAI LAI EDGEDRIVER DUNG PHIEN BAN!")
    else:
        print("\n⚠ CAN TAI EDGEDRIVER!")
    
    # Kiểm tra internet
    internet_ok = check_internet_connection()
    
    # Kiểm tra Selenium
    selenium_ok = test_selenium_connection()
    
    # Tổng kết
    print_header("TONG KET")
    
    status_items = [
        ("Microsoft Edge", edge_ok),
        ("EdgeDriver", driver_ok),
        ("Ket noi Internet", internet_ok),
        ("Selenium Connection", selenium_ok),
    ]
    
    if edge_version and driver_path:
        driver_version = get_edgedriver_version(driver_path)
        if edge_version and driver_version:
            compatible = edge_version.split('.')[0] == driver_version.split('.')[0]
            status_items.append(("Version Compatibility", compatible))
    
    all_ok = True
    for name, status in status_items:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {name}: {'OK' if status else 'FAIL'}")
        if not status:
            all_ok = False
    
    print()
    if all_ok:
        print("✓ TAT CA DEU OK! Ban co the chay edge_search_automation.py")
    else:
        print("✗ CO VAN DE CAN KHAI PHUC")
        print("\nHUONG DAN:")
        
        if not driver_ok:
            print("1. Tai EdgeDriver:")
            if internet_ok:
                print("   → python install_edgedriver.py")
            else:
                print("   → Tai thu cong tu: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                if edge_major:
                    print(f"   → Chon phien ban {edge_major}.x.x.x")
                print("   → Dat msedgedriver.exe vao cung thu muc voi script")
        
        if not selenium_ok:
            print("2. Cai dat Selenium:")
            print("   → pip install selenium")
        
        if not internet_ok:
            print("3. Kiem tra ket noi internet:")
            print("   → Kiem tra firewall/proxy")
            print("   → Thu ket noi lai")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDa huy!")
    except Exception as e:
        print(f"\nLoi: {e}")
        import traceback
        traceback.print_exc()

