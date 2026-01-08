"""
Script helper để tải và cài đặt EdgeDriver thủ công
Sử dụng khi webdriver-manager không hoạt động
"""

import os
import sys
import requests
import zipfile
import subprocess
import json
from pathlib import Path

def get_edge_version():
    """Lấy phiên bản Edge đã cài đặt"""
    try:
        # Thử lấy từ registry (Windows)
        if sys.platform == 'win32':
            import winreg
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Edge\BLBeacon"
                )
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                return version
            except:
                # Thử đường dẫn khác
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SOFTWARE\Microsoft\Edge\BLBeacon"
                    )
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    return version
                except:
                    pass
        
        # Fallback: Thử chạy edge --version
        try:
            result = subprocess.run(['msedge', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version
        except:
            pass
        
        return None
    except Exception as e:
        print(f"Khong the lay phien ban Edge: {e}")
        return None

def get_major_version(version):
    """Lấy major version từ version string"""
    if version:
        try:
            return int(version.split('.')[0])
        except:
            pass
    return None

def download_edgedriver(version=None):
    """Tải EdgeDriver từ Microsoft"""
    print("="*60)
    print("Tai EdgeDriver thu cong")
    print("="*60)
    
    # Lấy phiên bản Edge
    if not version:
        print("\nDang kiem tra phien ban Edge...")
        edge_version = get_edge_version()
        if edge_version:
            print(f"✓ Tim thay Edge version: {edge_version}")
            major_version = get_major_version(edge_version)
        else:
            print("✗ Khong the xac dinh phien ban Edge")
            print("Vui long nhap phien ban Edge (vi du: 120): ", end="")
            try:
                major_version = int(input().strip())
            except:
                print("Phien ban khong hop le!")
                return False
    else:
        major_version = get_major_version(version)
    
    # URL để tải EdgeDriver
    base_url = "https://msedgedriver.azureedge.net"
    
    # Thử các phiên bản gần nhất
    versions_to_try = [major_version] if major_version else [120, 119, 118, 117]
    
    for ver in versions_to_try:
        try:
            # URL cho Windows 64-bit
            url = f"{base_url}/{ver}.0.0.0/edgedriver_win64.zip"
            print(f"\nDang thu tai phien ban {ver}...")
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=30, stream=True)
            
            if response.status_code == 200:
                print("✓ Tai thanh cong!")
                
                # Lưu file zip
                zip_path = "edgedriver.zip"
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Giải nén
                print("Dang giai nen...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('.')
                
                # Tìm file msedgedriver.exe
                driver_path = None
                for root, dirs, files in os.walk('.'):
                    if 'msedgedriver.exe' in files:
                        driver_path = os.path.join(root, 'msedgedriver.exe')
                        break
                
                if driver_path:
                    # Di chuyển đến thư mục hiện tại
                    final_path = os.path.join(os.getcwd(), 'msedgedriver.exe')
                    if driver_path != final_path:
                        import shutil
                        shutil.move(driver_path, final_path)
                    
                    # Xóa file zip và thư mục tạm
                    os.remove(zip_path)
                    if os.path.exists('edgedriver_win64'):
                        import shutil
                        shutil.rmtree('edgedriver_win64')
                    
                    print(f"\n✓ Da tai va cai dat EdgeDriver thanh cong!")
                    print(f"Duong dan: {os.path.abspath(final_path)}")
                    print("\nBan co the:")
                    print("1. Dat file msedgedriver.exe vao cung thu muc voi script")
                    print("2. Hoac them vao PATH de su dung toan he thong")
                    return True
                else:
                    print("✗ Khong tim thay msedgedriver.exe trong file zip")
            else:
                print(f"✗ Loi: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Loi khi tai phien ban {ver}: {e}")
            continue
    
    print("\n✗ Khong the tai EdgeDriver. Vui long tai thu cong:")
    print("https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
    return False

if __name__ == "__main__":
    try:
        download_edgedriver()
    except KeyboardInterrupt:
        print("\n\nDa huy!")
    except Exception as e:
        print(f"\nLoi: {e}")

