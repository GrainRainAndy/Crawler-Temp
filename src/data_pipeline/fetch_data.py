import os
import sys
import subprocess
import shutil
import glob
import time
import random
import json

# ================= CONFIG LOADING =================
CONFIG_FILE = "crawler_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[Error] 配置文件不存在: {CONFIG_FILE}")
        # 如果找不到可能是在 src 目录下运行，尝试向上查找
        alt_path = os.path.join("..", "..", CONFIG_FILE)
        if os.path.exists(alt_path):
             return json.load(open(alt_path, 'r', encoding='utf-8'))
        
        # 再次尝试，也许是在 src/data_pipeline 运行
        alt_path_2 = os.path.join("..", CONFIG_FILE)
        if os.path.exists(alt_path_2):
             return json.load(open(alt_path_2, 'r', encoding='utf-8'))
             
        print("请确认 crawler_config.json 是否已放置在项目根目录下。")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# 项目路径配置
CRAWLER_DIR = config.get("crawler_dir", "MediaCrawler-main")
# 兼容不同系统的路径分隔符
DATA_RAW_DIR = os.path.normpath(config.get("data_raw_dir", os.path.join("data", "01_raw")))

# 爬虫参数配置
PLATFORM = config.get("platform", "xhs")
CRAWLER_TYPE = config.get("crawler_type", "search")
SAVE_OPTION = config.get("save_option", "csv")

# 关键词列表
KEYWORDS = config.get("keywords", [])
# =================================================

def check_environment():
    """环境自检"""
    if not os.path.exists(CRAWLER_DIR):
        print(f"[Error] 未找到爬虫目录: {CRAWLER_DIR}")
        print("请确认 MediaCrawler 源码是否已放置在项目根目录下。")
        return False
    
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    return True

def move_and_rename_files(keyword):
    """
    将爬取产生的数据移动到 data/01_raw，并重命名以区分关键词
    """
    # MediaCrawler 默认输出目录: MediaCrawler-main/data/xhs/csv/
    source_dir = os.path.join(CRAWLER_DIR, "data", PLATFORM, "csv")
    
    if not os.path.exists(source_dir):
        return

    csv_files = glob.glob(os.path.join(source_dir, "*.csv"))
    
    if not csv_files:
        print(f"[{keyword}] 未检测到生成的 CSV 文件。")
        return

    moved_count = 0
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        
        # 构造新文件名：原文件名_关键词.csv
        # 例如: search_comments_2026-01-25.csv -> search_comments_2026-01-25_山姆必买.csv
        # 这样可以防止不同关键词的数据混在一起，也避免被覆盖 (因为 MediaCrawler 默认是追加写入)
        name_part, ext_part = os.path.splitext(filename)
        new_filename = f"{name_part}_{keyword}{ext_part}"
        dest_path = os.path.join(DATA_RAW_DIR, new_filename)
        
        try:
            # 移动文件
            shutil.move(file_path, dest_path)
            print(f"  [Move] {filename} -> {new_filename}")
            moved_count += 1
        except Exception as e:
            print(f"  [Error] 移动文件失败: {e}")
            
    if moved_count > 0:
        print(f"[{keyword}] 数据搬运完成，共 {moved_count} 个文件。")

def run_workflow():
    if not check_environment():
        return

    print(f"=== 开始执行爬虫任务，共 {len(KEYWORDS)} 个关键词 ===")
    print(f"目标平台: {PLATFORM} | 存储目录: {DATA_RAW_DIR}\n")

    for index, keyword in enumerate(KEYWORDS, 1):
        print(f">>> [{index}/{len(KEYWORDS)}] 正在爬取关键词: {keyword}")
        
        # 构造命令
        # 注意: 参数名称需与 MediaCrawler 的 arg.py 定义一致
        # MediaCrawler 使用 --save-data-option (而在 arg.py 内部定义为 save_data_option，cli 自动转换)
        # 之前报错也是因为下划线问题，这里的 subprocess 传参给 typer，通常用横杠
        cmd = [
            sys.executable,
            "main.py",
            "--platform", PLATFORM,
            "--lt", "qrcode",  # 默认使用扫码，如果配置了 cookie 请改为 cookie
            "--type", CRAWLER_TYPE,
            "--keywords", keyword,
            "--save_data_option", SAVE_OPTION 
        ]
        
        try:
            # 调用子进程
            # cwd=CRAWLER_DIR 确保能读取到 config.py 等内部文件
            subprocess.run(cmd, cwd=CRAWLER_DIR, check=True)
            
            # 爬取完成后立即搬运数据
            # 这样 MediaCrawler 目录被清空，下一个关键词的数据会写入新文件
            move_and_rename_files(keyword)
            
        except subprocess.CalledProcessError as e:
            print(f"[{keyword}] 爬虫运行异常 (Exit Code: {e.returncode})")
        except Exception as e:
            print(f"[{keyword}] 发生未知错误: {e}")

        # 反爬虫策略：随机休眠
        if index < len(KEYWORDS):
            sleep_time = random.uniform(5, 10)
            print(f"Waiting {sleep_time:.1f}s ...\n")
            time.sleep(sleep_time)

    print("\n=== 所有任务执行完毕 ===")

if __name__ == "__main__":
    run_workflow()
