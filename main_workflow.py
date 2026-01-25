import os
import sys
import subprocess
import shutil
import glob
from datetime import datetime

# ================= Configuration =================
CRAWLER_DIR = "MediaCrawler-main"  # MediaCrawler 源码目录
DATA_RAW_DIR = os.path.join("data", "01_raw")  # 原始数据存放目录
KEYWORDS = ["山姆会员店", "山姆必买", "山姆吐槽", "山姆续卡"]
PLATFORM = "xhs"
CRAWLER_TYPE = "search"
SAVE_OPTION = "csv"
# =================================================

def check_environment():
    """检查必要的环境依赖"""
    print("Checking environment...")
    
    # Check if MediaCrawler exists
    if not os.path.exists(CRAWLER_DIR):
        print(f"Error: Directory '{CRAWLER_DIR}' not found.")
        return False
    
    # Check if playwright is installed
    try:
        import playwright
        print("Playwright is installed.")
    except ImportError:
        print("Error: Playwright is not installed. Please run: pip install playwright")
        return False

    return True

def run_crawler():
    """运行 MediaCrawler"""
    print(f"Starting crawler for keywords: {KEYWORDS}")
    
    keywords_str = ",".join(KEYWORDS)
    
    # 构建命令
    # 注意：我们不在此处传递 --cookies，而是让用户在 config/base_config.py 中配置，
    # 或者如果需要在命令行传递，可以取消下面相关代码的注释并修改
    cmd = [
        sys.executable,
        "main.py",
        "--platform", PLATFORM,
        "--type", CRAWLER_TYPE,
        "--keywords", keywords_str,
        "--save_data_option", SAVE_OPTION,
        # "--lt", "cookie", # 如果使用 Cookie 登录模式，取消注释
    ]
    
    print(f"Executing command: {' '.join(cmd)}")
    
    try:
        # 在 MediaCrawler 目录下运行，以确保相对路径引用正确
        result = subprocess.run(cmd, cwd=CRAWLER_DIR, check=True)
        print("Crawler finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Crawler failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
        
    return True

def move_data():
    """移动爬取的数据到 data/01_raw"""
    print("Moving data files...")
    
    # MediaCrawler 生成的 CSV 路径通常是 data/xhs/csv/
    source_dir = os.path.join(CRAWLER_DIR, "data", PLATFORM, "csv")
    
    if not os.path.exists(source_dir):
        print(f"Warning: Source directory '{source_dir}' does not exist. No data found?")
        return

    # 确保目标目录存在
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    # 查找所有 CSV 文件
    csv_files = glob.glob(os.path.join(source_dir, "*.csv"))
    
    if not csv_files:
        print("No CSV files found to move.")
        return
        
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(DATA_RAW_DIR, filename)
        
        # 如果目标文件存在，可以选择覆盖或重命名，这里选择覆盖
        try:
            shutil.move(file_path, dest_path)
            print(f"Moved: {filename} -> {DATA_RAW_DIR}")
        except Exception as e:
            print(f"Error moving {filename}: {e}")

    print("Data migration completed.")

def main():
    if not check_environment():
        return
    
    if run_crawler():
        move_data()

if __name__ == "__main__":
    main()
